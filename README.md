# automated-recruitment-pipeline

# 🤖 AI-Powered CV Screening & Recruitment Automation

## 📌 Project Overview
This automated pipeline streamlines the recruitment process by extracting, analyzing, and scoring candidate CVs automatically. It reduces manual screening time by filtering high-volume applications and segregating them by vacancy.

**Goal:** Minimise manual data entry while ensuring high-quality candidates are prioritized for HR review.

## 🛠️ The Workflow
The solution connects **Gmail**, **PDF.co**, and **Google Gemini AI** to process applications in real-time:

1.  **Watcher (Gmail):** Detects incoming emails labeled `incoming-cvs`.
2.  **Extractor (Iterator):** Isolates PDF attachments from the email body.
3.  **Digitizer (PDF.co):** Converts raw PDF files into machine-readable text (OCR).
4.  **Analyzer (Google Gemini 1.5):**
    * Extracts key data (Name, Phone, Skills, Experience).
    * Calculates a **"Fit Score" (0-100)** based on the specific Job Role.
    * Generates a summary reason for the score.
5.  **Staging Database (Google Sheets):** Logs structured candidate data for HR validation before entry into the core HRMS (BrioHR).

## 🚀 Key Features
* **Automatic Shortlisting:** Candidates are scored immediately upon application.
* **Structured Data Parsing:** Unstructured PDF text is converted into clean JSON.
* **Human-in-the-Loop:** Designed as a pre-processing layer to validate AI results before importing to BrioHR.

## 💻 Tech Stack
* **Make.com (Integromat):** Orchestration and Logic.
* **Google Gemini AI:** LLM for reasoning and parsing.
* **PDF.co:** Text Extraction.
* **Google Sheets:** Dashboard & Staging.

## 📂 How to Use
1.  Download the `Integration Gmail.blueprint.json` file from this repository.
2.  Import it into a new Make.com scenario.
3.  Connect your own Google and PDF.co accounts.
4.  Set up the Gmail filter: `resume OR CV` -> Label: `incoming-cvs`.
