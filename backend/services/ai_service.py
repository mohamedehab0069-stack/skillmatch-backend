import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── System prompts ────────────────────────────────────────────────────────────

PERSONA_SYSTEM_PROMPT = """
You are a career intelligence engine for SkillMatch+, an AI-powered career
development platform for university students in Egypt.

Given a student's quiz responses, analyse their answers and return ONLY a
valid JSON object with exactly these keys (no markdown, no explanation):

{
  "persona_title": "string — a creative 3-6 word title e.g. 'The Analytical Builder'",
  "persona_description": "string — 2-3 sentences describing this student's career identity",
  "top_career_paths": ["path1", "path2", "path3"],
  "strengths": ["strength1", "strength2", "strength3", "strength4"],
  "skill_gaps": ["gap1", "gap2", "gap3", "gap4"],
  "roadmap_steps": [
    {
      "step": 1,
      "title": "Foundation",
      "description": "What to focus on first",
      "courses": ["Course name 1", "Course name 2"]
    },
    {
      "step": 2,
      "title": "Core Skills",
      "description": "What to build next",
      "courses": ["Course name 3"]
    },
    {
      "step": 3,
      "title": "Specialisation",
      "description": "Advanced area to target",
      "courses": ["Course name 4", "Course name 5"]
    }
  ]
}

Rules:
- Be specific to Business Informatics / Digital Transformation students.
- skill_gaps should reflect what the student answered they lack, or what
  the career path demands that they haven't shown.
- roadmap_steps should be ordered from foundational to advanced.
- Return ONLY the JSON object. No backticks, no extra text.
"""

MATCH_SYSTEM_PROMPT = """
You are a skill-matching engine for SkillMatch+. Your job is to compare
a student's verified skills against an internship's required skills and
return a match score.

Return ONLY a valid JSON object (no markdown, no explanation):
{
  "match_score": <float 0.0 to 100.0>,
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "recommendation": "one sentence explaining the match quality"
}

Scoring guide:
- 90-100: Near-perfect match — student has all or almost all required skills.
- 70-89:  Strong match — student has most required skills with minor gaps.
- 50-69:  Moderate match — student has core skills but needs development.
- 30-49:  Weak match — significant skill gaps exist.
- 0-29:   Poor match — most required skills are missing.

Rules:
- Be strict but fair. Consider proficiency levels when scoring.
- Return ONLY the JSON object. No backticks, no extra text.
"""


# ── Public functions ──────────────────────────────────────────────────────────

def generate_persona(quiz_responses: list) -> dict:
    """
    Send quiz answers to GPT-4o-mini and return parsed career persona dict.
    Raises ValueError if the AI response cannot be parsed.
    """
    user_message = json.dumps({
        "student_quiz_responses": quiz_responses,
        "context": "Business Informatics student in Egypt, 2025"
    }, ensure_ascii=False)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PERSONA_SYSTEM_PROMPT.strip()},
            {"role": "user",   "content": user_message}
        ],
        temperature=0.7,
        max_tokens=1200,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\nRaw: {raw[:300]}")


def calculate_match_score(student_skills: list, required_skills: list) -> dict:
    """
    Compare student skills against internship requirements.
    Returns dict with match_score, matched_skills, missing_skills, recommendation.
    """
    student_skill_names = [
        s["name"] if isinstance(s, dict) else s for s in student_skills
    ]
    required_skill_names = [
        r if isinstance(r, str) else r.get("name", r) for r in required_skills
    ]

    if not required_skill_names:
        return {
            "match_score": 50.0,
            "matched_skills": [],
            "missing_skills": [],
            "recommendation": "No specific skills required — open application."
        }

    prompt = json.dumps({
        "student_verified_skills": student_skill_names,
        "internship_required_skills": required_skill_names
    }, ensure_ascii=False)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": MATCH_SYSTEM_PROMPT.strip()},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2,
        max_tokens=400,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
        result["match_score"] = round(float(result.get("match_score", 0)), 1)
        return result
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"AI match scoring returned invalid JSON: {e}")


def generate_skill_gap_advice(skill_gaps: list, career_path: str) -> str:
    """
    Generate a short personalised paragraph advising the student
    on how to close their identified skill gaps.
    """
    prompt = (
        f"A student pursuing a career as a '{career_path}' has these skill gaps: "
        f"{', '.join(skill_gaps)}. "
        "Write a single motivating paragraph (3-4 sentences) giving them practical "
        "advice on how to close these gaps using online learning and hands-on projects. "
        "Be specific, encouraging, and concise."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=200,
    )

    return response.choices[0].message.content.strip()
def generate_persona(answers):
    print("🔥 AI SERVICE CALLED")
    return {
        "persona": "Test Persona",
        "top_career_paths": ["Backend Developer"],
        "skill_gaps": ["Databases"],
        "roadmap_steps": ["Learn SQL", "Build API"]
    }
    def  generate_persona(answers):
     print ("🔥 AI SERVICE CALLED")

    # تحليل بسيط جدًا كبداية
    if len(answers) >= 5:
        return {
            "persona": "Backend Developer",
            "top_career_paths": [
                "Backend Developer",
                "Data Engineer"
            ],
            "skill_gaps": [
                "Databases",
                "APIs"
            ],
            "roadmap_steps": [
                "Learn SQL",
                "Build REST API",
                "Practice Flask"
            ]
        }

    return {
        "persona": "Unknown",
        "top_career_paths": [],
        "skill_gaps": [],
        "roadmap_steps": []
    }