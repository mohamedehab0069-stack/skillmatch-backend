from backend.db import query
import bcrypt


class User:

    @staticmethod
    def find_by_email(email: str):
        return query(
            "SELECT * FROM users WHERE email = %s LIMIT 1",
            (email.lower(),), fetch="one"
        )

    @staticmethod
    def find_by_id(user_id: int):
        return query(
            "SELECT id, name, email, role, phone, is_active, created_at FROM users WHERE id = %s",
            (user_id,), fetch="one"
        )

    @staticmethod
    def create(name: str, email: str, password_hash: str, role: str, phone: str = None) -> int:
        return query(
            "INSERT INTO users (name, email, password_hash, role, phone) VALUES (%s,%s,%s,%s,%s)",
            (name, email.lower(), password_hash, role, phone), fetch="none"
        )

    @staticmethod
    def check_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def set_active(user_id: int, active: bool):
        query(
            "UPDATE users SET is_active = %s WHERE id = %s",
            (active, user_id), fetch="none"
        )

    @staticmethod
    def all_users(role: str = None):
        if role:
            return query(
                "SELECT id, name, email, role, is_active, created_at FROM users WHERE role = %s ORDER BY created_at DESC",
                (role,)
            )
        return query(
            "SELECT id, name, email, role, is_active, created_at FROM users ORDER BY created_at DESC"
        )
