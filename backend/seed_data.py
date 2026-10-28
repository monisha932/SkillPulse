import os
import json
import sqlite3
import hashlib
from backend.database import get_db_connection, init_db

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 with a salt for secure persistence."""
    salt = "s5_micro_credential_salt"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def seed_database():
    """Initializes tables and seeds question bank, market roles, assessments, and default user."""
    print("Step 1: Initializing database tables...")
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Seed Demo User
    print("Step 2: Checking/Seeding demo student account...")
    demo_email = "student@example.com"
    cursor.execute("SELECT id FROM users WHERE email = ?", (demo_email,))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        hashed_pwd = hash_password("password123")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ("Monisha & Pooja (IT Batch)", demo_email, hashed_pwd, "student")
        )
        user_id = cursor.lastrowid
        print(f"Created demo student account (id={user_id}, email={demo_email}).")
    else:
        user_id = existing_user["id"]
        print(f"Demo student account already exists (id={user_id}).")

    # 2. Seed Assessments Definitions
    print("Step 3: Seeding Module 2 assessments for declared skills...")
    skill_definitions = [
        {"skill_name": "Python", "title": "Python Core & Advanced Technical Assessment", "domain": "Software & Backend Engineering"},
        {"skill_name": "SQL", "title": "Relational Database & SQL Proficiency Assessment", "domain": "Database Engineering"},
        {"skill_name": "Java", "title": "Java Standard Edition & OOP Technical Assessment", "domain": "Enterprise Software Engineering"}
    ]
    for s_def in skill_definitions:
        cursor.execute("SELECT id FROM assessments WHERE skill_name = ?", (s_def["skill_name"],))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO assessments (skill_name, title, domain, duration_minutes, total_mcq, total_coding)
            VALUES (?, ?, ?, 90, 50, 2)
            """, (s_def["skill_name"], s_def["title"], s_def["domain"]))

    # 3. Seed Skill Question Banks (Python, SQL, Java)
    print("Step 4: Seeding 50 MCQs + 2 Coding Problems per skill...")
    skill_banks_path = os.path.join(os.path.dirname(__file__), "data", "skill_banks.json")
    if os.path.exists(skill_banks_path):
        with open(skill_banks_path, "r", encoding="utf-8") as f:
            banks_data = json.load(f)

        for skill_name, s_data in banks_data.items():
            cursor.execute("SELECT id FROM assessments WHERE skill_name = ?", (skill_name,))
            ass_row = cursor.fetchone()
            ass_id = ass_row["id"] if ass_row else None

            # Insert MCQs
            for q in s_data.get("mcqs", []):
                cursor.execute("SELECT id FROM assessment_questions WHERE skill = ? AND question_num = ?", (skill_name, q["id"]))
                if not cursor.fetchone():
                    cursor.execute("""
                    INSERT INTO assessment_questions (
                        assessment_id, skill, question_num, type, topic, difficulty,
                        question_text, options_json, correct_option, explanation
                    ) VALUES (?, ?, ?, 'mcq', ?, ?, ?, ?, ?, ?)
                    """, (
                        ass_id, skill_name, q["id"], q.get("topic", "Core Concepts"), q["difficulty"],
                        q["question"], json.dumps(q["options"]), q["correct_option"], q.get("explanation", "")
                    ))

            # Insert Coding Problems
            for cq in s_data.get("coding", []):
                cursor.execute("SELECT id FROM assessment_questions WHERE skill = ? AND question_num = ?", (skill_name, cq["id"]))
                existing_q = cursor.fetchone()
                if not existing_q:
                    cursor.execute("""
                    INSERT INTO assessment_questions (
                        assessment_id, skill, question_num, type, topic, difficulty,
                        question_text, problem_statement, input_format, output_format, constraints,
                        code_template, function_name, class_name, schema_seed, test_cases_json
                    ) VALUES (?, ?, ?, 'coding', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ass_id, skill_name, cq["id"], cq.get("topic", "Problem Solving"), cq["difficulty"],
                        cq["title"], cq["problem_statement"], cq.get("input_format", ""), cq.get("output_format", ""),
                        cq.get("constraints", ""), cq.get("code_template", ""), cq.get("function_name", "solution"),
                        cq.get("class_name", "Solution"), cq.get("schema_seed", ""), json.dumps(cq.get("test_cases", []))
                    ))
                else:
                    cursor.execute("""
                    UPDATE assessment_questions
                    SET schema_seed = ?, test_cases_json = ?, code_template = ?, problem_statement = ?
                    WHERE skill = ? AND question_num = ? AND type = 'coding'
                    """, (
                        cq.get("schema_seed", ""), json.dumps(cq.get("test_cases", [])),
                        cq.get("code_template", ""), cq.get("problem_statement", ""),
                        skill_name, cq["id"]
                    ))

    # Also ensure backwards compatibility: if skill = 'Python', mirror legacy questions 1-52
    cursor.execute("SELECT COUNT(*) as cnt FROM assessment_questions")
    total_q = cursor.fetchone()["cnt"]
    print(f"Total assessment questions loaded across all skills: {total_q}")

    # 4. Seed Job Market Roles, Skills & Micro Credentials
    print("Step 5: Seeding market roles, required skills & micro-credentials...")
    m_file = os.path.join(os.path.dirname(__file__), "data", "market_postings.json")
    if os.path.exists(m_file):
        with open(m_file, "r", encoding="utf-8") as f:
            m_data = json.load(f)

        for role in m_data["roles"]:
            cursor.execute("SELECT id FROM job_roles WHERE role_id = ?", (role["role_id"],))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO job_roles (
                    role_id, role_title, domain, market_demand_index,
                    demand_status, avg_salary, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    role["role_id"], role["role_title"], role["domain"],
                    role["market_demand_index"], role["demand_status"],
                    role["average_salary_usd"], role["description"]
                ))
                
            # Insert or update skills for role
            for s in role["required_skills"]:
                cursor.execute("""
                SELECT id FROM role_skills WHERE role_id = ? AND LOWER(skill_name) = LOWER(?)
                """, (role["role_id"], s["name"]))
                existing_rs = cursor.fetchone()
                if not existing_rs:
                    cursor.execute("""
                    INSERT INTO role_skills (
                        role_id, skill_name, category, importance_weight, trend_status, min_proficiency
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        role["role_id"], s["name"], s.get("category", "Core"),
                        s["importance_weight"], s["trend"], s["min_proficiency"]
                    ))
                else:
                    cursor.execute("""
                    UPDATE role_skills
                    SET category = ?, importance_weight = ?, trend_status = ?, min_proficiency = ?
                    WHERE id = ?
                    """, (
                        s.get("category", "Core"), s["importance_weight"], s["trend"], s["min_proficiency"],
                        existing_rs["id"]
                    ))

            # Insert micro credentials
            for mc in role.get("micro_credentials", []):
                cursor.execute("SELECT id FROM micro_credentials WHERE code = ?", (mc["code"],))
                if not cursor.fetchone():
                    cursor.execute("""
                    INSERT INTO micro_credentials (
                        code, role_id, target_skill, title, estimated_hours, badge_icon,
                        learning_outcomes_json, modules_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        mc["code"], role["role_id"], mc["target_skill"], mc["title"],
                        mc["estimated_hours"], mc["badge_icon"],
                        json.dumps(mc["learning_outcomes"]), json.dumps(mc["modules"])
                    ))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
