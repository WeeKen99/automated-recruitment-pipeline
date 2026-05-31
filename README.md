# automated-recruitment-pipeline
🤖 **AI-Powered CV Screening & Recruitment Automation**

## 📌 Project Overview
This automated pipeline streamlines the recruitment process by extracting, analysing, and scoring candidate CVs automatically. It reduces manual screening time by filtering high-volume applications and segregating them by vacancy.

**Goal:** Minimise manual data entry while ensuring high-quality candidates are prioritised for HR review.

## 🎥 Demo
[![Watch the demo](https://img.youtube.com/vi/RdZNA-xoj5s/maxresdefault.jpg)](https://youtu.be/RdZNA-xoj5s)

## 🛠️ The Workflow
Built on **n8n**, the workflow connects Gmail, Google Sheets, and Google Gemini AI to process applications in real time:

1. **Trigger (Gmail):** Detects incoming emails labelled `incoming-cvs`.
2. **Extractor:** Isolates the PDF attachment from the email.
3. **Analyzer (Google Gemini 1.5 Flash):** Reads the attached PDF directly, then:
   - Extracts key data (Name, Phone, Skills, Experience).
   - Calculates a **Fit Score (0–100)** against the specific job role.
   - Generates a short justification for the score.
4. **Staging Database (Google Sheets):** Logs structured candidate data for HR validation before entry into the core HRMS (BrioHR).

## 🚀 Key Features
- **Automatic Shortlisting:** Candidates are scored immediately upon application.
- **Structured Data Parsing:** Unstructured PDF text is converted into clean JSON.
- **Human-in-the-Loop:** Acts as a pre-processing layer so HR validates AI results before importing to BrioHR.

## 💻 Tech Stack
- **n8n:** Workflow orchestration and logic.
- **Google Gemini 1.5 Flash:** LLM for document reading, reasoning, and parsing.
- **Google Sheets:** Staging database and dashboard.

## ⚙️ Setup Requirements
Before importing, make sure you have:
- An n8n instance (self-hosted or n8n Cloud)
- A Google account (Gmail + Google Sheets access)
- A Google Gemini (AI Studio) API key

## 📂 How to Use
1. Import the workflow `.json` file from this repository into your n8n instance.
2. Connect your own Google and Gemini credentials.
3. Set up the Gmail filter: `resume OR CV` → label `incoming-cvs`.
4. Activate the workflow.

## ⚠️ Limitations & Responsible Use
- Fit scores are **decision support, not automated rejection** — a human reviews shortlisted and borderline candidates before any action is taken.
- The model parses only what the CV states; it does not infer or use protected attributes (age, gender, ethnicity, etc.).
- Parsing accuracy varies with CV formatting; unusual layouts may need manual review.
