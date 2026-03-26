<p align="center">
  <h1 align="center">MedPal — AI-Powered Medical Assistant</h1>
  <p align="center">
    An intelligent healthcare platform that combines machine learning disease prediction, generative AI chatbots, medical image analysis, and personalized lifestyle guidance — all in one place.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3-green?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/AI-Google%20Gemini-orange?logo=google&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/ML-scikit--learn-yellow?logo=scikit-learn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/Vector%20DB-Pinecone-purple?logo=pinecone&logoColor=white" alt="Pinecone">
  <img src="https://img.shields.io/badge/Deploy-Render-brightgreen?logo=render&logoColor=white" alt="Render">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Disease Prediction Models](#disease-prediction-models)
- [AI Modules](#ai-modules)
- [Deployment](#deployment)
- [Team](#team)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Overview

**MedPal** is a full-stack web application that leverages artificial intelligence and machine learning to provide users with accessible healthcare tools. The platform enables early disease risk assessment through ML models, offers an AI-powered medical chatbot for health queries, analyzes medical documents (X-Rays & PDFs), and provides personalized diet and lifestyle recommendations.

Built with **Flask** on the backend and powered by **Google Gemini** for generative AI capabilities, MedPal is designed to make advanced health technologies approachable for everyone.

> **Important:** MedPal is designed for **informational purposes only** and should not replace professional medical advice, diagnosis, or treatment.

---

## Features

### Disease Prediction
Predict the likelihood of multiple diseases using machine learning models trained on medical datasets:
- **Diabetes** — Based on biomarkers like HbA1c, BMI, Cholesterol, Triglycerides, etc.
- **Heart Disease** — Evaluates 20 risk factors including BP, cholesterol, smoking, stress, and CRP levels.
- **Kidney Disease** — Comprehensive analysis using 24 clinical parameters (blood, urine, vitals).
- **Lung Cancer** — Risk assessment based on symptoms and lifestyle factors.

### AI Medical Chatbot
- Conversational medical assistant powered by **Google Gemini 2.0 Flash** via **LangChain**.
- Maintains conversation history for contextual follow-ups.
- Draws knowledge from trusted sources (AIIMS, Medscape, WHO, Planned Parenthood).
- Returns referenced, bullet-formatted answers.

### X-Ray & Medical Document Analysis
- **Image Analysis** — Upload X-Rays or medical images (PNG, JPG, JPEG) for AI-powered analysis using Google Gemini's vision capabilities.
- **PDF Analysis** — Upload medical PDFs; the system extracts text (using pdfplumber → PyMuPDF → PyPDF2 fallback chain), chunks it, embeds it with HuggingFace sentence-transformers, stores vectors in **Pinecone**, and enables question-answering over the documents via a RAG pipeline.

### Lifestyle & Diet Advisor
- AI-generated personalized diet plans based on health queries.
- Provides detailed food recommendations with nutritional values and health benefits.
- Powered by **Gemini 2.5 Flash**.

### User Authentication
- Email/password-based registration and login.
- Session-based authentication with route protection via `@login_required` decorator.
- SQLite database for user management.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Flask 2.3, Gunicorn |
| **Frontend** | Jinja2 Templates, Bootstrap 5, HTML/CSS/JS |
| **Database** | SQLite |
| **ML Models** | scikit-learn 1.6, XGBoost 3.1 (serialized via Joblib) |
| **Generative AI** | Google Gemini 2.0 Flash / 2.5 Flash |
| **AI Framework** | LangChain, LangChain-Google-GenAI |
| **Embeddings** | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| **Vector Store** | Pinecone |
| **PDF Processing** | pdfplumber, PyMuPDF (fitz), PyPDF2 |
| **Image Processing** | Pillow, Google Generative AI Vision |
| **Deployment** | Render (Python 3.11.9) |

---

## Project Structure

```
medpal/
├── app.py                  # Main Flask application — routes, config, and controllers
├── wsgi.py                 # WSGI entry point for production (Gunicorn)
├── run_dev.py              # Development server launcher
├── run_production.py       # Production server launcher
├── lifestyle_chat.py       # Lifestyle & diet plan AI module
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment configuration
├── .flaskenv               # Flask environment variables
├── .gitignore              # Git ignore rules
│
├── ai_modules/             # AI processing modules
│   ├── __init__.py
│   ├── image_processor.py  # X-Ray / medical image analysis (Gemini Vision)
│   └── pdf_processor.py    # PDF extraction + RAG pipeline (Pinecone + Gemini)
│
├── bot/                    # Chatbot module
│   └── chatbot.py          # Conversational medical chatbot (Gemini + LangChain)
│
├── models/                 # Pre-trained ML models (Joblib serialized)
│   ├── Diabetes.joblib
│   ├── Heart Disease.joblib
│   ├── Kidney Disease.joblib
│   └── Lung Cancer.joblib
│
├── templates/              # Jinja2 HTML templates
│   ├── index.html          # Home / login page
│   ├── register.html       # Registration page
│   ├── predict.html        # Disease prediction form & results
│   ├── chatbot.html        # AI chatbot interface
│   ├── xray.html           # X-Ray & PDF upload / analysis
│   ├── lifestyle.html      # Lifestyle & diet advisor
│   ├── about.html          # About page with team info
│   └── partials/           # Reusable template components
│       ├── header.html     # Navigation bar
│       └── footer.html     # Footer
│
├── static/                 # Static assets
│   └── images/             # Team member photos and assets
│
├── Databases/              # SQLite database directory
│   └── users.db            # User accounts database
│
├── uploads/                # Uploaded files (gitignored, created at runtime)
└── vector_stores/          # Local vector store cache (gitignored, created at runtime)
```

---

## Prerequisites

- **Python** 3.11+ (recommended: 3.11.9)
- **pip** (Python package manager)
- **Google API Key** — for Gemini AI services ([Get one here](https://makersuite.google.com/app/apikey))
- **Pinecone API Key** — for PDF vector storage ([Sign up here](https://www.pinecone.io/))

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/medpal.git
cd medpal
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The `torch` and `sentence-transformers` packages are large (~2 GB). Ensure you have sufficient disk space and a stable internet connection.

---

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following keys:

```env
# Required — Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# Required — Pinecone (for PDF RAG pipeline)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=medpal-index

# Optional — Flask config (defaults are set in .flaskenv)
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
```

### Pinecone Index Setup

Before using the PDF analysis feature, create a Pinecone index:

1. Log in to the [Pinecone Console](https://app.pinecone.io/).
2. Create a new index named `medpal-index` (or your custom name).
3. Set the **dimension** to `384` (matching the `all-MiniLM-L6-v2` embedding model).
4. Choose the **cosine** similarity metric.

---

## Running the Application

### Development Mode

```bash
# Option 1: Using the dev runner (recommended — auto-reload disabled to prevent AI lib restarts)
python run_dev.py

# Option 2: Using Flask CLI
flask run

# Option 3: Run app.py directly
python app.py
```

The application will be available at **http://127.0.0.1:5000**.

### Production Mode

```bash
# Option 1: Using Gunicorn (recommended)
gunicorn wsgi:application --bind 0.0.0.0:5000

# Option 2: Using the production runner
python run_production.py
```

---

## API Endpoints

### Pages (GET)

| Route | Auth Required | Description |
|---|:---:|---|
| `/` | ❌ | Home page / Login |
| `/register` | ❌ | User registration page |
| `/predictions` | ✅ | Disease prediction model selection |
| `/chatbot` | ✅ | AI medical chatbot interface |
| `/xray` | ✅ | X-Ray & PDF analysis page |
| `/lifestyle` | ✅ | Lifestyle & diet advisor |
| `/about` | ❌ | About page |

### Authentication (POST)

| Route | Description |
|---|---|
| `POST /login` | Authenticate user with email & password |
| `POST /register` | Register a new user account |
| `POST /logout` | Log out and clear session |

### Disease Prediction (POST)

| Route | Description |
|---|---|
| `POST /predictions` | Select a disease model and get the input form |
| `POST /predict_result` | Submit parameters and receive prediction result |

### AI & File Processing (POST)

| Route | Content Type | Description |
|---|---|---|
| `POST /chat` | JSON | Send a message to the chatbot API (`{"message": "...", "session_id": "..."}`) |
| `POST /upload` | Multipart | Upload an image or PDF file (max 16 MB) |
| `POST /process` | JSON | Process uploaded files (`{"type": "image"}` or `{"type": "pdf"}`) |
| `POST /ask` | JSON | Ask a question about uploaded files (`{"question": "...", "type": "image/pdf"}`) |
| `POST /clear` | — | Clear all session data and uploaded files |

### Lifestyle (POST)

| Route | Content Type | Description |
|---|---|---|
| `POST /get-response` | JSON | Get diet/lifestyle recommendations (`{"query": "..."}`) |

---

## Disease Prediction Models

Each model is a pre-trained scikit-learn / XGBoost classifier serialized with Joblib.

### Diabetes
| Parameter | Type |
|---|---|
| Gender | Categorical (Male/Female) |
| Age, Urea, Cr, HbA1c, Cholesterol, TG, HDL, LDL, VLDL, BMI | Numerical |

### Heart Disease
| Parameter | Type |
|---|---|
| Gender, Exercise Habits, Smoking, Family History, Diabetes, High BP, Low HDL, High LDL, Alcohol, Stress, Sugar Consumption | Categorical |
| Age, Blood Pressure, Cholesterol, Sleep Hours, Triglyceride, Fasting Blood Sugar, CRP, Homocysteine | Numerical |

### Kidney Disease
| Parameter | Type |
|---|---|
| RBC, Pus Cell, Pus Cell Clumps, Bacteria, Hypertension, Diabetes Mellitus, CAD, Appetite, Pedal Edema, Anemia | Categorical |
| Age, BP, Specific Gravity, Albumin, Sugar, BGR, Blood Urea, Serum Creatinine, Sodium, Potassium, Hemoglobin, PCV, WBC, RBC Count | Numerical |

### Lung Cancer
| Parameter | Type |
|---|---|
| Gender, Smoking, Yellow Fingers, Anxiety, Peer Pressure, Chronic Disease, Fatigue, Allergy, Wheezing, Alcohol, Coughing, Shortness of Breath, Swallowing Difficulty, Chest Pain | Categorical |
| Age | Numerical |

---

## AI Modules

### Medical Chatbot (`bot/chatbot.py`)
- Uses **Google Gemini 2.0 Flash** via LangChain's `ConversationChain`.
- Maintains per-session conversation memory with `ConversationBufferMemory`.
- Thread-safe session management.
- System prompt steers the bot to give referenced, professional medical guidance.

### Image Processor (`ai_modules/image_processor.py`)
- Leverages **Google Gemini's multimodal capabilities** for medical image analysis.
- Supports PNG, JPG, and JPEG uploads.
- Can answer follow-up questions about uploaded images.

### PDF Processor (`ai_modules/pdf_processor.py`)
- **Text Extraction:** Three-method fallback chain (pdfplumber → PyMuPDF → PyPDF2).
- **Text Chunking:** `RecursiveCharacterTextSplitter` with 10,000 character chunks and 1,000 char overlap.
- **Embeddings:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- **Vector Storage:** Pinecone for persistent, scalable vector search.
- **QA Chain:** LangChain `load_qa_chain` with Gemini 2.0 Flash for context-aware answers.

### Lifestyle Advisor (`lifestyle_chat.py`)
- Uses **Gemini 2.5 Flash** with a specialized diet plan prompt.
- Provides food item recommendations with nutritional values and health benefits.

---

## Deployment

MedPal is configured for deployment on **[Render](https://render.com/)** using `render.yaml`:

```yaml
services:
  - type: web
    name: medpal
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn wsgi:application
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
```

### Steps to Deploy on Render

1. Push your code to a GitHub repository.
2. Connect your GitHub repo to [Render](https://dashboard.render.com/).
3. Render will auto-detect `render.yaml` and configure the service.
4. Add your environment variables (`GOOGLE_API_KEY`, `PINECONE_API_KEY`, etc.) in the Render dashboard under **Environment**.
5. Deploy — Render will install dependencies and start the Gunicorn server.

> **Note:** The SQLite database is ephemeral on Render's free tier. For persistent storage, consider migrating to PostgreSQL (Render provides a managed PostgreSQL addon).

---

## Team

| | Name | Role |
|---|---|---|
| | **Yarakaraju Aditya** | Generative AI & Intelligence Systems |
| | **Vishnudev Butla** | Machine Learning & Prediction Modeling |
| | **Srivasthav T** | ML, Backend Development & Web Architecture |

---

## Disclaimer

> **MedPal is designed for informational purposes only and should not replace professional medical advice, diagnosis, or treatment.** Always consult with qualified healthcare professionals for medical concerns. In case of emergency, seek immediate medical attention.
>
> Predictions and recommendations are based on AI models and should be used as supplementary information to support — not replace — professional medical judgment.

---

## License

This project is developed as an academic/research project. Please contact the development team for licensing inquiries.
