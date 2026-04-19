from flask import Blueprint, request, jsonify
from backend.services.ai_service import generate_persona

assessment_bp = Blueprint("assessment", __name__)

@assessment_bp.route("/api/assessment/submit", methods=["POST"])
def submit_assessment():
    data = request.get_json()

    answers = data.get("answers", [])

    result = generate_persona(answers)

    return jsonify(result)
from backend.db import query
import json


class CareerAssessment:

    @staticmethod
    def create(student_id: int, quiz_responses: list, ai_raw: dict = None) -> int:
        return query(
            "INSERT INTO career_assessments (student_id, quiz_responses, ai_raw_response) VALUES (%s,%s,%s)",
            (student_id, json.dumps(quiz_responses), json.dumps(ai_raw) if ai_raw else None),
            fetch="none"
        )

    @staticmethod
    def get_latest(student_id: int):
        return query(
            "SELECT * FROM career_assessments WHERE student_id=%s ORDER BY taken_at DESC LIMIT 1",
            (student_id,), fetch="one"
        )

    @staticmethod
    def get_all(student_id: int):
        return query(
            "SELECT id, taken_at FROM career_assessments WHERE student_id=%s ORDER BY taken_at DESC",
            (student_id,)
        )


class CareerPersona:

    @staticmethod
    def create(assessment_id: int, student_id: int, persona: dict) -> int:
        return query(
            """INSERT INTO career_personas
               (assessment_id, student_id, persona_title, persona_description,
                top_career_paths, strengths, skill_gaps)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                assessment_id,
                student_id,
                persona.get("persona_title"),
                persona.get("persona_description"),
                json.dumps(persona.get("top_career_paths", [])),
                json.dumps(persona.get("strengths", [])),
                json.dumps(persona.get("skill_gaps", [])),
            ),
            fetch="none"
        )

    @staticmethod
    def get_latest(student_id: int):
        row = query(
            "SELECT * FROM career_personas WHERE student_id=%s ORDER BY generated_at DESC LIMIT 1",
            (student_id,), fetch="one"
        )
        return CareerPersona._parse(row)

    @staticmethod
    def get_by_id(persona_id: int):
        row = query("SELECT * FROM career_personas WHERE id=%s", (persona_id,), fetch="one")
        return CareerPersona._parse(row)

    @staticmethod
    def _parse(row):
        if not row:
            return None
        for field in ("top_career_paths", "strengths", "skill_gaps"):
            if isinstance(row.get(field), str):
                row[field] = json.loads(row[field])
        return row


class LearningRoadmap:

    @staticmethod
    def create(student_id: int, persona_id: int, career_path: str, steps: list) -> int:
        return query(
            "INSERT INTO learning_roadmaps (student_id, persona_id, career_path, roadmap_steps) VALUES (%s,%s,%s,%s)",
            (student_id, persona_id, career_path, json.dumps(steps)), fetch="none"
        )

    @staticmethod
    def get_active(student_id: int):
        row = query(
            "SELECT * FROM learning_roadmaps WHERE student_id=%s AND status='active' ORDER BY created_at DESC LIMIT 1",
            (student_id,), fetch="one"
        )
        return LearningRoadmap._parse(row)

    @staticmethod
    def get_by_id(roadmap_id: int):
        row = query("SELECT * FROM learning_roadmaps WHERE id=%s", (roadmap_id,), fetch="one")
        return LearningRoadmap._parse(row)

    @staticmethod
    def update_status(roadmap_id: int, status: str):
        query("UPDATE learning_roadmaps SET status=%s WHERE id=%s",
              (status, roadmap_id), fetch="none")

    @staticmethod
    def _parse(row):
        if not row:
            return None
        if isinstance(row.get("roadmap_steps"), str):
            row["roadmap_steps"] = json.loads(row["roadmap_steps"])
        return row
