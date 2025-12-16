from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from services.rfp_analyzer import RFPAnalyzer
from services.question_generator import QuestionGenerator
from services.response_drafter import ResponseDrafter

try:
    from services.google_drive_client import GoogleDriveClient
    DRIVE_AVAILABLE = True
except Exception as e:
    print(f"Google Drive client not available: {e}")
    DRIVE_AVAILABLE = False
    GoogleDriveClient = None

app = FastAPI(title="RFP AI Agent Accelerator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = RFPAnalyzer()
drafter = ResponseDrafter()
q_gen = QuestionGenerator()
drive_client = GoogleDriveClient() if DRIVE_AVAILABLE else None

@app.get("/")
def read_root():
    return {"message": "RFP AI Agent Accelerator API is running"}

@app.post("/assess")
async def assess_rfp(file: UploadFile = File(...)):
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        with open(temp_path, "rb") as f:
            content = str(f.read()) 
            
        result = analyzer.analyze_rfp(content)
        
        os.remove(temp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DraftRequest(BaseModel):
    pass

@app.post("/draft")
async def draft_response(
    file: UploadFile = File(...), 
    company_url: Optional[str] = Form(None)
):
    """
    Draft response using company knowledge base, fill placeholders, and upload to Google Drive.
    """
    try:
        # 1. Save input file
        input_path = f"temp_{file.filename}"
        output_filename = f"Draft_{file.filename}"
        output_path = f"temp_{output_filename}"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Extract text (mock for now, assume we read it)
        # In reality, we'd use python-docx to read the text
        rfp_content_preview = "Sample RFP content..."
        
        # 3. Generate Draft Content
        draft_text = drafter.draft_response(rfp_content_preview, company_url=company_url)
        
        # 4. Modify Document (fill placeholders)
        final_doc_path = drafter.generate_draft_document(draft_text, input_path, output_path, company_url=company_url)
        
        # 5. Upload to Google Drive
        drive_file_id = None
        if drive_client and final_doc_path and os.path.exists(final_doc_path):
            drive_file_id = drive_client.upload_file(final_doc_path, output_filename)
        
        # Cleanup input
        if os.path.exists(input_path):
            os.remove(input_path)

        if final_doc_path and os.path.exists(final_doc_path):
            # Return file with info about Drive upload
            response = FileResponse(
                final_doc_path, 
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                filename=output_filename
            )
            if drive_file_id:
                response.headers["X-Drive-File-ID"] = drive_file_id
                response.headers["X-Drive-Upload-Status"] = "success"
            return response
        else:
            raise HTTPException(status_code=500, detail="Failed to generate document")

    except Exception as e:
        # Cleanup on error
        if 'input_path' in locals() and os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/questions")
async def generate_questions(
    file: UploadFile = File(...),
    company_url: Optional[str] = Form(None)
):
    """
    Generate questions using company capabilities context.
    """
    try:
        rfp_content_preview = "Sample RFP content extracted from file..."
        questions = q_gen.generate_questions(rfp_content_preview, company_url=company_url)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

