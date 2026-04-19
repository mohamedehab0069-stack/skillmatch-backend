from backend.db import query
import json


class Internship:

    @staticmethod
    def create(company_id: int, title: str, description: str, location: str,
               is_remote: bool, required_skills: list, duration_weeks: int,
               deadline: str = None) -> int:
        return query(
            """INSERT INTO internships
               (company_id,title,description,location,is_remote,required_skills,
                duration_weeks,application_deadline)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (company_id, title, description, location, is_remote,
             json.dumps(required_skills), duration_weeks, deadline),
            fetch="none"
        )

    @staticmethod
    def get_active():
        rows = query(
            """SELECT i.*, cp.company_name, cp.logo_url, cp.industry
               FROM internships i
               JOIN company_profiles cp ON cp.id=i.company_id
               WHERE i.status='active'
               ORDER BY i.created_at DESC"""
        )
        for r in rows:
            if isinstance(r.get("required_skills"), str):
                r["required_skills"] = json.loads(r["required_skills"])
        return rows

    @staticmethod
    def get_by_id(internship_id: int):
        row = query(
            """SELECT i.*, cp.company_name, cp.logo_url, cp.industry
               FROM internships i
               JOIN company_profiles cp ON cp.id=i.company_id
               WHERE i.id=%s""",
            (internship_id,), fetch="one"
        )
        if row and isinstance(row.get("required_skills"), str):
            row["required_skills"] = json.loads(row["required_skills"])
        return row

    @staticmethod
    def get_by_company(company_id: int):
        rows = query(
            "SELECT * FROM internships WHERE company_id=%s ORDER BY created_at DESC",
            (company_id,)
        )
        for r in rows:
            if isinstance(r.get("required_skills"), str):
                r["required_skills"] = json.loads(r["required_skills"])
        return rows

    @staticmethod
    def update_status(internship_id: int, status: str):
        query("UPDATE internships SET status=%s WHERE id=%s",
              (status, internship_id), fetch="none")

    @staticmethod
    def already_applied(student_id: int, internship_id: int) -> bool:
        row = query(
            "SELECT id FROM internship_applications WHERE student_id=%s AND internship_id=%s",
            (student_id, internship_id), fetch="one"
        )
        return row is not None

    @staticmethod
    def apply(student_id: int, internship_id: int,
              match_score: float, match_breakdown: dict, cover_note: str) -> int:
        return query(
            """INSERT INTO internship_applications
               (student_id,internship_id,ai_match_score,match_breakdown,cover_note)
               VALUES (%s,%s,%s,%s,%s)""",
            (student_id, internship_id, match_score,
             json.dumps(match_breakdown), cover_note),
            fetch="none"
        )

    @staticmethod
    def get_applications_for_internship(internship_id: int):
        rows = query(
            """SELECT ia.*, u.name as student_name, sp.university, sp.major,
                      sp.linkedin_url, sp.github_url
               FROM internship_applications ia
               JOIN student_profiles sp ON sp.id=ia.student_id
               JOIN users u ON u.id=sp.user_id
               WHERE ia.internship_id=%s
               ORDER BY ia.ai_match_score DESC""",
            (internship_id,)
        )
        for r in rows:
            if isinstance(r.get("match_breakdown"), str):
                r["match_breakdown"] = json.loads(r["match_breakdown"])
        return rows

    @staticmethod
    def get_student_applications(student_id: int):
        rows = query(
            """SELECT ia.*, i.title as internship_title, cp.company_name
               FROM internship_applications ia
               JOIN internships i ON i.id=ia.internship_id
               JOIN company_profiles cp ON cp.id=i.company_id
               WHERE ia.student_id=%s ORDER BY ia.applied_at DESC""",
            (student_id,)
        )
        for r in rows:
            if isinstance(r.get("match_breakdown"), str):
                r["match_breakdown"] = json.loads(r["match_breakdown"])
        return rows

    @staticmethod
    def update_application_status(application_id: int, status: str):
        query("UPDATE internship_applications SET status=%s WHERE id=%s",
              (status, application_id), fetch="none")
