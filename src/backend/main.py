from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
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

# Initialize services lazily to prevent startup failures
analyzer = None
drafter = None
q_gen = None
drive_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup with error handling"""
    global analyzer, drafter, q_gen, drive_client
    try:
        analyzer = RFPAnalyzer()
        drafter = ResponseDrafter()
        q_gen = QuestionGenerator()
        if DRIVE_AVAILABLE:
            drive_client = GoogleDriveClient()
        print("All services initialized successfully")
    except Exception as e:
        print(f"Warning: Some services failed to initialize: {e}")
        # Initialize with None to allow app to start
        if analyzer is None:
            analyzer = RFPAnalyzer()
        if drafter is None:
            drafter = ResponseDrafter()
        if q_gen is None:
            q_gen = QuestionGenerator()

@app.get("/")
def read_root():
    return {"message": "RFP AI Agent Accelerator API is running", "status": "healthy"}

@app.get("/health")
def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "rfp-backend"}

@app.get("/debug-drive")
def debug_drive():
    """Debug endpoint to check Google Drive status"""
    if drive_client:
        return drive_client.get_config_status()
    return {"status": "Drive client not initialized", "available": DRIVE_AVAILABLE}

def extract_text_from_file(file_path: str) -> str:
    """Extract text from .docx, .pdf or .txt files"""
    if file_path.endswith('.docx'):
        from docx import Document
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file_path.endswith('.pdf'):
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    else:
        # Assume text file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()

@app.post("/assess")
async def assess_rfp(file: UploadFile = File(...)):
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        rfp_content = extract_text_from_file(temp_path)
        
        if not rfp_content or len(rfp_content.strip()) < 10:
             # Fallback if extraction failed
             with open(temp_path, "rb") as f:
                 rfp_content = str(f.read()[:5000])

        result = analyzer.analyze_rfp(rfp_content)
        
        os.remove(temp_path)
        return result
    except Exception as e:
        print(f"Error in assess_rfp: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class DraftRequest(BaseModel):
    pass

def cleanup_files(paths: list):
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Error cleaning up file {path}: {e}")

@app.post("/draft")
async def draft_response(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    company_url: Optional[str] = Form(None)
):
    """
    Draft response using company knowledge base, fill placeholders, and return the document for download.
    """
    try:
        print(f"Received draft request for file: {file.filename}")
        
        if not file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="Input file must be a .docx document for drafting")

        # 1. Save input file
        input_path = f"temp_{file.filename}"
        output_filename = f"Draft_{file.filename}"
        output_path = f"temp_{output_filename}"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Extract real text from document
        rfp_content = extract_text_from_file(input_path)
        
        # 3. Generate Draft Content using real RFP context
        draft_text = drafter.draft_response(rfp_content, company_url=company_url)
        
        # 4. Modify Document (fill placeholders)
        final_doc_path = drafter.generate_draft_document(draft_text, input_path, output_path, company_url=company_url)
        
        if not final_doc_path:
            raise HTTPException(status_code=500, detail="Failed to generate draft document. Ensure file is a valid .docx")
        
        # 5. Upload to Google Drive and Return Link
        drive_response = None
        if drive_client and DRIVE_AVAILABLE:
            try:
                drive_response = drive_client.upload_file(final_doc_path, filename=output_filename)
                print(f"Uploaded to Drive: {drive_response}")
            except Exception as e:
                print(f"Failed to upload to drive: {e}")
        
        # Add cleanup to background tasks
        background_tasks.add_task(cleanup_files, [input_path, final_doc_path])
        
        if drive_response:
            return {
                "message": "Draft generated and uploaded to Google Drive successfully",
                "file_id": drive_response.get('id'),
                "drive_url": drive_response.get('url'),
                "filename": drive_response.get('name')
            }
        else:
            # Fallback if drive upload fails
            error_msg = getattr(drive_client, 'error_message', 'Drive upload failed or not configured')
            return {
                "message": f"Draft generated but Google Drive upload failed: {error_msg}",
                "drive_url": None,
                "filename": output_filename,
                "error": error_msg
            }

    except HTTPException as he:
        raise he
    except Exception as e:
        # Cleanup on error
        if 'input_path' in locals() and os.path.exists(input_path):
            os.remove(input_path)
        print(f"Error in draft_response: {e}")
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

