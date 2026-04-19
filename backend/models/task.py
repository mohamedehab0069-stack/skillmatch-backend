from backend.db import query
import json
from datetime import datetime


class MicroTask:

    @staticmethod
    def create(company_id: int, title: str, description: str,
               category: str, difficulty: str, points: int) -> int:
        return query(
            "INSERT INTO micro_tasks (company_id,title,description,category,difficulty,points) VALUES (%s,%s,%s,%s,%s,%s)",
            (company_id, title, description, category, difficulty, points), fetch="none"
        )

    @staticmethod
    def get_active(category: str = None):
        if category:
            return query(
                "SELECT mt.*, cp.company_name FROM micro_tasks mt JOIN company_profiles cp ON cp.id=mt.company_id WHERE mt.is_active=TRUE AND mt.category=%s ORDER BY mt.created_at DESC",
                (category,)
            )
        return query(
            "SELECT mt.*, cp.company_name FROM micro_tasks mt JOIN company_profiles cp ON cp.id=mt.company_id WHERE mt.is_active=TRUE ORDER BY mt.created_at DESC"
        )

    @staticmethod
    def get_by_id(task_id: int):
        return query(
            "SELECT mt.*, cp.company_name FROM micro_tasks mt JOIN company_profiles cp ON cp.id=mt.company_id WHERE mt.id=%s",
            (task_id,), fetch="one"
        )

    @staticmethod
    def get_by_company(company_id: int):
        return query(
            "SELECT * FROM micro_tasks WHERE company_id=%s ORDER BY created_at DESC",
            (company_id,)
        )

    @staticmethod
    def toggle_active(task_id: int, active: bool):
        query("UPDATE micro_tasks SET is_active=%s WHERE id=%s",
              (active, task_id), fetch="none")


class TaskSubmission:

    @staticmethod
    def create(student_id: int, task_id: int, content: str, url: str) -> int:
        return query(
            "INSERT INTO task_submissions (student_id,task_id,submission_content,submission_url) VALUES (%s,%s,%s,%s)",
            (student_id, task_id, content, url), fetch="none"
        )

    @staticmethod
    def get_by_id(submission_id: int):
        return query("SELECT * FROM task_submissions WHERE id=%s", (submission_id,), fetch="one")

    @staticmethod
    def get_by_student(student_id: int):
        return query(
            """SELECT ts.*, mt.title as task_title, mt.points, cp.company_name
               FROM task_submissions ts
               JOIN micro_tasks mt ON mt.id=ts.task_id
               JOIN company_profiles cp ON cp.id=mt.company_id
               WHERE ts.student_id=%s ORDER BY ts.submitted_at DESC""",
            (student_id,)
        )

    @staticmethod
    def get_pending_for_task(task_id: int):
        return query(
            """SELECT ts.*, u.name as student_name, sp.university
               FROM task_submissions ts
               JOIN student_profiles sp ON sp.id=ts.student_id
               JOIN users u ON u.id=sp.user_id
               WHERE ts.task_id=%s AND ts.status='pending'
               ORDER BY ts.submitted_at ASC""",
            (task_id,)
        )

    @staticmethod
    def review(submission_id: int, status: str, score: int, feedback: str):
        query(
            "UPDATE task_submissions SET status=%s,score=%s,feedback=%s,reviewed_at=%s WHERE id=%s",
            (status, score, feedback, datetime.utcnow(), submission_id), fetch="none"
        )


class PortfolioItem:

    @staticmethod
    def create(student_id: int, submission_id: int, title: str,
               description: str, item_url: str) -> int:
        return query(
            "INSERT INTO portfolio_items (student_id,submission_id,title,description,item_url) VALUES (%s,%s,%s,%s,%s)",
            (student_id, submission_id, title, description, item_url), fetch="none"
        )

    @staticmethod
    def get_by_student(student_id: int, public_only: bool = False):
        sql = """SELECT pi.*, mt.title as task_title, mt.category
                 FROM portfolio_items pi
                 JOIN task_submissions ts ON ts.id=pi.submission_id
                 JOIN micro_tasks mt ON mt.id=ts.task_id
                 WHERE pi.student_id=%s"""
        if public_only:
            sql += " AND pi.is_public=TRUE"
        sql += " ORDER BY pi.created_at DESC"
        return query(sql, (student_id,))

    @staticmethod
    def toggle_public(item_id: int, student_id: int, is_public: bool):
        query("UPDATE portfolio_items SET is_public=%s WHERE id=%s AND student_id=%s",
              (is_public, item_id, student_id), fetch="none")
