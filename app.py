import os
import uvicorn
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

import database as db
import gemini_service as ai

app = FastAPI(
    title="EduGenie API",
    description="Google Gemini Powered Educational Assistant API",
    version="1.0.0"
)

# Netlify & Serverless path normalization middleware
@app.middleware("http")
async def normalize_serverless_path(request: Request, call_next):
    path = request.scope.get("path", "")
    if path.startswith("/.netlify/functions/api"):
        sub_path = path[len("/.netlify/functions/api"):]
        if not sub_path.startswith("/api") and sub_path != "":
            path = "/api" + sub_path
        else:
            path = sub_path
        request.scope["path"] = path
    elif path in ["/ask", "/quiz", "/learning-path", "/summarize", "/history"]:
        request.scope["path"] = "/api" + path

    response = await call_next(request)
    return response

# Ensure static folder exists
os.makedirs("static", exist_ok=True)

# Define Request Schemas (Pydantic V2 compliant)
class AskRequest(BaseModel):
    question: str = Field(..., json_schema_extra={"example": "Which is the largest ocean?"})
    mode: str = Field(default="explain", json_schema_extra={"example": "explain"})  # "explain" or "simplify"

class QuizRequest(BaseModel):
    topic: str = Field(..., json_schema_extra={"example": "The Pythagoras Theorem"})
    difficulty: str = Field(default="medium", json_schema_extra={"example": "medium"})
    num_questions: int = Field(default=4, ge=1, le=10)

class LearningPathRequest(BaseModel):
    topic: str = Field(..., json_schema_extra={"example": "SQL"})
    level: str = Field(default="beginner to advanced", json_schema_extra={"example": "beginner to advanced"})

class SummarizeRequest(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "Educational passage text to summarize..."})
    max_points: int = Field(default=5, ge=1, le=10)

# Helper to get API key from request header X-Gemini-API-Key or env
def resolve_api_key(x_gemini_api_key: Optional[str] = Header(None)) -> Optional[str]:
    return ai.get_api_key(x_gemini_api_key)

# Fallback Mock Data for demo mode when API Key is missing
MOCK_QA = {
    "which is the largest ocean?": (
        "### Pacific Ocean\n\n"
        "The **Pacific Ocean** is the largest and deepest of Earth's oceanic divisions. "
        "It extends from the Arctic Ocean in the north to the Southern Ocean in the south.\n\n"
        "**Key Facts:**\n"
        "- **Area:** Approx. 165.25 million square kilometers (63.8 million square miles).\n"
        "- **Coverage:** Covers about 32% of Earth's total surface area and 46% of Earth's water surface.\n"
        "- **Deepest Point:** The Mariana Trench (Challenger Deep) at approximately 10,994 meters (36,070 ft).\n"
        "- **Origin of Name:** Named by explorer Ferdinand Magellan, meaning 'peaceful sea'."
    )
}

MOCK_QUIZ = {
    "the pythagoras theorem": {
        "topic": "The Pythagoras Theorem",
        "difficulty": "medium",
        "questions": [
            {
                "id": 1,
                "question": "What is the mathematical formula for the Pythagorean Theorem?",
                "options": ["a² + b² = c²", "a + b = c", "a² - b² = c²", "2a + 2b = c²"],
                "correct_answer": "a² + b² = c²",
                "explanation": "In a right-angled triangle, the square of the hypotenuse (c) is equal to the sum of the squares of the other two sides (a and b)."
            },
            {
                "id": 2,
                "question": "In a right-angled triangle with side lengths a = 3 and b = 4, what is the length of hypotenuse c?",
                "options": ["5", "7", "12", "25"],
                "correct_answer": "5",
                "explanation": "c² = 3² + 4² = 9 + 16 = 25. Therefore c = √25 = 5 (a classic 3-4-5 right triangle)."
            },
            {
                "id": 3,
                "question": "To which type of triangle does the Pythagorean Theorem apply?",
                "options": ["Right-angled triangle", "Equilateral triangle", "Isosceles triangle (non-right)", "Scalene triangle (obtuse)"],
                "correct_answer": "Right-angled triangle",
                "explanation": "The Pythagorean Theorem exclusively applies to right-angled triangles (triangles with one 90-degree angle)."
            },
            {
                "id": 4,
                "question": "What is the longest side of a right-angled triangle called?",
                "options": ["Hypotenuse", "Adjacent", "Opposite", "Perpendicular"],
                "correct_answer": "Hypotenuse",
                "explanation": "The side opposite the 90-degree right angle is the longest side, called the hypotenuse."
            }
        ]
    }
}

MOCK_PATH = {
    "sql": {
        "title": "Learning Path for SQL",
        "overview": "A structured step-by-step roadmap to master SQL from fundamental queries to advanced database administration and optimization.",
        "estimated_time": "4-6 weeks (4 hrs/week)",
        "stages": [
            {
                "stage_number": 1,
                "title": "Stage 1: SQL Basics & Data Querying",
                "duration": "Week 1",
                "topics": ["Relational Databases & Tables", "SELECT, WHERE, ORDER BY", "Filtering with AND, OR, NOT, IN, BETWEEN"],
                "learning_goals": ["Understand database tables", "Write basic queries to retrieve data", "Filter records effectively"],
                "suggested_projects_or_exercises": ["Query an Employee database to list top earners and department filtering."]
            },
            {
                "stage_number": 2,
                "title": "Stage 2: Aggregations & Joins",
                "duration": "Week 2-3",
                "topics": ["GROUP BY & HAVING", "Aggregate Functions (COUNT, SUM, AVG, MIN, MAX)", "INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN"],
                "learning_goals": ["Summarize data into metrics", "Combine data from multiple relational tables"],
                "suggested_projects_or_exercises": ["Build an E-commerce sales analysis query joining Customers, Orders, and Products."]
            },
            {
                "stage_number": 3,
                "title": "Stage 3: Advanced SQL & Optimization",
                "duration": "Week 4-5",
                "topics": ["Subqueries & CTEs (Common Table Expressions)", "Window Functions (ROW_NUMBER, RANK, LEAD, LAG)", "Indexes & Query Performance Tuning"],
                "learning_goals": ["Write complex analytical queries", "Optimize slow-running database operations"],
                "suggested_projects_or_exercises": ["Create a monthly revenue growth calculation using window functions."]
            }
        ],
        "tips_for_success": [
            "Practice writing raw SQL daily on platforms like LeetCode or SQLBolt.",
            "Always inspect EXPLAIN plans when optimizing slow queries."
        ]
    }
}


@app.post("/api/ask")
def api_ask_question(req: AskRequest, x_gemini_api_key: Optional[str] = Header(None)):
    api_key = resolve_api_key(x_gemini_api_key)
    
    if not api_key:
        # Check mock fallback
        q_lower = req.question.strip().lower()
        if q_lower in MOCK_QA:
            answer = MOCK_QA[q_lower]
        else:
            answer = (
                f"### Answer to: '{req.question}'\n\n"
                f"EduGenie processed your query in demonstration mode.\n\n"
                f"- **Concept Overview:** Understanding '{req.question}' involves key educational principles.\n"
                f"- **Explanation:** To enable live generative AI responses from Google Gemini, please enter your Gemini API Key in the API Key settings input above or set `GEMINI_API_KEY` in your `.env` file."
            )
    else:
        try:
            answer = ai.ask_question(req.question, mode=req.mode, api_key=api_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini API Error: {str(e)}")

    try:
        db.save_qa(req.question, answer, req.mode)
    except Exception:
        pass
    return {"question": req.question, "answer": answer, "mode": req.mode}


@app.post("/api/quiz")
def api_generate_quiz(req: QuizRequest, x_gemini_api_key: Optional[str] = Header(None)):
    api_key = resolve_api_key(x_gemini_api_key)
    
    if not api_key:
        t_lower = req.topic.strip().lower()
        if t_lower in MOCK_QUIZ:
            quiz_data = MOCK_QUIZ[t_lower]
        else:
            quiz_data = {
                "topic": req.topic,
                "difficulty": req.difficulty,
                "questions": [
                    {
                        "id": 1,
                        "question": f"What is the fundamental concept behind {req.topic}?",
                        "options": ["Core principles and theory", "Random application", "Historical trivia only", "None of the above"],
                        "correct_answer": "Core principles and theory",
                        "explanation": f"{req.topic} is built upon core analytical and practical principles."
                    },
                    {
                        "id": 2,
                        "question": f"Which of the following is a primary use case of {req.topic}?",
                        "options": ["Problem solving and analysis", "Manual document filing", "Unrelated computation", "Static storage"],
                        "correct_answer": "Problem solving and analysis",
                        "explanation": f"Understanding {req.topic} allows for structured problem solving."
                    }
                ]
            }
    else:
        try:
            quiz_data = ai.generate_quiz(req.topic, difficulty=req.difficulty, num_questions=req.num_questions, api_key=api_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini API Quiz Error: {str(e)}")

    try:
        db.save_quiz(req.topic, quiz_data)
    except Exception:
        pass
    return quiz_data


@app.post("/api/learning-path")
def api_generate_learning_path(req: LearningPathRequest, x_gemini_api_key: Optional[str] = Header(None)):
    api_key = resolve_api_key(x_gemini_api_key)
    
    if not api_key:
        t_lower = req.topic.strip().lower()
        if t_lower in MOCK_PATH:
            path_data = MOCK_PATH[t_lower]
        else:
            path_data = {
                "title": f"Learning Path for {req.topic}",
                "overview": f"A structured step-by-step guide to mastering {req.topic}.",
                "estimated_time": "3-4 weeks",
                "stages": [
                    {
                        "stage_number": 1,
                        "title": f"Stage 1: Fundamentals of {req.topic}",
                        "duration": "Week 1",
                        "topics": ["Introduction & History", "Basic Syntax and Concepts", "Environment Setup"],
                        "learning_goals": ["Understand core terms", "Build first simple example"],
                        "suggested_projects_or_exercises": ["Complete basic hello-world or starter exercise."]
                    },
                    {
                        "stage_number": 2,
                        "title": f"Stage 2: Intermediate {req.topic} Techniques",
                        "duration": "Week 2-3",
                        "topics": ["Core Workflows", "Best Practices", "Common Patterns"],
                        "learning_goals": ["Apply patterns to practical tasks"],
                        "suggested_projects_or_exercises": ["Build a small portfolio project."]
                    }
                ],
                "tips_for_success": [
                    "Practice consistently every day.",
                    "Build small projects to reinforce learning."
                ]
            }
    else:
        try:
            path_data = ai.generate_learning_path(req.topic, level=req.level, api_key=api_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini API Learning Path Error: {str(e)}")

    try:
        db.save_learning_path(req.topic, path_data)
    except Exception:
        pass
    return path_data


@app.post("/api/summarize")
def api_summarize_text(req: SummarizeRequest, x_gemini_api_key: Optional[str] = Header(None)):
    api_key = resolve_api_key(x_gemini_api_key)
    
    if not api_key:
        # Simple local summary generator for demo mode
        text_lines = [line.strip() for line in req.text.split(".") if line.strip()]
        summary_overview = req.text[:200] + "..." if len(req.text) > 200 else req.text
        key_points = text_lines[:req.max_points] if text_lines else ["Educational passage provided."]
        
        summary_data = {
            "summary": f"Summary: {summary_overview}",
            "key_takeaways": key_points,
            "important_terms": [
                {"term": "FastAPI", "definition": "Modern, fast web framework for building APIs with Python."},
                {"term": "Generative AI", "definition": "AI models capable of generating text, code, or images based on prompts."}
            ]
        }
    else:
        try:
            summary_data = ai.summarize_text(req.text, max_points=req.max_points, api_key=api_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini API Summarizer Error: {str(e)}")

    try:
        db.save_summary(req.text, summary_data.get("summary", ""), summary_data.get("key_takeaways", []))
    except Exception:
        pass
    return summary_data


@app.get("/api/history")
def api_get_history():
    try:
        return db.get_qa_history()
    except Exception:
        return []


# Mount Static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/style.css")
def get_css():
    return FileResponse("static/style.css", media_type="text/css")

@app.get("/app.js")
def get_js():
    return FileResponse("static/app.js", media_type="application/javascript")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    print("Starting EduGenie server...")
    print("Open http://127.0.0.1:8000 in your browser.")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
