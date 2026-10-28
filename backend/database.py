import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

def get_db_connection():
    """Returns a SQLite connection with row factory enabled for dict-like access."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Creates all relational tables if they do not already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 1b. User Auth Tokens (Persistent Authentication Sessions across reloads)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_auth_tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 2. Career Profiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS career_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        target_role_id TEXT NOT NULL,
        experience_level TEXT DEFAULT 'Fresher',
        education TEXT DEFAULT 'Undergraduate',
        declared_skills_json TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 3. Assessments Table (Module 2: Per-Skill Assessment Definition)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        domain TEXT NOT NULL,
        duration_minutes INTEGER DEFAULT 90,
        total_mcq INTEGER DEFAULT 50,
        total_coding INTEGER DEFAULT 2,
        pass_percentage REAL DEFAULT 60.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Assessment Questions (50 MCQs + 2 Coding Problems per skill)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER,
        skill TEXT NOT NULL,
        question_num INTEGER NOT NULL,
        type TEXT NOT NULL, -- 'mcq' or 'coding'
        topic TEXT NOT NULL DEFAULT 'Core Concepts',
        difficulty TEXT NOT NULL, -- 'Easy', 'Medium', 'Hard'
        question_text TEXT NOT NULL,
        options_json TEXT, -- JSON array of string options for MCQs
        correct_option INTEGER, -- 0-3 index for MCQs
        problem_statement TEXT,
        input_format TEXT,
        output_format TEXT,
        constraints TEXT,
        code_template TEXT,
        function_name TEXT,
        class_name TEXT,
        schema_seed TEXT, -- In-memory SQLite schema creation & insert DDL for SQL challenges
        test_cases_json TEXT, -- JSON array of test cases
        explanation TEXT,
        UNIQUE(skill, question_num),
        FOREIGN KEY (assessment_id) REFERENCES assessments (id) ON DELETE CASCADE
    );
    """)

    # 5. Assessment Attempts (Module 2: Candidate Test Sessions)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_token TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        assessment_id INTEGER,
        skill_name TEXT NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        duration_minutes INTEGER DEFAULT 90,
        is_completed INTEGER DEFAULT 0,
        mcq_score REAL DEFAULT 0.0,
        programming_score REAL DEFAULT 0.0,
        total_score REAL DEFAULT 0.0,
        percentage REAL DEFAULT 0.0,
        integrity_score REAL DEFAULT 100.0,
        tab_switch_count INTEGER DEFAULT 0,
        blur_count INTEGER DEFAULT 0,
        copy_paste_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed', 'flagged', 'expired'
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (assessment_id) REFERENCES assessments (id)
    );
    """)

    # 6. Legacy assessment_sessions table for backwards compatibility
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_token TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        duration_minutes INTEGER DEFAULT 90,
        is_completed INTEGER DEFAULT 0,
        mcq_score REAL DEFAULT 0.0,
        coding_score REAL DEFAULT 0.0,
        total_score REAL DEFAULT 0.0,
        integrity_score REAL DEFAULT 100.0,
        tab_switch_count INTEGER DEFAULT 0,
        blur_count INTEGER DEFAULT 0,
        copy_paste_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'in_progress',
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 7. MCQ Answers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mcq_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        question_num INTEGER NOT NULL,
        selected_option INTEGER,
        is_correct INTEGER DEFAULT 0,
        score_awarded REAL DEFAULT 0.0,
        answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(attempt_id, question_id),
        FOREIGN KEY (attempt_id) REFERENCES assessment_attempts (id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES assessment_questions (id)
    );
    """)

    # 8. Programming Submissions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS programming_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        question_num INTEGER NOT NULL,
        submitted_code TEXT,
        language TEXT,
        test_cases_passed INTEGER DEFAULT 0,
        total_test_cases INTEGER DEFAULT 0,
        is_correct INTEGER DEFAULT 0,
        score_awarded REAL DEFAULT 0.0,
        status TEXT DEFAULT 'pending',
        execution_time_ms REAL DEFAULT 0.0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(attempt_id, question_id),
        FOREIGN KEY (attempt_id) REFERENCES assessment_attempts (id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES assessment_questions (id)
    );
    """)

    # 9. Legacy assessment_answers table for backwards compatibility
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        question_type TEXT NOT NULL,
        selected_option INTEGER,
        submitted_code TEXT,
        test_cases_passed INTEGER DEFAULT 0,
        total_test_cases INTEGER DEFAULT 0,
        is_correct INTEGER DEFAULT 0,
        score_awarded REAL DEFAULT 0.0,
        answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(session_id, question_id),
        FOREIGN KEY (session_id) REFERENCES assessment_sessions (id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES assessment_questions (id)
    );
    """)

    # 10. Integrity Events Table (Infraction Audit Trail)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS integrity_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        event_type TEXT NOT NULL, -- 'tab_switch', 'window_blur', 'copy_attempt', 'paste_attempt', 'cut_attempt', 'context_menu', 'shortcut_attempt'
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (attempt_id) REFERENCES assessment_attempts (id) ON DELETE CASCADE
    );
    """)

    # 11. Legacy assessment_violations table for backwards compatibility
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        violation_type TEXT NOT NULL,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES assessment_sessions (id) ON DELETE CASCADE
    );
    """)

    # 12. Assessment Results Table (Module 2 Granular Evaluation Record)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        mcq_score REAL NOT NULL,
        mcq_max REAL NOT NULL,
        programming_score REAL NOT NULL,
        programming_max REAL NOT NULL,
        total_score REAL NOT NULL,
        total_max REAL NOT NULL,
        percentage REAL NOT NULL,
        proficiency_level TEXT NOT NULL, -- 'Novice', 'Competent', 'Proficient', 'Expert'
        topic_scores_json TEXT NOT NULL,
        difficulty_scores_json TEXT NOT NULL,
        programming_details_json TEXT NOT NULL,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (attempt_id) REFERENCES assessment_attempts (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 13. Verified Skill Profiles (Module 3 handoff table)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verified_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_id INTEGER,
        attempt_id INTEGER,
        skill_name TEXT NOT NULL,
        category TEXT DEFAULT 'Technical Skill',
        score_pct REAL NOT NULL,
        proficiency_level TEXT NOT NULL, -- 'Beginner', 'Basic', 'Intermediate', 'Advanced', 'Expert'
        declared_level TEXT,             -- User-declared proficiency from career profile
        mcq_score REAL DEFAULT 0.0,
        mcq_max REAL DEFAULT 50.0,
        programming_score REAL DEFAULT 0.0,
        programming_max REAL DEFAULT 20.0,
        strengths_json TEXT,             -- Topic areas with >= 70% accuracy
        weaknesses_json TEXT,            -- Topic areas with < 70% accuracy
        comparison_status TEXT,          -- 'exceeded', 'matched', 'gap'
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 14. Job Roles & Market Demands
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_id TEXT UNIQUE NOT NULL,
        role_title TEXT NOT NULL,
        domain TEXT NOT NULL,
        market_demand_index INTEGER NOT NULL,
        demand_status TEXT NOT NULL,
        avg_salary TEXT NOT NULL,
        description TEXT NOT NULL
    );
    """)

    # 15. Role Required Skills
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_id TEXT NOT NULL,
        skill_name TEXT NOT NULL,
        category TEXT,
        importance_weight REAL NOT NULL,
        trend_status TEXT NOT NULL,
        min_proficiency TEXT NOT NULL,
        FOREIGN KEY (role_id) REFERENCES job_roles (role_id) ON DELETE CASCADE
    );
    """)

    # 16. Skill Gaps Analysis
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_gaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role_id TEXT NOT NULL,
        skill_name TEXT NOT NULL,
        category TEXT,
        required_level TEXT NOT NULL,
        verified_level TEXT NOT NULL,
        declared_level TEXT DEFAULT 'Not Declared',
        trend_status TEXT DEFAULT 'stable',
        required_weight REAL NOT NULL,
        verified_weight REAL NOT NULL,
        gap_score REAL NOT NULL,
        priority TEXT NOT NULL,
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 16b. Job Market Postings (Module 4 Job-Market Skill Demand Analyzer)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_postings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT NOT NULL,
        target_role_id TEXT NOT NULL,
        company TEXT NOT NULL,
        industry TEXT NOT NULL,
        location TEXT NOT NULL,
        required_skills_json TEXT NOT NULL,
        experience_level TEXT NOT NULL,
        posting_date DATE NOT NULL,
        data_source TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (target_role_id) REFERENCES job_roles (role_id)
    );
    """)

    # 17. Micro Credentials
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS micro_credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        role_id TEXT NOT NULL,
        target_skill TEXT NOT NULL,
        title TEXT NOT NULL,
        estimated_hours INTEGER NOT NULL,
        badge_icon TEXT NOT NULL,
        learning_outcomes_json TEXT NOT NULL,
        modules_json TEXT NOT NULL,
        FOREIGN KEY (role_id) REFERENCES job_roles (role_id)
    );
    """)

    # 18. User Curriculums
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_curriculums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role_id TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        total_modules INTEGER DEFAULT 0,
        completed_modules INTEGER DEFAULT 0,
        adaptation_version INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 19. Curriculum Modules
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS curriculum_modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curriculum_id INTEGER NOT NULL,
        micro_credential_id INTEGER,
        module_order INTEGER NOT NULL,
        title TEXT NOT NULL,
        hours INTEGER DEFAULT 4,
        status TEXT DEFAULT 'pending',
        progress_pct INTEGER DEFAULT 0,
        completed_at TIMESTAMP,
        FOREIGN KEY (curriculum_id) REFERENCES user_curriculums (id) ON DELETE CASCADE,
        FOREIGN KEY (micro_credential_id) REFERENCES micro_credentials (id)
    );
    """)

    # 20. Job Readiness Metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_readiness (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        role_id TEXT NOT NULL,
        overall_readiness_pct REAL DEFAULT 0.0,
        role_match_pct REAL DEFAULT 0.0,
        gap_coverage_pct REAL DEFAULT 0.0,
        credentials_earned INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 21. User Micro-Credentials (Module 7: Digital Micro-Credential Records)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        credential_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        skill TEXT NOT NULL,
        domain TEXT NOT NULL,
        level TEXT NOT NULL,
        learning_objectives_json TEXT NOT NULL,
        requirements_json TEXT NOT NULL,
        modules_completed_json TEXT NOT NULL,
        assessment_score REAL DEFAULT 0.0,
        practical_task TEXT NOT NULL,
        completion_pct REAL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'in_progress',
        issue_date TIMESTAMP,
        verification_status TEXT DEFAULT 'Verified (Platform Generated)',
        verification_code TEXT UNIQUE,
        accreditation_disclaimer TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 22. Skill Assessment History (Module 8: Historical Assessment Results Preservation)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_assessment_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        attempt_id INTEGER,
        attempt_number INTEGER NOT NULL DEFAULT 1,
        score_pct REAL NOT NULL,
        proficiency_level TEXT NOT NULL,
        mcq_score REAL DEFAULT 0.0,
        programming_score REAL DEFAULT 0.0,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 23. Learning Path Adaptations (Module 8: Adaptive Learning Path & Audit Log)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_path_adaptations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role_id TEXT NOT NULL,
        curriculum_id INTEGER,
        version INTEGER DEFAULT 1,
        trigger_reason TEXT NOT NULL, -- 'reassessment', 'progress_completed', 'market_demand_shift', 'manual_trigger'
        banner_message TEXT DEFAULT 'YOUR LEARNING PATH HAS BEEN UPDATED',
        explanations_json TEXT NOT NULL DEFAULT '[]',
        before_vs_after_json TEXT NOT NULL DEFAULT '[]',
        pruned_modules_json TEXT NOT NULL DEFAULT '[]',
        added_modules_json TEXT NOT NULL DEFAULT '[]',
        completed_skills_json TEXT NOT NULL DEFAULT '[]',
        recommended_next_json TEXT NOT NULL DEFAULT '[]',
        adapted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Safe column migration for existing assessment_questions table
    try:
        cursor.execute("ALTER TABLE assessment_questions ADD COLUMN schema_seed TEXT")
    except Exception:
        pass

    # Safe column migrations for Module 3 verified_skills table
    for col, col_type in [
        ("declared_level", "TEXT"),
        ("mcq_score", "REAL DEFAULT 0.0"),
        ("mcq_max", "REAL DEFAULT 50.0"),
        ("programming_score", "REAL DEFAULT 0.0"),
        ("programming_max", "REAL DEFAULT 20.0"),
        ("strengths_json", "TEXT"),
        ("weaknesses_json", "TEXT"),
        ("comparison_status", "TEXT")
    ]:
        try:
            cursor.execute(f"ALTER TABLE verified_skills ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # Safe column migrations for Module 4 & 5 skill_gaps table
    for col, col_type in [
        ("category", "TEXT"),
        ("declared_level", "TEXT DEFAULT 'Not Declared'"),
        ("trend_status", "TEXT DEFAULT 'stable'")
    ]:
        try:
            cursor.execute(f"ALTER TABLE skill_gaps ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # Safe column migrations for Module 6 user_curriculums table
    for col, col_type in [
        ("weekly_hours", "INTEGER DEFAULT 10"),
        ("preferred_difficulty", "TEXT DEFAULT 'Adaptive'"),
        ("learning_preferences", "TEXT DEFAULT 'Hands-on Projects'"),
        ("estimated_weeks", "INTEGER DEFAULT 6")
    ]:
        try:
            cursor.execute(f"ALTER TABLE user_curriculums ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # Safe column migrations for Module 6 curriculum_modules table
    for col, col_type in [
        ("skill_name", "TEXT"),
        ("current_proficiency", "TEXT DEFAULT 'Not Assessed'"),
        ("required_proficiency", "TEXT DEFAULT 'Intermediate'"),
        ("difficulty", "TEXT DEFAULT 'Intermediate'"),
        ("learning_objective", "TEXT"),
        ("prerequisites_json", "TEXT"),
        ("topics_json", "TEXT"),
        ("resources_json", "TEXT"),
        ("practice_json", "TEXT"),
        ("assessment_info", "TEXT"),
        ("project_task", "TEXT"),
        ("details_json", "TEXT"),
        ("is_unlocked", "INTEGER DEFAULT 1")
    ]:
        try:
            cursor.execute(f"ALTER TABLE curriculum_modules ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # Safe column migrations for Module 9 job_readiness table
    for col, col_type in [
        ("skill_coverage_pct", "REAL DEFAULT 0.0"),
        ("details_json", "TEXT")
    ]:
        try:
            cursor.execute(f"ALTER TABLE job_readiness ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # Backfill historical assessment records from assessment_results if table empty
    try:
        cursor.execute("SELECT COUNT(*) as cnt FROM skill_assessment_history")
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute("""
            INSERT INTO skill_assessment_history (user_id, skill_name, attempt_id, attempt_number, score_pct, proficiency_level, mcq_score, programming_score, evaluated_at)
            SELECT user_id, skill_name, attempt_id, 1, percentage, proficiency_level, mcq_score, programming_score, evaluated_at
            FROM assessment_results
            ORDER BY id ASC
            """)
    except Exception:
        pass

    conn.commit()
    conn.close()
    print("Database tables initialized successfully with Modules 1 through 9 models.")

if __name__ == "__main__":
    init_db()
