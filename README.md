# RFP AI Agent Accelerator

A comprehensive tool for Sales Teams to automate the RFP process using AI.

## Features

### 1. RFP Assessment & Scoring
- Upload RFP documents (PDF, Word).
- AI analyzes the document against key criteria:
    - Business strategy and alignment.
    - Core offerings fit.
    - Resource availability.
    - Risk and compliance.
- Provides a quantifiable score (0-100) and a "Pursue/No-Pursue" recommendation.

### 2. Intelligent Response Drafting
- Drafts responses using internal knowledge base (SharePoint, historical RFPs).
- Ensures consistent tone and branding.
- customization for value propositions.
- **Output:** Writes drafted content back to SharePoint in the original format.

### 3. Automated Question Generation
- Generates a prioritized list of clarification questions for the client.
- Covers scope, success criteria, budget, timeline, and technical constraints.
- Saves the questions list to SharePoint.

## Architecture

- **Frontend:** Next.js (React) - *Under Construction*
- **Backend:** Python (FastAPI)
- **AI Engine:** Google Vertex AI (Gemini)
- **Integration:** SharePoint Online, Google Cloud Storage

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+ (for frontend)
- Google Cloud Project with Vertex AI API enabled.
- SharePoint credentials.

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd src/backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in `src/backend`:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
   SHAREPOINT_URL="https://yourcompany.sharepoint.com"
   SHAREPOINT_CLIENT_ID="your_client_id"
   SHAREPOINT_CLIENT_SECRET="your_client_secret"
   ```

4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`.
   Docs: `http://localhost:8000/docs`

### Frontend Setup (Once generation completes)

1. Navigate to frontend:
   ```bash
   cd src/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000`.

## API Usage

- **POST /assess**: Upload a file to get a score.
- **POST /draft**: Upload a file to generate a draft.
- **POST /questions**: Upload a file to generate questions.
