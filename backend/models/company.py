from backend.db import query


class CompanyProfile:

    @staticmethod
    def create(user_id: int, company_name: str, industry: str = None,
               website: str = None, description: str = None) -> int:
        return query(
            "INSERT INTO company_profiles (user_id, company_name, industry, website, description) VALUES (%s,%s,%s,%s,%s)",
            (user_id, company_name, industry, website, description), fetch="none"
        )

    @staticmethod
    def get_by_user(user_id: int):
        return query(
            "SELECT * FROM company_profiles WHERE user_id = %s", (user_id,), fetch="one"
        )

    @staticmethod
    def get_by_id(company_id: int):
        return query(
            "SELECT * FROM company_profiles WHERE id = %s", (company_id,), fetch="one"
        )

    @staticmethod
    def update(company_id: int, **fields):
        allowed = {"company_name", "industry", "website", "description", "logo_url"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        cols = ", ".join(f"{k} = %s" for k in updates)
        query(f"UPDATE company_profiles SET {cols} WHERE id = %s",
              (*updates.values(), company_id), fetch="none")

    @staticmethod
    def verify(company_id: int):
        query("UPDATE company_profiles SET is_verified=TRUE WHERE id=%s",
              (company_id,), fetch="none")
