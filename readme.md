# AI Resume Analyzer

A production-style AI backend that analyzes resumes (text or PDF) and recommends the top 5 suitable job roles using structured LLM outputs.

Built using FastAPI and Google Gemini with schema-constrained responses to ensure reliability and consistency.

## Features

- Resume analysis (Text + PDF upload)
- LLM-powered job role recommendations
- Structured JSON output using schema validation
- Input & output validation to reduce hallucinations
- FastAPI backend with clean API design

## Tech Stack

- Python
- FastAPI
- Google Gemini API
- Pydantic
- PyPDF2

## API Endpoints

### 1. Analyze Resume (Text)
POST /analyze-resume

### 2. Analyze Resume (PDF)
POST /analyze-resume-pdf

## Sample Output:
```json
{
  "jobs": [
    {
      "role": "Data Engineer",
      "reason": [
        "Experience with Airflow and ETL pipelines",
        "Strong SQL and data processing skills"
      ],
      "score": 9
    }
  ]
}
```

## Run Locally

```bash
git clone <your-repo>
cd ai-job-matcher
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python -m uvicorn main:app --reload
```