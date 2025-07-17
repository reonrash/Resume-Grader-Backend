# 📄 Resume Grader Backend

Welcome to the Resume Grader Backend! This project provides a robust and intelligent backend service for resume grading and augmentation, powered by Google's Gemini Large Language Model. Whether you're a job seeker looking to optimize your resume or a developer interested in AI-driven applications, this backend serves as an excellent foundation for resume optimization tools.

## ✨ What Can This Backend Do?

Our backend offers three powerful API endpoints designed to help you create the perfect resume:

### 🔧 `/augment` (POST)

**Transform your bullet points into compelling statements**

This endpoint takes your existing resume bullet points and rewrites them into three enhanced versions that pack more punch. The AI focuses on:

- Strong action verbs that grab attention
- Quantifiable achievements that demonstrate impact
- Skill relevance that aligns with industry standards
- Clear, concise language that recruiters love

**Input:** Your original bullet point as JSON
**Output:** Three professionally enhanced alternatives

### 📊 `/grader` (POST)

**Get a comprehensive resume assessment**

Think of this as having an expert resume evaluator review your entire resume. The AI analyzes your resume across multiple dimensions:

- **ATS-friendly formatting** - Will it pass through applicant tracking systems?
- **Clarity and impact** - Are your achievements clearly communicated?
- **Quantifiable results** - Do you show measurable outcomes?
- **Keyword optimization** - Are you using industry-relevant terms?
- **Professional brevity** - Is your content concise yet comprehensive?

**Input:** Upload your resume (PDF, DOCX, or TXT)
**Output:** Detailed assessment with grade, score, highlights, and improvement suggestions

### 🎯 `/comparison` (POST)

**Tailor your resume to specific job applications**

This endpoint acts like a seasoned technical recruiter, comparing your resume against a specific job description to identify gaps and opportunities.

**Input:** Your resume file + job description text
**Output:** Alignment analysis with keyword gaps, skill recommendations, and tailoring suggestions

## 🚀 Technology Stack

We've chosen modern, reliable technologies to ensure great performance and developer experience:

- **FastAPI** - Lightning-fast Python web framework with automatic API documentation
- **Uvicorn** - High-performance ASGI server
- **Google Generative AI** - Powered by Gemini LLM for intelligent text processing
- **PyPDF & Python-DOCX** - Seamless document parsing
- **Python-Dotenv** - Clean environment variable management

## ⚙️ Getting Started

### Prerequisites

Before diving in, make sure you have:

- Python 3.9 or higher
- Docker (recommended for deployment)
- A Google Gemini API Key ([get yours here](https://ai.google.dev/))

### 1. Environment Setup

First, let's get your environment ready:

1. **Clone or create your project directory** with the necessary files
2. **Create a `.env` file** in your project root:
   ```env
   GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
   ```
   Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key from Google AI Studio.

### 2. Running Locally (Development Mode)

Perfect for development and testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The `--reload` flag enables hot-reloading, so your changes are reflected instantly! 🔄

**Access your API:**

- **API endpoints:** http://127.0.0.1:8000
- **Interactive documentation:** http://127.0.0.1:8000/docs (FastAPI's automatic docs - pretty cool!)

### 3. Running with Docker (Recommended for Production)

Docker makes deployment a breeze:

```bash
# Build your Docker image
docker build -t resume-grader-backend .

# Run the container
docker run -d -p 8000:8000 --env-file ./.env resume-grader-backend
```

**What's happening here:**

- `-d` runs the container in the background
- `-p 8000:8000` maps your local port 8000 to the container's port 8000
- `--env-file ./.env` securely loads your API key into the container

Your API is now live at http://localhost:8000! 🎉

## 🧪 Testing Your API

Let's test each endpoint using Postman or any HTTP client:

### Testing `/augment`

```
POST http://localhost:8000/augment
Content-Type: application/json

{
  "bullet_point": "Managed team tasks and reported progress."
}
```

### Testing `/grader`

```
POST http://localhost:8000/grader
Content-Type: multipart/form-data

Key: file (File type)
Value: Upload your resume (.pdf, .docx, or .txt)
```

### Testing `/comparison`

```
POST http://localhost:8000/comparison
Content-Type: multipart/form-data

Key 1: file (File type) - Upload your resume
Key 2: job_application_text (Text type) - Paste the job description
```

## 🛑 Shutting Down

When you're done working, here's how to cleanly stop your Docker container:

```bash
# Find your running container
docker ps

# Stop the container
docker stop resume-grader-backend

# Remove the container
docker rm resume-grader-backend

# Or do both in one command (use with caution)
docker rm -f resume-grader-backend
```

## 🎯 What Makes This Special?

This backend demonstrates several advanced concepts:

- **AI Integration** - Shows how to effectively integrate LLMs into web services
- **Prompt Engineering** - Carefully crafted prompts for optimal AI responses
- **Type Safety** - FastAPI's automatic validation using Pydantic models
- **Document Processing** - Handles multiple file formats seamlessly
- **Production Ready** - Docker containerization for easy deployment

## 🤝 Ready to Get Started?

This backend is designed to be both educational and practical. Whether you're learning about AI integration or building a production resume service, you'll find the code well-structured and thoroughly documented.

Happy coding, and may your resumes always stand out! 🌟
