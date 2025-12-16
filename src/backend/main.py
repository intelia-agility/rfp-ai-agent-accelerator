from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil
from services.rfp_analyzer import RFPAnalyzer
from services.question_generator import QuestionGenerator
from services.response_drafter import ResponseDrafter

app = FastAPI(title="RFP AI Agent Accelerator")

# Initialize services
analyzer = RFPAnalyzer()
drafter = ResponseDrafter()
q_gen = QuestionGenerator()

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
async def draft_response(file: UploadFile = File(...)):
    return {
        "message": "Draft created successfully",
        "output_path": "sharepoint/drafts/" + file.filename,
        "content_preview": drafter.draft_response("dummy text")
    }

@app.post("/questions")
async def generate_questions(file: UploadFile = File(...)):
    return {
        "questions": q_gen.generate_questions("dummy text")
    }
