import re
import pandas as pd

KEYWORD_RULES = {
    "Highly Confidential": {
        "score": 90,
        "keywords": [
            "medical", "health", "diagnosis", "disease", "blood_group",
            "medication", "biometric", "password", "bank_account",
            "account_number", "financial", "aadhaar", "pan",
            "emergency_contact"
        ],
        "usage": "Authorized personnel only"
    },
    "Confidential": {
        "score": 65,
        "keywords": [
            "email", "phone", "mobile", "address", "dob", "date_of_birth",
            "full_name", "name", "cgpa", "marks", "grade", "scholarship",
            "fee", "salary", "placement_package", "counselling"
        ],
        "usage": "Restricted access / approved analytics"
    },
    "Internal": {
        "score": 35,
        "keywords": [
            "student_id", "record_id", "employee_id", "attendance",
            "department", "course_code", "semester", "hostel",
            "transport", "advisor", "placement_status"
        ],
        "usage": "Institutional / internal use"
    },
    "Public": {
        "score": 10,
        "keywords": [
            "department_name", "program_name", "course_title",
            "campus", "event_name", "event_status"
        ],
        "usage": "General sharing / public analytics"
    }
}

def normalize(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")

def keyword_matches(column, keyword):
    # Match complete underscore-separated terms, avoiding false matches such as
    # 'name' inside 'program_name' when a more specific rule exists.
    col = normalize(column)
    key = normalize(keyword)
    return col == key or key in col.split("_")

def classify_column(column, series):
    col = normalize(column)
    non_null = series.dropna().astype(str)

    for level in ["Highly Confidential", "Confidential", "Internal", "Public"]:
        for keyword in KEYWORD_RULES[level]["keywords"]:
            if keyword_matches(col, keyword):
                return (
                    KEYWORD_RULES[level]["score"],
                    level,
                    KEYWORD_RULES[level]["usage"],
                    f"Matched sensitivity rule: {keyword}"
                )

    if len(non_null):
        email_ratio = non_null.str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$").mean()
        phone_ratio = non_null.str.match(r"^\d{10}$").mean()

        if email_ratio > 0.5:
            return 65, "Confidential", KEYWORD_RULES["Confidential"]["usage"], "Detected email pattern"

        if phone_ratio > 0.5:
            return 65, "Confidential", KEYWORD_RULES["Confidential"]["usage"], "Detected phone pattern"

    if pd.api.types.is_numeric_dtype(series):
        return 35, "Internal", KEYWORD_RULES["Internal"]["usage"], "Numeric institutional data fallback"

    return 35, "Internal", KEYWORD_RULES["Internal"]["usage"], "General institutional-data fallback"

def classify_dataset(df):
    rows = []
    for col in df.columns:
        score, level, usage, reason = classify_column(col, df[col])
        rows.append({
            "Column": col,
            "Data Type": str(df[col].dtype),
            "Missing": int(df[col].isna().sum()),
            "Sensitivity Score": score,
            "Classification": level,
            "Recommended Usage": usage,
            "Reason": reason
        })
    return pd.DataFrame(rows)
