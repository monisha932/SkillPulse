import os
import csv
import json
import io
from datetime import datetime
from collections import Counter
from backend.database import get_db_connection

def seed_default_job_postings_if_empty():
    """Seeds initial curated job postings if the table is empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_postings")
    count = cursor.fetchone()[0]
    if count == 0:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "seed_job_postings.csv")
        if os.path.exists(csv_path):
            with open(csv_path, "r", encoding="utf-8") as f:
                import_csv_postings(f.read(), data_source="Curated Tech Dataset 2026")
    conn.close()

def import_job_postings(postings: list, data_source: str = "API Import") -> dict:
    """
    Inserts a list of job posting dictionaries into job_postings table.
    Validates required fields and normalizes required_skills into JSON array.
    """
    if not isinstance(postings, list) or len(postings) == 0:
        return {"success": False, "imported_count": 0, "message": "No postings provided."}

    conn = get_db_connection()
    cursor = conn.cursor()
    imported = 0
    errors = []

    for idx, p in enumerate(postings):
        try:
            job_title = (p.get("job_title") or "").strip()
            target_role_id = (p.get("target_role_id") or "").strip().lower()
            company = (p.get("company") or "").strip()
            industry = (p.get("industry") or "Technology").strip()
            location = (p.get("location") or "Remote").strip()
            exp_level = (p.get("experience_level") or "Mid Level").strip()
            posting_date = (p.get("posting_date") or datetime.now().strftime("%Y-%m-%d")).strip()
            src = (p.get("data_source") or data_source).strip()

            if not job_title or not target_role_id or not company:
                errors.append(f"Row {idx + 1}: Missing job_title, target_role_id, or company.")
                continue

            # Parse required_skills into normalized list
            skills_raw = p.get("required_skills", [])
            if isinstance(skills_raw, str):
                # Split by semicolon or comma
                delimiter = ";" if ";" in skills_raw else ","
                skills_list = [s.strip() for s in skills_raw.split(delimiter) if s.strip()]
            elif isinstance(skills_raw, list):
                skills_list = [str(s).strip() for s in skills_raw if str(s).strip()]
            else:
                skills_list = []

            skills_json = json.dumps(skills_list)

            cursor.execute("""
            INSERT INTO job_postings (
                job_title, target_role_id, company, industry, location,
                required_skills_json, experience_level, posting_date, data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_title, target_role_id, company, industry, location,
                skills_json, exp_level, posting_date, src
            ))
            imported += 1
        except Exception as e:
            errors.append(f"Row {idx + 1}: {str(e)}")

    conn.commit()
    conn.close()

    return {
        "success": imported > 0,
        "imported_count": imported,
        "failed_count": len(errors),
        "errors": errors[:10]
    }

def import_csv_postings(csv_content: str, data_source: str = "Admin Upload CSV") -> dict:
    """
    Parses CSV string and imports job postings.
    Expected headers: job_title, target_role_id, company, industry, location, required_skills, experience_level, posting_date, data_source
    """
    if not csv_content or not csv_content.strip():
        return {"success": False, "imported_count": 0, "message": "CSV content is empty."}

    f = io.StringIO(csv_content.strip())
    reader = csv.DictReader(f)
    postings = []
    for row in reader:
        # Standardize keys (strip whitespace, lowercase)
        normalized_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
        postings.append({
            "job_title": normalized_row.get("job_title", ""),
            "target_role_id": normalized_row.get("target_role_id", "fullstack-dev"),
            "company": normalized_row.get("company", "Tech Corp"),
            "industry": normalized_row.get("industry", "Technology"),
            "location": normalized_row.get("location", "Remote"),
            "required_skills": normalized_row.get("required_skills", ""),
            "experience_level": normalized_row.get("experience_level", "Mid Level"),
            "posting_date": normalized_row.get("posting_date", datetime.now().strftime("%Y-%m-%d")),
            "data_source": normalized_row.get("data_source", data_source)
        })

    return import_job_postings(postings, data_source=data_source)

def categorize_skill(skill_name: str) -> str:
    """Heuristic categorizer for skill distribution chart."""
    s = skill_name.lower()
    if s in ["javascript", "typescript", "python", "java", "c++", "go", "ruby", "c#", "rust", "php"]:
        return "Programming Languages"
    elif s in ["react", "vue", "angular", "node.js", "express", "django", "fastapi", "spring", "flask", "next.js"]:
        return "Frameworks & Runtimes"
    elif s in ["sql", "postgresql", "mysql", "mongodb", "redis", "cassandra", "snowflake", "sqlite"]:
        return "Databases & Storage"
    elif s in ["docker", "kubernetes", "aws", "gcp", "azure", "linux", "terraform", "ci/cd", "bash", "git"]:
        return "DevOps & Cloud Tools"
    elif s in ["html/css", "rest api", "graphql", "microservices", "system design", "grpc"]:
        return "Architecture & Web Standards"
    elif s in ["machine learning", "deep learning", "pytorch", "tensorflow", "nlp", "computer vision", "mlops"]:
        return "AI & Machine Learning"
    else:
        return "Core Software Engineering"

def analyze_target_role_skills(
    target_role_id: str,
    industry: str = None,
    location: str = None,
    experience_level: str = None
) -> dict:
    """
    Module 4 Core Analytical Engine:
    Calculates for the selected target role:
    1. Most frequently requested skills & exact frequencies
    2. Skill demand percentage: (postings with skill / total role postings) * 100
    3. Industry distribution
    4. Location distribution
    5. Experience level distribution
    6. Trending skills & category distributions
    """
    seed_default_job_postings_if_empty()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get target role metadata
    cursor.execute("SELECT * FROM job_roles WHERE LOWER(role_id) = LOWER(?)", (target_role_id,))
    role_row = cursor.fetchone()
    if not role_row:
        # Fallback to fullstack-dev
        cursor.execute("SELECT * FROM job_roles WHERE role_id = 'fullstack-dev'")
        role_row = cursor.fetchone()

    active_role_id = role_row["role_id"] if role_row else target_role_id

    # Build query with optional filters
    query = "SELECT * FROM job_postings WHERE LOWER(target_role_id) = LOWER(?)"
    params = [active_role_id]

    if industry and isinstance(industry, str) and industry.strip().lower() != "all":
        query += " AND LOWER(industry) = LOWER(?)"
        params.append(industry.strip())

    if location and isinstance(location, str) and location.strip().lower() != "all":
        if location.strip().lower() == "remote":
            query += " AND LOWER(location) LIKE '%remote%'"
        else:
            query += " AND LOWER(location) = LOWER(?)"
            params.append(location.strip())

    if experience_level and isinstance(experience_level, str) and experience_level.strip().lower() != "all":
        query += " AND LOWER(experience_level) = LOWER(?)"
        params.append(experience_level.strip())

    query += " ORDER BY posting_date DESC"

    cursor.execute(query, params)
    postings = cursor.fetchall()

    total_postings = len(postings)
    if total_postings == 0:
        # If filtered too strictly, count base postings for role
        cursor.execute("SELECT COUNT(*) FROM job_postings WHERE LOWER(target_role_id) = LOWER(?)", (active_role_id,))
        base_count = cursor.fetchone()[0]
        conn.close()
        return {
            "target_role": {
                "role_id": role_row["role_id"],
                "role_title": role_row["role_title"],
                "domain": role_row["domain"]
            },
            "total_postings_analyzed": 0,
            "base_role_postings_count": base_count,
            "message": "No postings match the current filter criteria.",
            "skills": [],
            "top_skills": [],
            "industry_distribution": {},
            "location_distribution": {},
            "experience_distribution": {},
            "category_distribution": {},
            "data_sources": []
        }

    skill_counter = Counter()
    industry_counter = Counter()
    location_counter = Counter()
    experience_counter = Counter()
    data_sources = set()

    for p in postings:
        industry_counter[p["industry"]] += 1
        location_counter[p["location"]] += 1
        experience_counter[p["experience_level"]] += 1
        data_sources.add(p["data_source"])

        try:
            skills = json.loads(p["required_skills_json"])
            for s in skills:
                if s and s.strip():
                    skill_counter[s.strip()] += 1
        except Exception:
            pass

    # Calculate skill frequency and demand percentage
    skills_analyzed = []
    category_counter = Counter()

    for skill_name, freq in skill_counter.most_common():
        demand_pct = round((freq / total_postings) * 100.0, 1)
        cat = categorize_skill(skill_name)
        category_counter[cat] += freq
        is_trending = (demand_pct >= 50.0)

        skills_analyzed.append({
            "skill_name": skill_name,
            "frequency": freq,
            "demand_percentage": demand_pct,
            "category": cat,
            "is_trending": is_trending,
            "status": "Surging" if demand_pct >= 75 else "High Demand" if demand_pct >= 50 else "Moderate Demand"
        })

    # Industry distribution percentages
    ind_dist = [
        {"industry": ind, "count": cnt, "percentage": round((cnt / total_postings) * 100.0, 1)}
        for ind, cnt in industry_counter.most_common(6)
    ]

    # Location distribution
    loc_dist = [
        {"location": loc, "count": cnt, "percentage": round((cnt / total_postings) * 100.0, 1)}
        for loc, cnt in location_counter.most_common(6)
    ]

    # Experience level distribution
    exp_dist = [
        {"level": lvl, "count": cnt, "percentage": round((cnt / total_postings) * 100.0, 1)}
        for lvl, cnt in experience_counter.most_common()
    ]

    # Category distribution for chart
    total_skill_mentions = sum(category_counter.values()) or 1
    cat_dist = [
        {"category": cat, "count": cnt, "percentage": round((cnt / total_skill_mentions) * 100.0, 1)}
        for cat, cnt in category_counter.most_common()
    ]

    conn.close()

    return {
        "target_role": {
            "role_id": role_row["role_id"],
            "role_title": role_row["role_title"],
            "domain": role_row["domain"],
            "market_demand_index": role_row["market_demand_index"],
            "demand_status": role_row["demand_status"],
            "avg_salary": role_row["avg_salary"],
            "description": role_row["description"]
        },
        "total_postings_analyzed": total_postings,
        "skills": skills_analyzed,
        "top_skills": skills_analyzed[:10],
        "trending_skills": [s for s in skills_analyzed if s["is_trending"]][:8],
        "industry_distribution": ind_dist,
        "location_distribution": loc_dist,
        "experience_distribution": exp_dist,
        "category_distribution": cat_dist,
        "data_sources": list(data_sources),
        "as_of_date": datetime.now().strftime("%Y-%m-%d")
    }

def get_market_filters(target_role_id: str = None) -> dict:
    """Returns available industries, locations, and experience levels for filtering."""
    seed_default_job_postings_if_empty()
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT DISTINCT industry FROM job_postings"
    loc_query = "SELECT DISTINCT location FROM job_postings"
    exp_query = "SELECT DISTINCT experience_level FROM job_postings"

    if target_role_id:
        cursor.execute(query + " WHERE LOWER(target_role_id) = LOWER(?) ORDER BY industry", (target_role_id,))
        industries = [r[0] for r in cursor.fetchall() if r[0]]
        cursor.execute(loc_query + " WHERE LOWER(target_role_id) = LOWER(?) ORDER BY location", (target_role_id,))
        locations = [r[0] for r in cursor.fetchall() if r[0]]
    else:
        cursor.execute(query + " ORDER BY industry")
        industries = [r[0] for r in cursor.fetchall() if r[0]]
        cursor.execute(loc_query + " ORDER BY location")
        locations = [r[0] for r in cursor.fetchall() if r[0]]

    cursor.execute(exp_query + " ORDER BY experience_level")
    exp_levels = [r[0] for r in cursor.fetchall() if r[0]]

    conn.close()

    return {
        "industries": industries,
        "locations": locations,
        "experience_levels": exp_levels
    }
