from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# IMPORT THE INGEST FUNCTION
from agent import app as agent_app
from ingest import ingest  # <--- Make sure ingest.py is in the same folder!

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DebugRequest(BaseModel):
    error_message: str

@app.post("/debug")
async def debug_endpoint(request: DebugRequest):
    print(f"📩 API Received: {request.error_message}")
    try:
        result = agent_app.invoke({"query": request.error_message})
        return {
            "success": True,
            "fix": result["answer"],
            "iterations": result.get("iterations", 0)
        }
    except Exception as e:
        print(f"❌ API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW ENDPOINT: UPDATE MEMORY ---
@app.post("/ingest")
async def ingest_endpoint():
    print("🔄 API: Starting Ingestion...")
    try:
        # Runs the actual ingestion logic from ingest.py
        ingest() 
        return {"success": True, "message": "Database Updated Successfully"}
    except Exception as e:
        print(f"❌ Ingest Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))