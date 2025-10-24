"""
FastAPI Server for AI Question Generation
Serves the AI-powered question generator via REST API
Optimized for CPU execution on laptops
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import logging
import time
import asyncio
from contextlib import asynccontextmanager

from ai_question_generator import AIQuestionGenerator, QuestionRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for the generator
question_generator = None
generator_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    global question_generator, generator_ready
    logger.info("Starting AI Question Generator Server...")
    
    try:
        question_generator = AIQuestionGenerator()
        generator_ready = True
        logger.info("Question generator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize question generator: {e}")
        generator_ready = False
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Question Generator Server...")


# Create FastAPI app
app = FastAPI(
    title="AI Question Generator API",
    description="AI-powered question generation API for QuizHive",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests and responses
class QuestionGenerationRequest(BaseModel):
    """Request model for question generation"""
    topic: str = Field(..., description="Topic for question generation (e.g., AWS, Python, Docker)")
    level: str = Field(..., description="Difficulty level: beginner, intermediate, advanced")
    num_questions: int = Field(..., ge=1, le=50, description="Number of questions to generate (1-50)")
    core_type: Optional[str] = Field(None, description="Core type: baseline or variable")
    keywords: Optional[List[str]] = Field(None, description="Additional keywords to focus on")


class QuestionResponse(BaseModel):
    """Response model for generated questions"""
    id: str
    core_type: str
    level: str
    topic: str
    question: str
    options: Dict[str, str]
    correct: str
    explanation: str


class QuizGenerationResponse(BaseModel):
    """Response model for quiz generation"""
    topic: str
    level: str
    total_questions: int
    generated_at: str
    questions: List[QuestionResponse]
    generation_time_ms: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    generator_ready: bool
    version: str
    uptime_seconds: float


class TopicListResponse(BaseModel):
    """Response model for available topics"""
    topics: List[str]
    levels: List[str]


# Global start time
start_time = time.time()


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "AI Question Generator API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - start_time
    return HealthResponse(
        status="healthy" if generator_ready else "initializing",
        generator_ready=generator_ready,
        version="2.0.0",
        uptime_seconds=uptime
    )


@app.get("/topics", response_model=TopicListResponse)
async def get_available_topics():
    """Get list of available topics and levels"""
    if not generator_ready:
        raise HTTPException(status_code=503, detail="Question generator not ready")
    
    topics = ["Any topic supported - AI generates concepts dynamically"]
    levels = ["beginner", "intermediate", "advanced"]
    
    return TopicListResponse(
        topics=topics,
        levels=levels
    )


@app.post("/generate-questions", response_model=QuizGenerationResponse)
async def generate_questions(request: QuestionGenerationRequest):
    """Generate questions based on the request"""
    if not generator_ready:
        raise HTTPException(status_code=503, detail="Question generator not ready")
    
    start_generation_time = time.time()
    
    try:
        # Validate inputs
        if request.level not in ["beginner", "intermediate", "advanced"]:
            raise HTTPException(
                status_code=400, 
                detail="Level must be one of: beginner, intermediate, advanced"
            )
        
        if request.core_type and request.core_type not in ["baseline", "variable"]:
            raise HTTPException(
                status_code=400,
                detail="Core type must be one of: baseline, variable"
            )
        
        # Create question request
        question_request = QuestionRequest(
            topic=request.topic,
            level=request.level,
            num_questions=request.num_questions,
            core_type=request.core_type,
            keywords=request.keywords
        )
        
        # Generate questions
        questions = question_generator.generate_questions(question_request)
        
        # Calculate generation time
        generation_time = int((time.time() - start_generation_time) * 1000)
        
        # Convert to response format
        question_responses = []
        for q in questions:
            question_responses.append(QuestionResponse(
                id=q.id,
                core_type=q.core_type,
                level=q.level,
                topic=q.topic,
                question=q.question,
                options=q.options,
                correct=q.correct,
                explanation=q.explanation
            ))
        
        return QuizGenerationResponse(
            topic=request.topic,
            level=request.level,
            total_questions=len(question_responses),
            generated_at=questions[0].__dict__.get('generated_at', '') if questions else '',
            questions=question_responses,
            generation_time_ms=generation_time
        )
        
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")


@app.post("/generate-quiz")
async def generate_quiz(request: QuestionGenerationRequest):
    """Generate a complete quiz (alternative endpoint)"""
    # This endpoint uses the same logic but returns a slightly different format
    if not generator_ready:
        raise HTTPException(status_code=503, detail="Question generator not ready")
    
    try:
        quiz = question_generator.generate_quiz(
            topic=request.topic,
            level=request.level,
            num_questions=request.num_questions,
            keywords=request.keywords
        )
        
        return quiz
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


@app.get("/stats")
async def get_generation_stats():
    """Get generation statistics"""
    if not generator_ready:
        raise HTTPException(status_code=503, detail="Question generator not ready")
    
    uptime = time.time() - start_time
    
    return {
        "uptime_seconds": uptime,
        "generator_ready": generator_ready,
        "available_topics": ["Any topic supported - AI generates concepts dynamically"],
        "supported_levels": ["beginner", "intermediate", "advanced"],
        "max_questions_per_request": 50,
        "generator_type": "AI-powered with fallback templates",
        "models_loaded": question_generator.models_loaded
    }


@app.post("/validate-questions")
async def validate_questions(questions: List[Dict[str, Any]]):
    """Validate generated questions for quality"""
    if not generator_ready:
        raise HTTPException(status_code=503, detail="Question generator not ready")
    
    validation_results = []
    
    for i, question in enumerate(questions):
        issues = []
        
        # Check required fields
        required_fields = ["id", "core_type", "level", "topic", "question", "options", "correct", "explanation"]
        for field in required_fields:
            if field not in question:
                issues.append(f"Missing required field: {field}")
        
        # Validate options
        if "options" in question:
            options = question["options"]
            if not isinstance(options, dict):
                issues.append("Options must be a dictionary")
            elif len(options) != 4:
                issues.append("Must have exactly 4 options")
            else:
                # Check if correct answer exists in options
                correct = question.get("correct")
                if correct and correct not in options:
                    issues.append(f"Correct answer '{correct}' not found in options")
        
        # Validate core_type
        if "core_type" in question:
            if question["core_type"] not in ["baseline", "variable"]:
                issues.append("Core type must be 'baseline' or 'variable'")
        
        # Validate level
        if "level" in question:
            if question["level"] not in ["beginner", "intermediate", "advanced"]:
                issues.append("Level must be 'beginner', 'intermediate', or 'advanced'")
        
        validation_results.append({
            "question_index": i,
            "question_id": question.get("id", f"question_{i}"),
            "is_valid": len(issues) == 0,
            "issues": issues
        })
    
    return {
        "total_questions": len(questions),
        "valid_questions": sum(1 for r in validation_results if r["is_valid"]),
        "validation_results": validation_results
    }


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
