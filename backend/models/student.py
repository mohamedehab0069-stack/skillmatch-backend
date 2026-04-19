from backend.db import query
import json


class StudentProfile:

    @staticmethod
    def create(user_id: int, university: str = None, major: str = None,
               graduation_year: int = None) -> int:
        return query(
            "INSERT INTO student_profiles (user_id, university, major, graduation_year) VALUES (%s,%s,%s,%s)",
            (user_id, university, major, graduation_year), fetch="none"
        )

    @staticmethod
    def get_by_user(user_id: int):
        return query(
            "SELECT * FROM student_profiles WHERE user_id = %s", (user_id,), fetch="one"
        )

    @staticmethod
    def get_by_id(student_id: int):
        return query(
            "SELECT * FROM student_profiles WHERE id = %s", (student_id,), fetch="one"
        )

    @staticmethod
    def update(student_id: int, **fields):
        allowed = {"university", "major", "graduation_year", "linkedin_url",
                   "github_url", "avatar_url"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        cols = ", ".join(f"{k} = %s" for k in updates)
        query(f"UPDATE student_profiles SET {cols} WHERE id = %s",
              (*updates.values(), student_id), fetch="none")

    @staticmethod
    def get_skills(student_id: int):
        rows = query(
            """SELECT s.name, ss.proficiency, ss.is_verified
               FROM student_skills ss
               JOIN skills s ON s.id = ss.skill_id
               WHERE ss.student_id = %s""",
            (student_id,)
        )
        return rows or []

    @staticmethod
    def add_skill(student_id: int, skill_name: str, proficiency: str = "beginner"):
        skill = query("SELECT id FROM skills WHERE name = %s", (skill_name,), fetch="one")
        if not skill:
            skill_id = query(
                "INSERT INTO skills (name) VALUES (%s)", (skill_name,), fetch="none"
            )
        else:
            skill_id = skill["id"]
        try:
            query(
                "INSERT INTO student_skills (student_id, skill_id, proficiency) VALUES (%s,%s,%s)",
                (student_id, skill_id, proficiency), fetch="none"
            )
        except Exception:
            query(
                "UPDATE student_skills SET proficiency=%s WHERE student_id=%s AND skill_id=%s",
                (proficiency, student_id, skill_id), fetch="none"
            )

    @staticmethod
    def verify_skill(student_id: int, skill_name: str):
        skill = query("SELECT id FROM skills WHERE name = %s", (skill_name,), fetch="one")
        if skill:
            query(
                "UPDATE student_skills SET is_verified=TRUE WHERE student_id=%s AND skill_id=%s",
                (student_id, skill["id"]), fetch="none"
            )
