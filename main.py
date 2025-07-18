import os
import io
import json

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from dotenv import load_dotenv
from docx import Document
from pypdf import PdfReader
import google.generativeai as genai

load_dotenv()

# Configure Gemini API key from environment variable
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_text_from_pdf(file: UploadFile) -> str:
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(io.BytesIO(file.file.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {e}")


def extract_text_from_docx(file: UploadFile) -> str:
    """Extracts text from a DOCX file."""
    try:
        document = Document(io.BytesIO(file.file.read()))
        text = ""
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing DOCX: {e}")


def extract_text_from_text_file(file: UploadFile) -> str:
    """Extracts text from a plain text file."""
    try:
        return file.file.read().decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing text file: {e}")


async def call_gemini_llm(prompt: str, model_name: str = "gemini-2.5-flash"):
    """
    Makes a service call to the Gemini LLM and returns the generated text.
    Assumes the LLM will return a JSON string.
    """
    try:
        model = genai.GenerativeModel(model_name)
        response = await model.generate_content_async(
            contents=[prompt],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            ),
        )
        # Return the JSON string to be parsed by FastAPI's JSONResponse
        return response.text
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error communicating with Gemini LLM: {e}"
        )


class AugmentRequest(BaseModel):
    bullet_point: str


@app.post("/augment")
async def augment_text(request: AugmentRequest):
    """
    Augments a given resume bullet point into three improved options.
    Expected LLM JSON format: {"options": ["option1", "option2", "option3"]}
    """
    prompt = (
        f"Using the bullet point provided, rewrite it as three augmented resume bullet point options that maximize impact across the following categories:\n\n"
        f"1. Action Verb: Starts with a strong, clear action verb relevant to the skill or task.\n"
        f"2. Quantifiable Impact: Includes specific numbers, percentages, or measurable outcomes.\n"
        f"3. Skill Relevance: Uses relevant keywords or skills.\n"
        f"4. Length and Clarity: Maintains a professional tone, keeps the bullet between 50–150 characters, and avoids unnecessary filler words.\n\n"
        f"Original Bullet Point:\n"
        f"{request.bullet_point}\n\n"
        f"Augment the given text by providing 3 options.\n\n"
        f"Expected LLM JSON format: {{\"options\": [\"option1\", \"option2\", \"option3\"]}}\n\n"
        f"Return only the JSON object, no extra commentary."
    )
    llm_response_str = await call_gemini_llm(prompt)
    return JSONResponse(content=json.loads(llm_response_str))


@app.post("/grader")
async def grade_document(file: UploadFile = File(...)):
    """
    Grades a document (PDF, DOCX, or text) and returns detailed feedback from the LLM.
    Expected LLM JSON format aligns with the new prompt requirements.
    """
    file_content = ""
    if file.filename.endswith(".pdf"):
        file_content = extract_text_from_pdf(file)
    elif file.filename.endswith(".docx"):
        file_content = extract_text_from_docx(file)
    elif file.filename.endswith(".txt"):
        file_content = extract_text_from_text_file(file)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF, DOCX, and TXT are supported.",
        )

    prompt = (
        f"You are an expert resume evaluator specializing in various roles at FAANG/MANGA-level companies.\n\n"
        f"Analyze the following resume content and produce a structured JSON assessment focusing on both ATS optimization and recruiter-readability. Use the following evaluation criteria inspired by Tech Interview Handbook:\n\n"
        f"1. ATS‑friendly formatting: Are sections (e.g., “Work Experience”, “Skills”) clear and in standard order? Is the font/plain text optimized for parsing?\n"
        f"2. Clarity & action‑oriented language: Do bullets start with strong action verbs? Is the phrasing clear and concise (avoid vague language)?\n"
        f"3. Quantifiable impact: Are measurable achievements present (e.g., “increased X by 20%”)?\n"
        f"4. Keyword relevance: Does the text include at least 5 role-specific keywords from the target job description?\n"
        f"5. Brevity & formatting: Is the resume one page? Are fonts standard and margins reasonable? Is it easy to scan?\n\n"
        f"Return only a JSON object with these keys:\n\n"
        f"- \"Keywords\": Array of ≥5 unique, high-impact technical keywords found.\n"
        f"- \"SectionFormatting\": \"ok\" or \"needs work\" based on section headings & order, with short reasoning.\n"
        f"- \"ClarityAction\": \"ok\" or \"needs work\" with brief note on action verbs/phrasing.\n"
        f"- \"QuantifiableImpact\": \"ok\" or \"needs work\" with note on presence or absence of measurable results.\n"
        f"- \"KeywordRelevance\": \"ok\" or \"needs work\" with reasoning.\n"
        f"- \"BrevityFormatting\": \"ok\" or \"needs work\" with note on page length, fonts, margins.\n"
        f"- \"Grade\": Letter (A–F) per handbook criteria.\n"
        f"- \"Score\": Integer 0–100 based on overall evaluation.\n"
        f"- \"Highlights\": 3–4 sentence summary of strongest aspects.\n"
        f"- \"Improvements\": 3–4 sentence summary of key areas to improve.\n\n"
        f"Resume Content: \n\"{file_content}\""
    )
    llm_response_str = await call_gemini_llm(prompt)
    return JSONResponse(content=json.loads(llm_response_str))


@app.post("/comparison")
async def compare_resume_to_job_application(
    resume_file: UploadFile = File(..., alias="file"),
    job_application_text: str = File(..., alias="job_application_text"),
):
    """
    Compares a resume (PDF, DOCX, or text) with a job application text,
    highlighting differences and providing a detailed comparison.
    Expected LLM JSON format aligns with the new prompt requirements.
    """
    resume_content = ""
    if resume_file.filename.endswith(".pdf"):
        resume_content = extract_text_from_pdf(resume_file)
    elif resume_file.filename.endswith(".docx"):
        resume_content = extract_text_from_docx(resume_file)
    elif resume_file.filename.endswith(".txt"):
        resume_content = extract_text_from_text_file(resume_file)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type for resume. Only PDF, DOCX, and TXT are supported.",
        )

    prompt = (
        f"You are a seasoned technical recruiter and resume coach specializing in various roles.\n\n"
        f"Carefully compare the provided **resume content** with the **job application description**, analyzing alignment in skills, experience, and language based on best practices from the Tech Interview Handbook.\n\n"
        f"Your output should be a JSON object with the following keys:\n\n"
        f"- \"Grade\": A letter grade (A, B, C, D, or F) assessing how well the resume matches the job application, factoring in relevance of skills, clarity, and demonstrated impact.\n"
        f"- \"Keyword difference\": An array of important keywords or key phrases that appear in the job application text but are missing or underemphasized in the resume, as well as resume keywords not reflected in the job description.\n"
        f"- \"Skill Gap Analysis\": A detailed explanation of specific technical skills, tools, or experiences requested by the job that are absent or insufficiently demonstrated in the resume.\n"
        f"- \"Impact & Clarity Gap\": Commentary on missing quantifiable achievements, action verbs, or clear descriptions in the resume relative to expectations set by the job application.\n"
        f"- \"Recommendations\": Practical advice on how to better tailor the resume to the job, focusing on adding relevant keywords, highlighting measurable impact, and improving clarity or formatting.\n\n"
        f"**Resume Content:** \n\"{resume_content}\"\n\n"
        f"**Job Application Text:** \n\"{job_application_text}\"\n\n"
        f"Return only the JSON object, correctly formatted, without any additional text or explanation outside the JSON."
    )
    llm_response_str = await call_gemini_llm(prompt)
    return JSONResponse(content=json.loads(llm_response_str))


if __name__ == "__main__":
    print("Starting FastAPI application...")
    print("Access the API documentation at: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)