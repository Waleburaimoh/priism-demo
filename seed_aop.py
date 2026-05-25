#!/usr/bin/env python3
"""
Seed script for priism.aop_activities.
Usage: python seed_aop.py <path_to_excel> <aop_id>
"""

import sys
import uuid
from datetime import date, timedelta

try:
    import pyodbc
    import pandas as pd
except ImportError:
    print("Missing dependencies. Run: pip install pyodbc pandas openpyxl")
    sys.exit(1)

CONN_STR = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=priism-sql-poc.database.windows.net;"
    "Database=priism-db;"
    "Uid=priismadmin;"
    "Pwd=H052026Fl13r&&;"
    "Encrypt=yes;"
    "TrustServerCertificate=no"
)

ORG_ID = "b7d41f9f-7f15-49b2-8e3b-5850025e970f"

DEPT_MAP = {
    "College Of Agriculture": "CA",
    "College Of Veterinery Medicine": "CVM",
    "College Of Business Administration": "BA",
    "College Of Law": "CL",
    "College of Computing and Intelligent Systems": "CS",
    "College Of Arts, Humanities, And Social Sciences": "LA",
    "Center Excellence in Education & Learning": "COE",
    "Skills Development Center": "SP",
    "Vice Chancellor of Academic Affairs": "VCA",
    "Vice Chancellor of Administration & Finance": "VCAF",
    "Vice Chancellor of Community Affairs": "VCCA",
    "Department of Admissions and Registrations": "AD",
    "Corporate Communications": "CD",
    "Human Resource": "HR",
    "Information Technology": "IT",
    "Department of Finance": "FN",
    "Department of Procurement": "PC",
    "Department of Library": "LB",
    "Facility Management": "FM",
    "Institutional Effectiveness": "IEA",
    "Strategy & Institutional Development": "SI",
    "Deanship of Scientific Research & Innovation": "RI",
    "Office for Industry Partnership (OIP)": "OIP",
    "Office of Legal Affairs": "OLA",
    "Office of Internal Unit": "IU",
    "Student Affairs": "SA",
}

EXCEL_DATE_ORIGIN = date(1899, 12, 30)

SKIP_SENTINELS = {"", "nan", "tbd", "n/a", "none", "-", "–", "—"}


def safe_str(val, default=None):
    if val is None:
        return default
    s = str(val).strip()
    if s.lower() in SKIP_SENTINELS:
        return default
    return s


def parse_date(val):
    if val is None:
        return None
    # pandas Timestamp
    if hasattr(val, "date"):
        return val.date()
    s = str(val).strip()
    if s.lower() in SKIP_SENTINELS:
        return None
    # Excel serial number
    try:
        n = float(s)
        if n > 1000:
            return EXCEL_DATE_ORIGIN + timedelta(days=int(n))
    except (ValueError, TypeError):
        pass
    # Common date string formats
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d %b %Y"):
        try:
            from datetime import datetime
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


INSERT_SQL = """
INSERT INTO priism.aop_activities (
    activity_id, org_id, aop_id, sort_order,
    department_code, department_name,
    objective_text, core_process,
    activity_name, description,
    start_date, end_date, activity_kpi,
    manpower_requirement, procurement_description,
    inputs_required, outputs_to_deliver,
    budget_amount, budget_currency,
    status, completion_pct
) VALUES (
    ?, ?, ?, ?,
    ?, ?,
    ?, ?,
    ?, ?,
    ?, ?, ?,
    ?, ?,
    ?, ?,
    NULL, 'AED',
    'not_started', 0
)
"""


def main():
    if len(sys.argv) < 3:
        print("Usage: python seed_aop.py <excel_path> <aop_id>")
        sys.exit(1)

    excel_path = sys.argv[1]
    aop_id = sys.argv[2]

    print(f"Excel: {excel_path}")
    print(f"aop_id: {aop_id}")
    print(f"org_id: {ORG_ID}")

    print("Reading Excel...")
    df = pd.read_excel(excel_path, header=0)
    print(f"  {len(df)} rows loaded, columns: {list(df.columns)}")

    print("Connecting to Azure SQL...")
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    print("  Connected.")

    inserted = 0
    skipped = 0

    for i, row in df.iterrows():
        activity_name = safe_str(row.get("Operating Plan Activities"))
        if not activity_name or activity_name == "Operating Plan Activities":
            skipped += 1
            continue

        dept_raw = safe_str(row.get("Department/College"), "")
        dept_name = dept_raw.strip() if dept_raw else None
        dept_code = DEPT_MAP.get(dept_name or "", "OTHER")

        sort_order = row.get("S.N")
        try:
            sort_order = int(float(sort_order)) if sort_order is not None and str(sort_order).strip() not in ("", "nan") else None
        except (ValueError, TypeError):
            sort_order = None

        cursor.execute(INSERT_SQL, (
            str(uuid.uuid4()),
            ORG_ID,
            aop_id,
            sort_order,
            dept_code,
            dept_name,
            safe_str(row.get("Objective")),
            safe_str(row.get("Core Processes")),
            activity_name,
            safe_str(row.get("Operating Plan Activity Description")),
            parse_date(row.get("Start Date")),
            parse_date(row.get("End Date")),
            safe_str(row.get("Operating Plan Activity KPI")),
            safe_str(row.get("Additional Manpower Requirement & Justification")),
            safe_str(row.get("Procurement Requirement & Justification")),
            safe_str(row.get("Input Required")),
            safe_str(row.get("Output To Delivered")),
        ))
        inserted += 1

        if inserted % 50 == 0:
            conn.commit()
            print(f"  Inserted {inserted} rows...")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"\nDone. Inserted: {inserted}  Skipped: {skipped}")


if __name__ == "__main__":
    main()
