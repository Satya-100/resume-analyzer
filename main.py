from fastapi import FastAPI, HTTPException, UploadFile, File
import google.genai as genai
from pydantic import BaseModel, Field
from typing import List
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

client = None
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    print("Connected to Gemini API successfully!")
except Exception as e:
    print(f"Error connecting to Gemini API: {e}")

if client is None:
    raise RuntimeError("Gemini client not initialized")

prompt = f"""
            Please choose the 5 most suitable job roles for the candidate based on the resume provided. 
            For each job role, provide a short reason for why it is suitable and 
            assign a score out of 10 indicating the suitability of the candidate for that role.
            reason must be a list of exactly 2 short bullet points. Return exactly 5 job roles.
            Ensure output strictly follows the provided JSON schema.
            Resume:
        """

class Job(BaseModel):
    role: str = Field(description="Name of the job.")
    reason: List[str] = Field(description="Reason for the job.")
    score:  int = Field(description="Score of the job.")

class JobList(BaseModel):
    jobs: List[Job] = Field(description="List of suitable job roles for the candidate.")

class ResumeRequest(BaseModel):
    resume_text: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

def analyze_resume_text(resume_text: str) ->JobList:
    if not resume_text or len(resume_text.strip()) < 30:
        raise HTTPException(
            status_code=400,
            detail="Resume text is too short or empty"
        )

    if len(resume_text) > 10000:
        raise HTTPException(
            status_code=400,
            detail="Resume text too large"
        )

    # if "experience" not in resume_text.lower() and "skills" not in resume_text.lower():
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Invalid resume format"
    #     )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt + "\n" + resume_text,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": JobList.model_json_schema(),
            },
        )

        if not response.text:
            raise HTTPException(status_code=500, detail="Empty response from Gemini")
    except Exception as e:
        print(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail="Error generating content from Gemini API")

    try:
        job_list = JobList.model_validate_json(response.text)
    except Exception as e:
        print("Raw response:", response.text)
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON response from Gemini API"
        )

    if len(job_list.jobs) != 5:
        raise HTTPException(
        status_code=400,
        detail="Gemini API did not return exactly 5 job roles"
    )
            
    for idx, job in enumerate(job_list.jobs):        
        if len(job.reason) != 2:
            raise HTTPException(
                status_code=400,
                detail=f"Job at index {idx} does not have exactly 2 reasons"
            )
        
        if not (1 <= job.score <= 10):
            raise HTTPException(
                status_code=400,
                detail=f"Job at index {idx} has invalid score: {job.score}"
            )
    
    return job_list


@app.post("/analyze-resume", response_model=JobList)
def analyze_resume(request: ResumeRequest):
    resume_text = request.resume_text
    return analyze_resume_text(resume_text)

def extract_text_from_pdf(file: UploadFile) -> str:
    try: 
        reader = PdfReader(file.file)

        text = ""

        for pages in reader.pages:
            text += pages.extract_text()
        
        text = text.strip()

        if not text:
            raise HTTPException(400, detail="No text found in PDF file")
        
        return text.strip()
    except Exception as e:
        raise HTTPException(400, detail="Error reading PDF file")


@app.post("/analyze-resume-pdf", response_model=JobList)
def analyze_resume_pdf(file: UploadFile):
    if(file.content_type != "application/pdf"):
        raise HTTPException(400, detail="Invalid file type. Please upload a PDF file.")
    
    resume_text = extract_text_from_pdf(file)
    return analyze_resume_text(resume_text)
