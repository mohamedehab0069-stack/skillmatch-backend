from backend.db import query


class Notification:

    @staticmethod
    def create(user_id: int, title: str, message: str, ntype: str = "info") -> int:
        return query(
            "INSERT INTO notifications (user_id,title,message,type) VALUES (%s,%s,%s,%s)",
            (user_id, title, message, ntype), fetch="none"
        )

    @staticmethod
    def get_for_user(user_id: int, unread_only: bool = False):
        sql = "SELECT * FROM notifications WHERE user_id=%s"
        if unread_only:
            sql += " AND is_read=FALSE"
        sql += " ORDER BY created_at DESC LIMIT 50"
        return query(sql, (user_id,))

    @staticmethod
    def mark_read(notification_id: int, user_id: int):
        query("UPDATE notifications SET is_read=TRUE WHERE id=%s AND user_id=%s",
              (notification_id, user_id), fetch="none")

    @staticmethod
    def mark_all_read(user_id: int):
        query("UPDATE notifications SET is_read=TRUE WHERE user_id=%s",
              (user_id,), fetch="none")

    @staticmethod
    def unread_count(user_id: int) -> int:
        row = query(
            "SELECT COUNT(*) as cnt FROM notifications WHERE user_id=%s AND is_read=FALSE",
            (user_id,), fetch="one"
        )
        return row["cnt"] if row else 0
