import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Check available SDKs
USE_GENAI_SDK = False
try:
    from google import genai
    from google.genai import types
    USE_GENAI_SDK = True
except ImportError:
    try:
        import google.generativeai as legacy_genai
        USE_GENAI_SDK = False
    except ImportError:
        pass

MODEL_NAME = "gemini-2.5-flash"

def get_api_key(custom_key: Optional[str] = None) -> Optional[str]:
    """Retrieve API key from argument or environment variable."""
    if custom_key and custom_key.strip():
        return custom_key.strip()
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    return None

def clean_json_string(text: str) -> str:
    """Extract clean JSON string from markdown code blocks or raw text."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def generate_with_gemini(prompt: str, api_key: Optional[str] = None, system_instruction: Optional[str] = None) -> str:
    key = get_api_key(api_key)
    if not key:
        raise ValueError("Google Gemini API Key is missing. Please provide a valid key in settings or .env file.")

    if USE_GENAI_SDK:
        client = genai.Client(api_key=key)
        config = types.GenerateContentConfig()
        if system_instruction:
            config.system_instruction = system_instruction
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )
        return response.text
    else:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=key)
        model = legacy_genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        response = model.generate_content(prompt)
        return response.text


def ask_question(question: str, mode: str = "explain", api_key: Optional[str] = None) -> str:
    """Answer educational questions or simplify complex concepts."""
    system_prompt = (
        "You are EduGenie, an expert AI educational assistant. "
        "Your goal is to help students learn effectively. "
        "Provide accurate, clear, concise, and structured answers. "
        "Use markdown formatting (bullet points, bold text, code blocks) where appropriate. "
        "Include relevant real-world examples or analogies when explaining concepts."
    )
    
    if mode == "simplify":
        prompt = (
            f"Explain the following concept in extremely simple, intuitive terms suitable for a beginner or high school student:\n\n"
            f"Concept / Question: {question}\n\n"
            f"Structure your response with:\n"
            f"1. Core Idea (Simple definition)\n"
            f"2. Real-world Analogy\n"
            f"3. Key Takeaways (3-4 bullet points)"
        )
    else:
        prompt = f"Answer the following educational question thoroughly and clearly:\n\n{question}"
        
    return generate_with_gemini(prompt, api_key=api_key, system_instruction=system_prompt)


def generate_quiz(topic: str, difficulty: str = "medium", num_questions: int = 4, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Generate an interactive quiz on a given topic."""
    system_prompt = "You are an educational assessment expert. Output ONLY valid JSON."
    
    prompt = f"""Generate a {difficulty} level quiz on the topic: "{topic}".
Create exactly {num_questions} multiple-choice questions.

Return your response strictly as a JSON object matching this schema:
{{
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "id": 1,
      "question": "Question text here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Brief explanation of why this answer is correct."
    }}
  ]
}}

Do NOT include any extra conversational text outside the JSON object.
"""
    raw_response = generate_with_gemini(prompt, api_key=api_key, system_instruction=system_prompt)
    cleaned = clean_json_string(raw_response)
    
    try:
        data = json.loads(cleaned)
        return data
    except Exception as e:
        # Fallback regex extraction if JSON parsing fails
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Failed to parse quiz response as JSON: {str(e)}")


def generate_learning_path(topic: str, level: str = "beginner to advanced", api_key: Optional[str] = None) -> Dict[str, Any]:
    """Generate a structured learning path / roadmap for a topic."""
    system_prompt = "You are a curriculum design expert. Output ONLY valid JSON."
    
    prompt = f"""Design a comprehensive learning roadmap for learning: "{topic}" (Level: {level}).

Return your response strictly as a JSON object matching this schema:
{{
  "title": "Learning Path for {topic}",
  "overview": "Brief description of the learning goal and outcome.",
  "estimated_time": "e.g., 4 weeks (5 hrs/week)",
  "stages": [
    {{
      "stage_number": 1,
      "title": "Stage title (e.g. Foundations & Basics)",
      "duration": "e.g. Week 1",
      "topics": ["Topic 1", "Topic 2", "Topic 3"],
      "learning_goals": ["Goal 1", "Goal 2"],
      "suggested_projects_or_exercises": ["Exercise or mini project idea"]
    }}
  ],
  "tips_for_success": ["Tip 1", "Tip 2"]
}}

Do NOT include any text outside the JSON object.
"""
    raw_response = generate_with_gemini(prompt, api_key=api_key, system_instruction=system_prompt)
    cleaned = clean_json_string(raw_response)
    
    try:
        return json.loads(cleaned)
    except Exception as e:
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Failed to parse learning path response as JSON: {str(e)}")


def summarize_text(text: str, max_points: int = 5, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Summarize educational passages or notes."""
    system_prompt = "You are an educational content summarizer. Output ONLY valid JSON."
    
    prompt = f"""Summarize the following educational content:

---
{text}
---

Return your response strictly as a JSON object matching this schema:
{{
  "summary": "Concise 2-3 sentence overview of the main topic.",
  "key_takeaways": [
    "Key takeaway point 1",
    "Key takeaway point 2"
  ],
  "important_terms": [
    {{"term": "Term Name", "definition": "Brief definition"}}
  ]
}}

Limit key_takeaways to at most {max_points} points.
Do NOT include any text outside the JSON object.
"""
    raw_response = generate_with_gemini(prompt, api_key=api_key, system_instruction=system_prompt)
    cleaned = clean_json_string(raw_response)
    
    try:
        return json.loads(cleaned)
    except Exception as e:
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Failed to parse summary response as JSON: {str(e)}")
