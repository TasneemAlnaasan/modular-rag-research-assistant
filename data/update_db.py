import sqlite3
from datetime import date

def update_company(company_name: str, **fields):
    """
    Update any number of columns for a specified comoany.
    Example: update_company("openai", valuation_usd_millions=7000000, last_funding_round="Series X")
    """
    conn = sqlite3.connect("data/company_data.db")
    cursor = conn.cursor()

    fields["last_updated"] = str(date.today()) # updated automatically every time

    set_clause = ", ".join(f"{col} = ?" for col in fields)
    values = list(fields.values()) + [company_name]

    cursor.execute(f"""
        UPDATE company_funding
        SET {set_clause}
        WHERE company_name = ?
    """, values)

    conn.commit()
    conn.close()
    print(f"Updated {company_name}: {fields}")


if __name__ == "__main__":
    update_company("openai",
                    valuation_usd_millions=900000,
                    last_funding_round="Series I (, Date)")
