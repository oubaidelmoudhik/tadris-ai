"""
AI Service - OpenAI integration for lesson processing.
Migrated from Flask's pdf_generator.py (process_with_ai function)
"""
import json
import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
from django.conf import settings
from .cache_service import get_cached_lesson, set_cached_lesson


# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# Define specific lesson steps per subject
LESSON_STEPS = {
    "français": {
        "1": ["Présentation du vocabulaire", "Exploitation du vocabulaire", "Activités de vocabulaire sur livret"],
        "2": ["Oral – Acte de parole 1", "Ecrit – Point de langue 1", "Lecture – Mots avec difficultés"],
        "3": ["Oral - Acte de parole 2", "Ecrit – Point de langue 2", "Lecture – Phrases"],
        "4": ["Oral – Dialogue", "Lecture – Texte ( fluidité et compréhension)"],
        "5": ["Oral – Prise de parole", "Ecriture – Texte"],
        "6": ["Révision", "Lecture offerte"]
    },
    "mathématiques": {
        "default": ["الافتتاح", "النمذجة", "الممارسة الموجهة", "الممارسة المستقلة", "اختتام الحصة"],
        "5": ["افتتاح الدرس", "مراجعة الدرس 1", "مراجعة الدرس 2", "مراجعة الدرس 3", "مراجعة الدرس 4", "اختتام الحصة"]
    },
    "langue arabe": {
        "default": ["الافتتاح", "النمذجة", "الممارسة الموجهة", "الممارسة المستقلة", "اختتام الحصة"]
    }
}


def get_lesson_steps(subject: str, session: str) -> List[str]:
    """
    Get specific lesson steps based on subject and session.
    
    Args:
        subject: Subject name
        session: Session number
        
    Returns:
        List of step names
    """
    subj_lower = subject.lower()
    sess_str = str(session)
    
    if "français" in subj_lower or "francais" in subj_lower:
        return LESSON_STEPS["français"].get(sess_str, [])
    
    elif "math" in subj_lower:
        try:
            if sess_str == "5":
                return LESSON_STEPS["mathématiques"]["5"]
            elif sess_str == "6":
                return LESSON_STEPS["mathématiques"].get("5", LESSON_STEPS["mathématiques"]["default"])
            return LESSON_STEPS["mathématiques"]["default"]
        except KeyError:
            return LESSON_STEPS["mathématiques"]["default"]
    
    elif "arabe" in subj_lower:
        return LESSON_STEPS["langue arabe"]["default"]
    
    return []


def _build_arabic_prompt(title: str, subject: str, level: str, period: str, 
                         week: str, session: str, content: str, steps: List[str]) -> str:
    """Build Arabic prompt for AI."""
    steps_instruction = ""
    if steps:
        steps_list = "\n".join([f"- {step}" for step in steps])
        steps_instruction = f"""
IMPORTANT: You MUST use EXACTLY these lesson steps in this order:
{steps_list}

For each step, extract relevant content from the slides and assign a realistic duration.
"""
    
    return f"""
You are a teaching assistant generating structured lesson data for a lesson in Arabic.

Return **only valid JSON**, no markdown, no extra text.

{steps_instruction}

Analyze the lesson content and fill in the content for each step. Each step should have:
- name (EXACTLY as specified above)
- duration as in the content (e.g., "10min", "20min")
- icon (emoji)
- content (description in Arabic based on slides)

**OBJECTIVE EXTRACTION (CRITICAL):**
- Extract the main pedagogical objective from the lesson content.
- The objective should be specific, measurable, and action-oriented.
- Example: "تعلم قراءة وكتابة الأعداد من الملايين بالأرقام والحروف"
- Example: "حل مسائل متعلقة بوضعية البحث عن الكل أو الجزء"
- If no explicit objective is found, infer it from the lesson title and content.
- Do NOT use placeholders like "هدف الدرس" or "......".

**PHRASING STYLE (CRITICAL):**
- Use **pedagogical phrasing** describing what the students do.
- Start sentences with **"يقوم التلاميذ بـ..."** or **"يبدأ التaluiذ..."** or **"يشارك التلاميذ..."**.
- Example: "يبدأ التلاميذ بحساب ذهني سريع، ويكتبون النتائج على ألواحهم ثم يصححون بشكل جماعي."
- Example: "يقرأ التلاميذ النص ويستخرجون الكلمات الصعبة."
- Avoid passive voice or simple copying of slide text.

**SPECIFIC CONTENT RULES (CRITICAL):**
- For the step **"الافتتاح"** (Opening): The content MUST explicitly mention correcting homework and mental arithmetic (تصحيح الواجبات المنزلية والحساب الذهني), adapting the specific details to the lesson's context.
- For the step **"النمذجة"** (Modeling): Students do NOT participate in this step. The description must state that they are attentive/listening to the teacher's explanation (ينتبهون للشرح) without active participation.

Follow **exactly** this structure:
{{
  "lesson_data": {{
    "subject": "{subject}",
    "level": "{level}",
    "period": "{period}",
    "week": "{week}",
    "session": "{session}",
    "objective": "هدف الدرس بالعربية",
    "steps": [
      {{
        "name": "Step Name",
        "duration": "10min",
        "icon": "📝",
        "content": "يبدأ التلاميذ..."
      }}
    ]
  }}
}}

Rules:
- All text must be in Arabic
- Use ONLY the specified lesson steps
- Include realistic durations based on the content
- Output must be strictly valid JSON
- Never include ```json or other code fences
- Do not add explanations before or after the JSON

Lesson slides content:
{content}
"""


def _build_french_prompt(title: str, subject: str, level: str, period: str,
                         week: str, session: str, content: str, steps: List[str]) -> str:
    """Build French prompt for AI."""
    steps_instruction = ""
    if steps:
        steps_list = "\n".join([f"- {step}" for step in steps])
        steps_instruction = f"""
IMPORTANT: You MUST use EXACTLY these lesson steps in this order:
{steps_list}

For each step, extract relevant content from the slides and assign a realistic duration.
"""
    
    return f"""
You are a teaching assistant generating structured lesson data for a French lesson.

Return **only valid JSON**, no markdown, no extra text.

{steps_instruction}

Analyze the lesson content and fill in the content for each step. Each step should have:
- name (EXACTLY as specified above)
- duration (e.g., "10min", "20min")
- icon (emoji)
- content (description in French based on slides)

**OBJECTIVE EXTRACTION (CRITICAL):**
- Extract the main pedagogical objective from the lesson content.
- The objective should be specific, measurable, and action-oriented.
- Example: "Utiliser les indicateurs de lieu et leurs contraires"
- Example: "Lire et comprendre des phrases sur les déplacements"
- If no explicit objective is found, infer it from the lesson title and content.
- Do NOT use placeholders like "Objectif de la leçon" or "......".

**PHRASING STYLE (CRITICAL):**
- Use **pedagogical phrasing** describing what the students do.
- Start sentences with **"Les élèves [action]..."**.
- Example: "Les élèves lisent un texte sur les déplacements et identifient les phrases clés."
- Example: "Les élèves commencent par un calcul mental, écrivent les résultats et corrigent ensemble."
- Example: "Les élèves rédigent un paragraphe en utilisant des mots donnés."
- Avoid passive voice or simple copying of slide text.

Follow **exactly** this structure:
{{
  "lesson_data": {{
    "subject": "{subject}",
    "level": "{level}",
    "period": "{period}",
    "week": "{week}",
    "session": "{session}",
    "objective": "Objectif de la leçon en français",
    "steps": [
      {{
        "name": "Step Name",
        "duration": "10min",
        "icon": "📝",
        "content": "Les élèves observent l'image..."
      }}
    ]
  }}
}}

Rules:
- All text must be in French
- Use ONLY the specified lesson steps
- Include realistic durations based on the content
- Output must be strictly valid JSON
- Never include ```json or other code fences
- Do not add explanations before or after the JSON
- Use Moroccan French teaching style (action-based, classroom-focused)

Lesson slides content:
{content}
"""


def process_with_ai(
    title: str,
    subject: str,
    level: str,
    period: str,
    week: str,
    session: str,
    content: str
) -> Optional[Dict[str, Any]]:
    """
    Send lesson content to AI and return structured JSON with lesson data.
    
    Args:
        title: Lesson title
        subject: Subject name
        level: Level/grade
        period: Period number
        week: Week number
        session: Session number
        content: Extracted PPTX text content
        
    Returns:
        Dictionary with lesson_data or None on failure
    """
    # Determine language based on subject
    subj_lower = subject.lower()
    is_math = "math" in subj_lower
    is_arabe = "arabe" in subj_lower
    language = "Arabic" if (is_math or is_arabe) else "French"
    
    # Check cache first
    cached_data = get_cached_lesson(content, language, subject, str(session))
    if cached_data:
        print(f"⚡ Returning cached lesson data (saved API call!)")
        cached_data['title'] = title
        return cached_data
    
    # Get specific steps
    specific_steps = get_lesson_steps(subject, session)
    
    # Build appropriate prompt
    if language == "Arabic":
        prompt = _build_arabic_prompt(
            title, subject, level, period, week, session, content, specific_steps
        )
    else:
        prompt = _build_french_prompt(
            title, subject, level, period, week, session, content, specific_steps
        )
    
    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": f"You generate structured JSON for a teacher's lesson journal in {language}."},
                {"role": "user", "content": prompt}
            ]
        )
        
        raw_result = response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return None
    
    # Parse JSON response
    try:
        raw_result = raw_result.replace("None", "null")
        data = json.loads(raw_result)
        lesson_data = data["lesson_data"]
        
        # Validate required fields
        if not lesson_data.get("objective") or lesson_data["objective"] in ["......", "Objectif de la leçon", "هدف الدرس"]:
            print("⚠️  Warning: Objective is missing or placeholder. Using fallback.")
            lesson_data["objective"] = f"Lesson on {subject} - Session {session}"
        
        if not lesson_data.get("steps") or not isinstance(lesson_data["steps"], list):
            print("❌ Error: Steps are missing or invalid")
            return None
        
        if len(lesson_data["steps"]) == 0:
            print("❌ Error: No steps extracted")
            return None
        
        print(f"✅ Successfully extracted {len(lesson_data.get('steps', []))} lesson steps")
        
        # Cache the result
        set_cached_lesson(content, language, subject, str(session), lesson_data)
        
    except json.JSONDecodeError as e:
        print("❌ Invalid JSON received:", e)
        print("Raw output:\n", raw_result)
        return None
    except KeyError as e:
        print(f"❌ Missing required field: {e}")
        return None
    
    # Inject title and subject into lesson_data
    lesson_data["title"] = title
    lesson_data["subject"] = subject
    
    return lesson_data
