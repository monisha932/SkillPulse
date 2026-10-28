import json
import secrets
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from backend.database import get_db_connection
from backend.routers.auth import get_current_user_id
from backend.models import (
    SkillAssessmentStartRequest,
    SaveAnswerRequest,
    RunCodeRequest,
    ViolationRequest,
    CompleteAssessmentRequest
)
from backend.services.code_evaluator import evaluate_code

router = APIRouter(prefix="/api/assessment", tags=["Module 2: Skill Assessment & Verification"])

@router.get("/skills")
def get_assessment_skills(user_id: int = Depends(get_current_user_id)):
    """
    Returns available technical skills configured for assessment (e.g., Python, SQL, Java),
    cross-referenced with candidate's declared profile skills.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get user declared skills
    cursor.execute("SELECT declared_skills_json FROM career_profiles WHERE user_id = ?", (user_id,))
    p_row = cursor.fetchone()
    declared_skills = []
    if p_row and p_row["declared_skills_json"]:
        declared_list = json.loads(p_row["declared_skills_json"])
        declared_skills = [s.get("skill_name") for s in declared_list if isinstance(s, dict)]

    # Fetch configured assessments
    cursor.execute("SELECT * FROM assessments ORDER BY id ASC")
    assessments = [dict(r) for r in cursor.fetchall()]

    # Fetch completed results for this user
    cursor.execute("""
    SELECT ar.skill_name, ar.percentage, ar.proficiency_level, ar.evaluated_at
    FROM assessment_results ar
    WHERE ar.user_id = ?
    ORDER BY ar.id DESC
    """, (user_id,))
    verified_records = {r["skill_name"].lower(): dict(r) for r in cursor.fetchall()}

    skills_data = []
    for ass in assessments:
        s_name = ass["skill_name"]
        verified = verified_records.get(s_name.lower())
        skills_data.append({
            "id": ass["id"],
            "skill_name": s_name,
            "title": ass["title"],
            "domain": ass["domain"],
            "duration_minutes": ass["duration_minutes"],
            "total_mcq": ass["total_mcq"],
            "total_coding": ass["total_coding"],
            "is_declared": any(s_name.lower() == d.lower() for d in declared_skills),
            "is_verified": bool(verified),
            "verified_percentage": verified["percentage"] if verified else None,
            "proficiency_level": verified["proficiency_level"] if verified else None,
            "verified_at": verified["evaluated_at"] if verified else None
        })

    conn.close()
    return {"success": True, "skills": skills_data}

@router.post("/start")
def start_assessment(req: Optional[SkillAssessmentStartRequest] = None, user_id: int = Depends(get_current_user_id)):
    """
    Module 2 Core: Initializes a 90-minute timed skill-specific assessment.
    Returns 50 MCQs (options A-D, topics, difficulty; correct answer hidden) and 2 Programming challenges.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Determine skill to assess
    skill_name = req.skill_name.strip() if (req and req.skill_name) else None
    if not skill_name:
        # Fallback: check user declared skills
        cursor.execute("SELECT declared_skills_json FROM career_profiles WHERE user_id = ?", (user_id,))
        p_row = cursor.fetchone()
        if p_row and p_row["declared_skills_json"]:
            decl = json.loads(p_row["declared_skills_json"])
            if decl and isinstance(decl, list) and len(decl) > 0:
                skill_name = decl[0].get("skill_name")
        if not skill_name:
            skill_name = "Python"

    # Normalize skill name (capitalize: Python, SQL, Java)
    cursor.execute("SELECT * FROM assessments WHERE LOWER(skill_name) = LOWER(?)", (skill_name,))
    ass_row = cursor.fetchone()
    if not ass_row:
        # Default to Python if skill not configured
        cursor.execute("SELECT * FROM assessments WHERE skill_name = 'Python'")
        ass_row = cursor.fetchone()
    
    skill_name = ass_row["skill_name"]
    ass_id = ass_row["id"]
    duration_mins = ass_row["duration_minutes"] or 90

    # Check for active uncompleted attempt for this user and skill
    cursor.execute("""
    SELECT id, session_token, start_time, duration_minutes, is_completed
    FROM assessment_attempts
    WHERE user_id = ? AND LOWER(skill_name) = LOWER(?) AND is_completed = 0
    ORDER BY id DESC LIMIT 1
    """, (user_id, skill_name))
    existing_attempt = cursor.fetchone()

    start_time = datetime.now()

    if existing_attempt:
        attempt_id = existing_attempt["id"]
        session_token = existing_attempt["session_token"]
        st = datetime.fromisoformat(existing_attempt["start_time"]) if isinstance(existing_attempt["start_time"], str) else existing_attempt["start_time"]
        elapsed = (datetime.now() - st).total_seconds()
        if elapsed > (duration_mins * 60):
            # Expired session -> close and create new
            cursor.execute("UPDATE assessment_attempts SET is_completed = 1, status = 'expired' WHERE id = ?", (attempt_id,))
            cursor.execute("UPDATE assessment_sessions SET is_completed = 1, status = 'expired' WHERE session_token = ?", (session_token,))
            
            session_token = secrets.token_hex(16)
            cursor.execute("""
            INSERT INTO assessment_attempts (session_token, user_id, assessment_id, skill_name, start_time, duration_minutes, is_completed, status)
            VALUES (?, ?, ?, ?, ?, ?, 0, 'in_progress')
            """, (session_token, user_id, ass_id, skill_name, start_time.isoformat(), duration_mins))
            attempt_id = cursor.lastrowid

            cursor.execute("""
            INSERT INTO assessment_sessions (session_token, user_id, start_time, duration_minutes, is_completed, status)
            VALUES (?, ?, ?, ?, 0, 'in_progress')
            """, (session_token, user_id, start_time.isoformat(), duration_mins))
    else:
        session_token = secrets.token_hex(16)
        cursor.execute("""
        INSERT INTO assessment_attempts (session_token, user_id, assessment_id, skill_name, start_time, duration_minutes, is_completed, status)
        VALUES (?, ?, ?, ?, ?, ?, 0, 'in_progress')
        """, (session_token, user_id, ass_id, skill_name, start_time.isoformat(), duration_mins))
        attempt_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO assessment_sessions (session_token, user_id, start_time, duration_minutes, is_completed, status)
        VALUES (?, ?, ?, ?, 0, 'in_progress')
        """, (session_token, user_id, start_time.isoformat(), duration_mins))
        conn.commit()

    # Retrieve all 50 MCQs for this skill (DO NOT expose correct_option)
    cursor.execute("""
    SELECT id, question_num, type, topic, difficulty, question_text, options_json
    FROM assessment_questions
    WHERE LOWER(skill) = LOWER(?) AND type = 'mcq'
    ORDER BY question_num ASC
    """, (skill_name,))
    mcq_rows = cursor.fetchall()
    mcq_list = []
    for r in mcq_rows:
        mcq_list.append({
            "id": r["id"],
            "question_num": r["question_num"],
            "type": "mcq",
            "topic": r["topic"],
            "difficulty": r["difficulty"],
            "question_text": r["question_text"],
            "options": json.loads(r["options_json"]) if r["options_json"] else []
        })

    # Retrieve 2 Programming questions for this skill (visible test cases only)
    cursor.execute("""
    SELECT id, question_num, type, topic, difficulty, question_text, problem_statement,
           input_format, output_format, constraints, code_template, function_name, class_name, test_cases_json
    FROM assessment_questions
    WHERE LOWER(skill) = LOWER(?) AND type = 'coding'
    ORDER BY question_num ASC
    """, (skill_name,))
    coding_rows = cursor.fetchall()
    coding_list = []
    for cr in coding_rows:
        all_tc = json.loads(cr["test_cases_json"]) if cr["test_cases_json"] else []
        visible_tc = [tc for tc in all_tc if not tc.get("is_hidden", False)]
        coding_list.append({
            "id": cr["id"],
            "question_num": cr["question_num"],
            "type": "coding",
            "topic": cr["topic"],
            "difficulty": cr["difficulty"],
            "title": cr["question_text"],
            "problem_statement": cr["problem_statement"],
            "input_format": cr["input_format"],
            "output_format": cr["output_format"],
            "constraints": cr["constraints"],
            "code_template": cr["code_template"],
            "function_name": cr["function_name"],
            "class_name": cr["class_name"] or "Solution",
            "language": skill_name.lower(),
            "visible_test_cases": visible_tc,
            "total_test_cases_count": len(all_tc)
        })

    # Retrieve already saved answers
    cursor.execute("""
    SELECT question_num, selected_option, 0 as is_coding
    FROM mcq_answers
    WHERE attempt_id = ?
    UNION ALL
    SELECT question_num, NULL as selected_option, 1 as is_coding
    FROM programming_submissions
    WHERE attempt_id = ?
    """, (attempt_id, attempt_id))
    saved_answers = {}

    # Read mcq_answers
    cursor.execute("SELECT question_num, selected_option FROM mcq_answers WHERE attempt_id = ?", (attempt_id,))
    for ma in cursor.fetchall():
        saved_answers[str(ma["question_num"])] = {
            "selected_option": ma["selected_option"],
            "submitted_code": None
        }

    # Read programming_submissions
    cursor.execute("SELECT question_num, submitted_code FROM programming_submissions WHERE attempt_id = ?", (attempt_id,))
    for ps in cursor.fetchall():
        qnum_str = str(ps["question_num"])
        if qnum_str in saved_answers:
            saved_answers[qnum_str]["submitted_code"] = ps["submitted_code"]
        else:
            saved_answers[qnum_str] = {
                "selected_option": None,
                "submitted_code": ps["submitted_code"]
            }

    conn.commit()
    conn.close()

    return {
        "success": True,
        "session_token": session_token,
        "skill_name": skill_name,
        "assessment_title": ass_row["title"],
        "duration_minutes": duration_mins,
        "total_mcqs": len(mcq_list),
        "total_coding": len(coding_list),
        "mcqs": mcq_list,
        "coding_questions": coding_list,
        "saved_answers": saved_answers
    }

@router.get("/session/{session_token}")
def get_session_status(session_token: str):
    """
    Returns live session state, remaining 90-minute countdown, and integrity metrics.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assessment_attempts WHERE session_token = ?", (session_token,))
    attempt = cursor.fetchone()
    if not attempt:
        # Fallback to assessment_sessions
        cursor.execute("SELECT * FROM assessment_sessions WHERE session_token = ?", (session_token,))
        attempt = cursor.fetchone()
        if not attempt:
            conn.close()
            raise HTTPException(status_code=404, detail="Assessment session not found.")

    st = datetime.fromisoformat(attempt["start_time"]) if isinstance(attempt["start_time"], str) else attempt["start_time"]
    elapsed_sec = (datetime.now() - st).total_seconds()
    total_sec = attempt["duration_minutes"] * 60
    remaining_sec = max(0, int(total_sec - elapsed_sec))
    is_expired = (remaining_sec == 0 and attempt["is_completed"] == 0)

    # Saved answers count
    att_id = attempt["id"]
    cursor.execute("SELECT COUNT(*) as mcq_cnt FROM mcq_answers WHERE attempt_id = ?", (att_id,))
    mcq_cnt = cursor.fetchone()["mcq_cnt"]
    cursor.execute("SELECT COUNT(*) as prog_cnt FROM programming_submissions WHERE attempt_id = ?", (att_id,))
    prog_cnt = cursor.fetchone()["prog_cnt"]

    conn.close()
    return {
        "session_id": attempt["id"],
        "skill_name": attempt["skill_name"] if "skill_name" in attempt.keys() else "Python",
        "is_completed": bool(attempt["is_completed"]),
        "status": attempt["status"],
        "duration_minutes": attempt["duration_minutes"],
        "remaining_seconds": remaining_sec,
        "is_expired": is_expired,
        "tab_switch_count": attempt["tab_switch_count"],
        "blur_count": attempt["blur_count"],
        "copy_paste_count": attempt["copy_paste_count"],
        "integrity_score": attempt["integrity_score"],
        "answered_count": mcq_cnt + prog_cnt
    }

@router.post("/save-answer")
def save_answer(req: SaveAnswerRequest):
    """
    Auto-saves candidate answer incrementally (MCQ option selection or programming code draft).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, user_id, skill_name, is_completed FROM assessment_attempts WHERE session_token = ?", (req.session_token,))
    attempt = cursor.fetchone()
    if not attempt:
        conn.close()
        raise HTTPException(status_code=404, detail="Invalid assessment session token.")

    if attempt["is_completed"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Assessment has already been completed.")

    attempt_id = attempt["id"]
    skill_name = attempt["skill_name"]

    cursor.execute("SELECT id, type FROM assessment_questions WHERE LOWER(skill) = LOWER(?) AND question_num = ?", (skill_name, req.question_num))
    q_row = cursor.fetchone()
    if not q_row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Question {req.question_num} for skill {skill_name} not found.")

    q_id = q_row["id"]
    q_type = q_row["type"]

    if q_type == "mcq":
        cursor.execute("""
        INSERT INTO mcq_answers (attempt_id, question_id, question_num, selected_option)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(attempt_id, question_id) DO UPDATE SET
            selected_option = excluded.selected_option,
            answered_at = CURRENT_TIMESTAMP
        """, (attempt_id, q_id, req.question_num, req.selected_option))
    else:
        cursor.execute("""
        INSERT INTO programming_submissions (attempt_id, question_id, question_num, submitted_code, language)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(attempt_id, question_id) DO UPDATE SET
            submitted_code = excluded.submitted_code,
            submitted_at = CURRENT_TIMESTAMP
        """, (attempt_id, q_id, req.question_num, req.submitted_code, skill_name.lower()))

    # Mirror to legacy table for backwards compatibility
    cursor.execute("SELECT id FROM assessment_sessions WHERE session_token = ?", (req.session_token,))
    sess_row = cursor.fetchone()
    if sess_row:
        cursor.execute("""
        INSERT INTO assessment_answers (session_id, question_id, question_type, selected_option, submitted_code)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(session_id, question_id) DO UPDATE SET
            selected_option = excluded.selected_option,
            submitted_code = excluded.submitted_code,
            answered_at = CURRENT_TIMESTAMP
        """, (sess_row["id"], q_id, q_type, req.selected_option, req.submitted_code))

    conn.commit()
    conn.close()
    return {"success": True, "question_num": req.question_num, "saved": True}

@router.post("/run-code")
def run_code_tests(req: RunCodeRequest):
    """
    Sandboxed code execution against visible sample test cases on demand.
    Supports Python, SQL, and Java.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, skill_name FROM assessment_attempts WHERE session_token = ?", (req.session_token,))
    attempt = cursor.fetchone()
    if not attempt:
        conn.close()
        raise HTTPException(status_code=404, detail="Invalid session token.")

    skill_name = attempt["skill_name"]
    cursor.execute("""
    SELECT id, function_name, class_name, test_cases_json, code_template, schema_seed
    FROM assessment_questions
    WHERE LOWER(skill) = LOWER(?) AND question_num = ? AND type = 'coding'
    """, (skill_name, req.question_num))
    q_row = cursor.fetchone()
    conn.close()

    if not q_row:
        raise HTTPException(status_code=404, detail="Coding challenge not found.")

    all_tc = json.loads(q_row["test_cases_json"]) if q_row["test_cases_json"] else []
    visible_tc = [tc for tc in all_tc if not tc.get("is_hidden", False)]

    # Run code through multi-language evaluation engine
    res = evaluate_code(
        submitted_code=req.code,
        function_name=q_row["function_name"] or "solution",
        test_cases=visible_tc,
        language=skill_name.lower(),
        class_name=q_row["class_name"] or "Solution",
        schema_seed=(q_row["schema_seed"] or "") if skill_name.lower() == "sql" else "",
        timeout_sec=4.0
    )
    return res

@router.post("/violation")
def log_violation(req: ViolationRequest):
    """
    Assessment Integrity Monitor:
    Logs browser focus-loss, tab switches, and clipboard restrictions into integrity_events table.
    Updates candidate's integrity score and flags session if tab switches exceed threshold (5).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, tab_switch_count, blur_count, copy_paste_count, integrity_score, status
    FROM assessment_attempts WHERE session_token = ?
    """, (req.session_token,))
    attempt = cursor.fetchone()
    if not attempt:
        conn.close()
        raise HTTPException(status_code=404, detail="Invalid session token.")

    attempt_id = attempt["id"]
    cursor.execute("""
    INSERT INTO integrity_events (attempt_id, event_type, details)
    VALUES (?, ?, ?)
    """, (attempt_id, req.violation_type, req.details))

    tab_cnt = attempt["tab_switch_count"]
    blur_cnt = attempt["blur_count"]
    cp_cnt = attempt["copy_paste_count"]
    current_integrity = attempt["integrity_score"]

    deduction = 0.0
    if req.violation_type == "tab_switch":
        tab_cnt += 1
        deduction = 5.0
    elif req.violation_type == "window_blur":
        blur_cnt += 1
        deduction = 2.0
    elif req.violation_type in ["copy_attempt", "paste_attempt", "cut_attempt", "context_menu", "shortcut_attempt"]:
        cp_cnt += 1
        deduction = 3.0

    new_integrity = max(0.0, current_integrity - deduction)
    status = "flagged" if tab_cnt >= 5 else attempt["status"]

    cursor.execute("""
    UPDATE assessment_attempts
    SET tab_switch_count = ?, blur_count = ?, copy_paste_count = ?, integrity_score = ?, status = ?
    WHERE id = ?
    """, (tab_cnt, blur_cnt, cp_cnt, new_integrity, status, attempt_id))

    # Mirror to legacy table
    cursor.execute("""
    UPDATE assessment_sessions
    SET tab_switch_count = ?, blur_count = ?, copy_paste_count = ?, integrity_score = ?, status = ?
    WHERE session_token = ?
    """, (tab_cnt, blur_cnt, cp_cnt, new_integrity, status, req.session_token))

    cursor.execute("""
    INSERT INTO assessment_violations (session_id, violation_type, details)
    SELECT id, ?, ? FROM assessment_sessions WHERE session_token = ?
    """, (req.violation_type, req.details, req.session_token))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "tab_switch_count": tab_cnt,
        "blur_count": blur_cnt,
        "copy_paste_count": cp_cnt,
        "integrity_score": new_integrity,
        "is_flagged": (tab_cnt >= 5)
    }

@router.post("/complete")
def complete_assessment(req: CompleteAssessmentRequest):
    """
    CRITICAL SECURITY REQUIREMENT: Backend-only secure scoring.
    Never trusts frontend values.
    1. Grades 50 MCQs against database keys.
    2. Executes 2 programming challenges against full test suites (visible + hidden).
    3. Calculates topic-wise breakdown, difficulty-wise performance, and test-case metrics.
    4. Records comprehensive evaluation in assessment_results table.
    5. Saves candidate verified skill level into verified_skills table for Module 3 handoff.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assessment_attempts WHERE session_token = ?", (req.session_token,))
    attempt = cursor.fetchone()
    if not attempt:
        conn.close()
        raise HTTPException(status_code=404, detail="Invalid session token.")

    attempt_id = attempt["id"]
    user_id = attempt["user_id"]
    skill_name = attempt["skill_name"]

    # 1. Evaluate 50 MCQs
    cursor.execute("""
    SELECT id, question_num, topic, difficulty, correct_option
    FROM assessment_questions
    WHERE LOWER(skill) = LOWER(?) AND type = 'mcq'
    ORDER BY question_num ASC
    """, (skill_name,))
    mcq_questions = cursor.fetchall()

    cursor.execute("SELECT question_id, selected_option FROM mcq_answers WHERE attempt_id = ?", (attempt_id,))
    user_mcq_answers = {r["question_id"]: r["selected_option"] for r in cursor.fetchall()}

    mcq_correct = 0
    topic_stats = {}      # topic -> { correct, total }
    difficulty_stats = {} # difficulty -> { correct, total }

    for q in mcq_questions:
        q_id = q["id"]
        q_num = q["question_num"]
        topic = q["topic"] or "General"
        diff = q["difficulty"] or "Medium"
        correct_opt = q["correct_option"]
        user_opt = user_mcq_answers.get(q_id)

        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0}
        topic_stats[topic]["total"] += 1

        if diff not in difficulty_stats:
            difficulty_stats[diff] = {"correct": 0, "total": 0}
        difficulty_stats[diff]["total"] += 1

        is_corr = (user_opt == correct_opt) if user_opt is not None else False
        if is_corr:
            mcq_correct += 1
            topic_stats[topic]["correct"] += 1
            difficulty_stats[diff]["correct"] += 1

        # Record grading in mcq_answers
        cursor.execute("""
        INSERT INTO mcq_answers (attempt_id, question_id, question_num, selected_option, is_correct, score_awarded)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(attempt_id, question_id) DO UPDATE SET
            is_correct = excluded.is_correct,
            score_awarded = excluded.score_awarded
        """, (attempt_id, q_id, q_num, user_opt, 1 if is_corr else 0, 1.0 if is_corr else 0.0))

    # Format topic and difficulty stats
    topic_scores = {
        k: {
            "correct": v["correct"],
            "total": v["total"],
            "percentage": round((v["correct"] / v["total"]) * 100.0, 1) if v["total"] > 0 else 0.0
        }
        for k, v in topic_stats.items()
    }

    difficulty_scores = {
        k: {
            "correct": v["correct"],
            "total": v["total"],
            "percentage": round((v["correct"] / v["total"]) * 100.0, 1) if v["total"] > 0 else 0.0
        }
        for k, v in difficulty_stats.items()
    }

    # 2. Evaluate 2 Programming Questions
    cursor.execute("""
    SELECT id, question_num, question_text, function_name, class_name, test_cases_json, code_template, schema_seed
    FROM assessment_questions
    WHERE LOWER(skill) = LOWER(?) AND type = 'coding'
    ORDER BY question_num ASC
    """, (skill_name,))
    coding_questions = cursor.fetchall()

    cursor.execute("SELECT question_id, submitted_code FROM programming_submissions WHERE attempt_id = ?", (attempt_id,))
    user_coding_answers = {r["question_id"]: r["submitted_code"] for r in cursor.fetchall()}

    coding_total_points = 0.0
    coding_max_points = len(coding_questions) * 10.0 # 10 pts per coding problem
    programming_details = []

    for cq in coding_questions:
        cq_id = cq["id"]
        cq_num = cq["question_num"]
        code = user_coding_answers.get(cq_id, "")
        all_tc = json.loads(cq["test_cases_json"]) if cq["test_cases_json"] else []

        eval_res = evaluate_code(
            submitted_code=code,
            function_name=cq["function_name"] or "solution",
            test_cases=all_tc,
            language=skill_name.lower(),
            class_name=cq["class_name"] or "Solution",
            schema_seed=(cq["schema_seed"] or "") if skill_name.lower() == "sql" else "",
            timeout_sec=4.0
        )

        passed = eval_res["passed_count"]
        total_tc = eval_res["total_count"]
        points = round((passed / total_tc) * 10.0, 1) if total_tc > 0 else 0.0
        coding_total_points += points

        programming_details.append({
            "question_num": cq_num,
            "title": cq["question_text"],
            "test_cases_passed": passed,
            "total_test_cases": total_tc,
            "score_awarded": points,
            "max_score": 10.0,
            "all_passed": eval_res["all_passed"],
            "execution_time_ms": eval_res.get("execution_time_ms", 0.0),
            "error": eval_res.get("error")
        })

        cursor.execute("""
        INSERT INTO programming_submissions (
            attempt_id, question_id, question_num, submitted_code, language,
            test_cases_passed, total_test_cases, is_correct, score_awarded, status, execution_time_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(attempt_id, question_id) DO UPDATE SET
            test_cases_passed = excluded.test_cases_passed,
            total_test_cases = excluded.total_test_cases,
            is_correct = excluded.is_correct,
            score_awarded = excluded.score_awarded,
            status = excluded.status,
            execution_time_ms = excluded.execution_time_ms
        """, (
            attempt_id, cq_id, cq_num, code, skill_name.lower(),
            passed, total_tc, 1 if eval_res["all_passed"] else 0, points,
            "evaluated", eval_res.get("execution_time_ms", 0.0)
        ))

    # 3. Overall Weighted Scoring
    # MCQ weight: 70%, Coding weight: 30%
    mcq_score_pct = round((mcq_correct / 50.0) * 100.0, 1) if len(mcq_questions) > 0 else 0.0
    coding_score_pct = round((coding_total_points / coding_max_points) * 100.0, 1) if coding_max_points > 0 else 0.0
    overall_pct = round((mcq_score_pct * 0.7) + (coding_score_pct * 0.3), 1)

    # Determine Verified Proficiency Tier (Module 3 Standard: 0-39 Beginner, 40-59 Basic, 60-74 Intermediate, 75-89 Advanced, 90-100 Expert)
    if overall_pct >= 90:
        prof_level = "Expert"
    elif overall_pct >= 75:
        prof_level = "Advanced"
    elif overall_pct >= 60:
        prof_level = "Intermediate"
    elif overall_pct >= 40:
        prof_level = "Basic"
    else:
        prof_level = "Beginner"

    # Analyze Topic-wise Strengths and Weaknesses
    strengths = []
    weaknesses = []
    for t_name, t_stat in topic_scores.items():
        item = {
            "topic": t_name,
            "correct": t_stat["correct"],
            "total": t_stat["total"],
            "percentage": t_stat["percentage"]
        }
        if t_stat["percentage"] >= 70.0:
            strengths.append(item)
        else:
            weaknesses.append(item)
    strengths.sort(key=lambda x: x["percentage"], reverse=True)
    weaknesses.sort(key=lambda x: x["percentage"])

    # Retrieve User-Declared Skill Rating from Career Profile for Clear Distinction
    cursor.execute("SELECT declared_skills_json FROM career_profiles WHERE user_id = ?", (user_id,))
    cp_row = cursor.fetchone()
    declared_level = "Not Declared"
    if cp_row and cp_row["declared_skills_json"]:
        try:
            decl_list = json.loads(cp_row["declared_skills_json"])
            for d in decl_list:
                if d.get("skill_name", "").lower() == skill_name.lower():
                    declared_level = d.get("self_rating") or "Intermediate"
                    break
        except Exception:
            pass

    # Compare Declared vs. Verified Proficiency Level
    tier_ranks = {
        "Beginner": 1,
        "Basic": 2,
        "Intermediate": 3,
        "Advanced": 4,
        "Expert": 5
    }
    d_rank = tier_ranks.get(declared_level, 0)
    v_rank = tier_ranks.get(prof_level, 0)
    if d_rank == 0:
        comparison_status = "unrated"
        comparison_label = f"Verified as {prof_level} (No Prior Self-Declaration)"
    elif v_rank > d_rank:
        diff = v_rank - d_rank
        comparison_status = "exceeded"
        comparison_label = f"Outperformed Declared Rating (+{diff} tier{'s' if diff > 1 else ''})"
    elif v_rank == d_rank:
        comparison_status = "matched"
        comparison_label = "Accurately Self-Assessed (Matched Rating)"
    else:
        diff = d_rank - v_rank
        comparison_status = "gap"
        comparison_label = f"Below Declared Rating (-{diff} tier{'s' if diff > 1 else ''})"

    # 4. Save into assessment_results table
    cursor.execute("""
    INSERT INTO assessment_results (
        attempt_id, user_id, skill_name, mcq_score, mcq_max, programming_score, programming_max,
        total_score, total_max, percentage, proficiency_level,
        topic_scores_json, difficulty_scores_json, programming_details_json
    ) VALUES (?, ?, ?, ?, 50.0, ?, ?, ?, 100.0, ?, ?, ?, ?, ?)
    ON CONFLICT(attempt_id) DO UPDATE SET
        mcq_score = excluded.mcq_score,
        programming_score = excluded.programming_score,
        total_score = excluded.total_score,
        percentage = excluded.percentage,
        proficiency_level = excluded.proficiency_level,
        topic_scores_json = excluded.topic_scores_json,
        difficulty_scores_json = excluded.difficulty_scores_json,
        programming_details_json = excluded.programming_details_json,
        evaluated_at = CURRENT_TIMESTAMP
    """, (
        attempt_id, user_id, skill_name, mcq_correct, coding_total_points, coding_max_points,
        overall_pct, overall_pct, prof_level,
        json.dumps(topic_scores), json.dumps(difficulty_scores), json.dumps(programming_details)
    ))

    # Update assessment_attempts
    end_time = datetime.now().isoformat()
    cursor.execute("""
    UPDATE assessment_attempts
    SET is_completed = 1, end_time = ?, mcq_score = ?, programming_score = ?,
        total_score = ?, percentage = ?, status = 'completed'
    WHERE id = ?
    """, (end_time, mcq_correct, coding_total_points, overall_pct, overall_pct, attempt_id))

    # Mirror to legacy assessment_sessions
    cursor.execute("""
    UPDATE assessment_sessions
    SET is_completed = 1, end_time = ?, mcq_score = ?, coding_score = ?,
        total_score = ?, status = 'completed'
    WHERE session_token = ?
    """, (end_time, mcq_score_pct, coding_score_pct, overall_pct, req.session_token))

    # 5. Store Verified Skill Result in Database for Module 3 and downstream modules
    cursor.execute("DELETE FROM verified_skills WHERE user_id = ? AND LOWER(skill_name) = LOWER(?)", (user_id, skill_name))
    cursor.execute("""
    INSERT INTO verified_skills (
        user_id, session_id, attempt_id, skill_name, category, score_pct, proficiency_level,
        declared_level, mcq_score, mcq_max, programming_score, programming_max,
        strengths_json, weaknesses_json, comparison_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, attempt_id, attempt_id, skill_name, "Technical Skill", overall_pct, prof_level,
        declared_level, mcq_correct, 50.0, coding_total_points, coding_max_points,
        json.dumps(strengths), json.dumps(weaknesses), comparison_status
    ))

    conn.commit()
    conn.close()

    # Module 8: Record assessment attempt in permanent history & trigger adaptive learning path
    adaptive_result = None
    try:
        from backend.services.adaptive_engine import record_assessment_attempt, adapt_learning_path
        record_assessment_attempt(
            user_id=user_id,
            skill_name=skill_name,
            attempt_id=attempt_id,
            score_pct=overall_pct,
            proficiency_level=prof_level,
            mcq_score=mcq_correct,
            programming_score=coding_total_points
        )
        adaptive_result = adapt_learning_path(user_id=user_id, trigger_reason="reassessment")
    except Exception as e:
        pass

    return {
        "success": True,
        "message": f"Module 2 Assessment for {skill_name} evaluated successfully!",
        "learning_path_updated": bool(adaptive_result),
        "adaptive_summary": adaptive_result.get("explanations", []) if adaptive_result else [],
        "results": {
            "attempt_id": attempt_id,
            "session_id": attempt_id,
            "skill_name": skill_name,
            "declared_skill": {
                "skill_name": skill_name,
                "declared_level": declared_level
            },
            "verified_skill": {
                "skill_name": skill_name,
                "score_pct": overall_pct,
                "proficiency_level": prof_level,
                "category": "Technical Skill"
            },
            "comparison": {
                "declared_level": declared_level,
                "verified_level": prof_level,
                "status": comparison_status,
                "label": comparison_label
            },
            "mcq_score": mcq_correct,
            "mcq_correct": mcq_correct,
            "mcq_total": 50,
            "mcq_score_pct": mcq_score_pct,
            "programming_score": coding_total_points,
            "coding_points": coding_total_points,
            "programming_max": coding_max_points,
            "coding_max_points": coding_max_points,
            "programming_score_pct": coding_score_pct,
            "coding_score_pct": coding_score_pct,
            "overall_total_pct": overall_pct,
            "proficiency_level": prof_level,
            "integrity_score": attempt["integrity_score"],
            "tab_switch_count": attempt["tab_switch_count"],
            "blur_count": attempt["blur_count"],
            "is_flagged": (attempt["tab_switch_count"] >= 5),
            "topic_scores": topic_scores,
            "difficulty_scores": difficulty_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "programming_details": programming_details,
            "verified_skills": [
                {
                    "skill_name": skill_name,
                    "category": "Technical Skill",
                    "score_pct": overall_pct,
                    "proficiency_level": prof_level
                }
            ]
        }
    }

@router.get("/verified-profile")
def get_verified_skill_profile(skill_name: Optional[str] = None, user_id: int = Depends(get_current_user_id)):
    """
    Module 3 Core Endpoint:
    Retrieves the candidate's latest Verified Skill Profile(s), displaying:
    1. Skill name (e.g. Python)
    2. Overall verified score
    3. Verified proficiency level (0-39 Beginner, 40-59 Basic, 60-74 Intermediate, 75-89 Advanced, 90-100 Expert)
    4. MCQ performance
    5. Programming performance
    6. Topic-wise strengths and weaknesses
    7. Distinction between User-declared skill and Assessment-verified skill
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT vs.*, ar.topic_scores_json, ar.difficulty_scores_json, ar.programming_details_json,
           ar.total_score, ar.total_max, ar.evaluated_at
    FROM verified_skills vs
    LEFT JOIN assessment_results ar ON vs.attempt_id = ar.attempt_id
    WHERE vs.user_id = ?
    """
    params = [user_id]

    if skill_name:
        query += " AND LOWER(vs.skill_name) = LOWER(?)"
        params.append(skill_name.strip())

    query += " ORDER BY vs.verified_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "success": True,
            "has_verified_profile": False,
            "profiles": [],
            "profile": None
        }

    profiles = []
    tier_ranks = {"Beginner": 1, "Basic": 2, "Intermediate": 3, "Advanced": 4, "Expert": 5}

    for r in rows:
        strengths = json.loads(r["strengths_json"]) if r["strengths_json"] else []
        weaknesses = json.loads(r["weaknesses_json"]) if r["weaknesses_json"] else []
        topic_scores = json.loads(r["topic_scores_json"]) if r["topic_scores_json"] else {}
        difficulty_scores = json.loads(r["difficulty_scores_json"]) if r["difficulty_scores_json"] else {}
        prog_details = json.loads(r["programming_details_json"]) if r["programming_details_json"] else []

        decl_lvl = r["declared_level"] or "Not Declared"
        prof_lvl = r["proficiency_level"]
        d_rank = tier_ranks.get(decl_lvl, 0)
        v_rank = tier_ranks.get(prof_lvl, 0)

        if d_rank == 0:
            status = "unrated"
            label = f"Verified as {prof_lvl} (No Prior Self-Declaration)"
        elif v_rank > d_rank:
            diff = v_rank - d_rank
            status = "exceeded"
            label = f"Outperformed Declared Rating (+{diff} tier{'s' if diff > 1 else ''})"
        elif v_rank == d_rank:
            status = "matched"
            label = "Accurately Self-Assessed (Matched Rating)"
        else:
            diff = d_rank - v_rank
            status = "gap"
            label = f"Below Declared Rating (-{diff} tier{'s' if diff > 1 else ''})"

        mcq_s = r["mcq_score"] or 0.0
        mcq_m = r["mcq_max"] or 50.0
        prog_s = r["programming_score"] or 0.0
        prog_m = r["programming_max"] or 20.0

        profiles.append({
            "skill_name": r["skill_name"],
            "overall_score_pct": r["score_pct"],
            "proficiency_level": prof_lvl,
            "declared_skill": {
                "skill_name": r["skill_name"],
                "declared_level": decl_lvl
            },
            "verified_skill": {
                "skill_name": r["skill_name"],
                "score_pct": r["score_pct"],
                "proficiency_level": prof_lvl,
                "category": r["category"] or "Technical Skill"
            },
            "comparison": {
                "declared_level": decl_lvl,
                "verified_level": prof_lvl,
                "status": status,
                "label": label
            },
            "mcq_performance": {
                "score": mcq_s,
                "total": mcq_m,
                "percentage": round((mcq_s / mcq_m) * 100.0, 1) if mcq_m > 0 else 0.0,
                "weight_pct": 70
            },
            "programming_performance": {
                "score": prog_s,
                "total": prog_m,
                "percentage": round((prog_s / prog_m) * 100.0, 1) if prog_m > 0 else 0.0,
                "weight_pct": 30,
                "challenges": prog_details
            },
            "topic_scores": topic_scores,
            "difficulty_scores": difficulty_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "verified_at": r["verified_at"]
        })

    return {
        "success": True,
        "has_verified_profile": len(profiles) > 0,
        "profile": profiles[0] if profiles else None,
        "profiles": profiles
    }

@router.get("/verified-profile/{skill_name}")
def get_single_verified_skill_profile(skill_name: str, user_id: int = Depends(get_current_user_id)):
    """Retrieves verified skill profile for a specific skill."""
    return get_verified_skill_profile(skill_name=skill_name, user_id=user_id)
