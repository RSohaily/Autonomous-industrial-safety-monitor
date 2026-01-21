from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import base64
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

logger = logging.getLogger(__name__)

# Define Models
class DetectedItem(BaseModel):
    category: str  # "component" or "hazard"
    name: str
    description: str
    confidence: str
    priority: str  # "high", "medium", "low"
    action: str
    location: Optional[str] = None

class Analysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    image_name: str
    detected_items: List[DetectedItem]
    overall_safety_score: str
    summary: str

class AnalysisCreate(BaseModel):
    image_base64: str
    image_name: str

class AnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    timestamp: str
    image_name: str
    detected_items: List[DetectedItem]
    overall_safety_score: str
    summary: str

# Vision Analysis Function
async def analyze_warehouse_image(image_base64: str) -> dict:
    """
    Analyze warehouse image using OpenAI GPT-5.2 with vision
    Returns structured analysis with components and hazards
    """
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY', '')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        # Create chat instance
        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message="""You are an expert industrial safety and logistics AI system.
            Analyze warehouse and workshop images to identify:
            1. Industrial components (bolts, screws, tools, parts) with specifications
            2. Safety hazards (spills, obstacles, unsafe conditions)
            
            For each detected item, provide:
            - Category: "component" or "hazard"
            - Name: Specific identification (e.g., "M8 Hex Bolt", "Oil Spill")
            - Description: Detailed observation
            - Confidence: "high", "medium", or "low"
            - Priority: "high" (immediate action), "medium" (monitor), "low" (routine)
            - Action: Specific recommended action
            - Location: If visible, describe location in image
            
            Also provide an overall safety score (Safe/Caution/Danger) and summary.
            
            Return response in this EXACT JSON format:
            {
              "detected_items": [
                {
                  "category": "component" or "hazard",
                  "name": "Item name",
                  "description": "Description",
                  "confidence": "high/medium/low",
                  "priority": "high/medium/low",
                  "action": "Recommended action",
                  "location": "Location in image"
                }
              ],
              "overall_safety_score": "Safe/Caution/Danger",
              "summary": "Overall analysis summary"
            }"""
        ).with_model("openai", "gpt-5.2")
        
        # Create image content
        image_content = ImageContent(image_base64=image_base64)
        
        # Create message
        user_message = UserMessage(
            text="Analyze this warehouse/workshop image. Identify all industrial components and safety hazards. Return structured JSON as specified.",
            file_contents=[image_content]
        )
        
        # Send message and get response
        response = await chat.send_message(user_message)
        logger.info(f"Vision API response: {response}")
        
        # Parse JSON response
        import json
        # Extract JSON from response
        response_text = response.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        return result
        
    except Exception as e:
        logger.error(f"Error in vision analysis: {str(e)}")
        # Return fallback analysis
        return {
            "detected_items": [
                {
                    "category": "component",
                    "name": "Analysis Error",
                    "description": f"Could not complete analysis: {str(e)}",
                    "confidence": "low",
                    "priority": "medium",
                    "action": "Retry analysis or check system logs",
                    "location": "N/A"
                }
            ],
            "overall_safety_score": "Unknown",
            "summary": "Analysis could not be completed due to technical error."
        }

# Routes
@api_router.get("/")
async def root():
    return {"message": "Warehouse Vision AI API", "status": "operational"}

@api_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(input: AnalysisCreate):
    """
    Analyze an uploaded warehouse image
    """
    try:
        # Perform vision analysis
        analysis_result = await analyze_warehouse_image(input.image_base64)
        
        # Create analysis object
        detected_items = [
            DetectedItem(**item) for item in analysis_result.get("detected_items", [])
        ]
        
        analysis = Analysis(
            image_name=input.image_name,
            detected_items=detected_items,
            overall_safety_score=analysis_result.get("overall_safety_score", "Unknown"),
            summary=analysis_result.get("summary", "Analysis completed.")
        )
        
        # Save to database
        doc = analysis.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.analyses.insert_one(doc)
        
        # Return response
        return AnalysisResponse(
            id=analysis.id,
            timestamp=analysis.timestamp.isoformat(),
            image_name=analysis.image_name,
            detected_items=analysis.detected_items,
            overall_safety_score=analysis.overall_safety_score,
            summary=analysis.summary
        )
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/history", response_model=List[AnalysisResponse])
async def get_analysis_history():
    """
    Get analysis history (last 50 analyses)
    """
    try:
        analyses = await db.analyses.find({}, {"_id": 0}).sort("timestamp", -1).limit(50).to_list(50)
        
        return [
            AnalysisResponse(
                id=a["id"],
                timestamp=a["timestamp"],
                image_name=a["image_name"],
                detected_items=a["detected_items"],
                overall_safety_score=a["overall_safety_score"],
                summary=a["summary"]
            )
            for a in analyses
        ]
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return []

@api_router.get("/stats")
async def get_stats():
    """
    Get analysis statistics
    """
    try:
        total_analyses = await db.analyses.count_documents({})
        
        # Count by safety score
        safe_count = await db.analyses.count_documents({"overall_safety_score": "Safe"})
        caution_count = await db.analyses.count_documents({"overall_safety_score": "Caution"})
        danger_count = await db.analyses.count_documents({"overall_safety_score": "Danger"})
        
        return {
            "total_analyses": total_analyses,
            "safe_count": safe_count,
            "caution_count": caution_count,
            "danger_count": danger_count
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {
            "total_analyses": 0,
            "safe_count": 0,
            "caution_count": 0,
            "danger_count": 0
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()