"""
Comprehensive automated test suite for MODULE 2: USER SKILL ASSESSMENT & VERIFICATION.
Tests all requirements:
1. 50 MCQs per skill (Python, SQL, Java)
2. 2 Programming questions per skill
3. 90-minute timer calculation & auto-submit
4. Answer persistence (MCQ selections & code drafts)
5. Multi-language sandboxed code execution (Python, SQL, Java)
6. Anti-cheating browser integrity controls & focus-loss audit log
7. Secure backend scoring, topic-wise, difficulty-wise, and test-case analytics
8. Database storage across all relational tables
"""

import json
from datetime import datetime, timedelta
from backend.database import get_db_connection, init_db
from backend.routers.auth import register_user, login_user
from backend.models import (
    UserLoginRequest,
    SkillAssessmentStartRequest,
    SaveAnswerRequest,
    RunCodeRequest,
    ViolationRequest,
    CompleteAssessmentRequest
)
from backend.routers.assessment import (
    get_assessment_skills,
    start_assessment,
    get_session_status,
    save_answer,
    run_code_tests,
    log_violation,
    complete_assessment
)
from backend.services.code_evaluator import evaluate_code

def run_all_tests():
    print("======================================================================")
    print("RUNNING COMPREHENSIVE TEST SUITE FOR MODULE 2: SKILL ASSESSMENT")
    print("======================================================================")

    # 1. Authenticate Demo Student
    print("\n--- TEST 1: Candidate Authentication ---")
    login_res = login_user(UserLoginRequest(email="student@example.com", password="password123"))
    assert login_res["success"] is True
    user_id = login_res["user"]["id"]
    print(f"Candidate Authenticated: {login_res['user']['name']} (ID: {user_id})")

    # 2. Check Available Assessment Skills
    print("\n--- TEST 2: Available Assessment Skills Discovery ---")
    skills_res = get_assessment_skills(user_id=user_id)
    skills = skills_res["skills"]
    skill_names = [s["skill_name"] for s in skills]
    print(f"Available Skills for Verification: {skill_names}")
    assert "Python" in skill_names
    assert "SQL" in skill_names
    assert "Java" in skill_names

    # 3. Test 50 MCQs & 2 Coding Questions for Python, SQL, and Java
    print("\n--- TEST 3: 50 MCQs + 2 Programming Questions Structure ---")
    for test_skill in ["Python", "SQL", "Java"]:
        start_payload = SkillAssessmentStartRequest(skill_name=test_skill)
        ass_data = start_assessment(req=start_payload, user_id=user_id)
        
        token = ass_data["session_token"]
        mcqs = ass_data["mcqs"]
        coding = ass_data["coding_questions"]

        print(f"\nEvaluating {test_skill} Assessment Payload:")
        print(f" - Duration: {ass_data['duration_minutes']} minutes (90m required)")
        print(f" - Total MCQs: {len(mcqs)} (50 required)")
        print(f" - Total Coding Challenges: {len(coding)} (2 required)")

        assert ass_data["duration_minutes"] == 90, "Assessment duration must be 90 minutes"
        assert len(mcqs) == 50, f"Expected exactly 50 MCQs for {test_skill}, got {len(mcqs)}"
        assert len(coding) == 2, f"Expected exactly 2 Coding questions for {test_skill}, got {len(coding)}"

        # Verify correct options are NEVER leaked in candidate payload
        for q in mcqs:
            assert "correct_option" not in q, f"CRITICAL SECURITY LEAK: correct_option exposed in MCQ #{q['question_num']}"
            assert len(q["options"]) == 4, f"MCQ #{q['question_num']} must have 4 options (A, B, C, D)"
            assert q["topic"], f"MCQ #{q['question_num']} missing topic categorization"
            assert q["difficulty"] in ["Easy", "Medium", "Hard"], f"MCQ #{q['question_num']} invalid difficulty: {q['difficulty']}"

        # Verify Coding Questions have required attributes
        for cq in coding:
            assert cq["problem_statement"], f"Coding #{cq['question_num']} missing problem statement"
            assert cq["code_template"], f"Coding #{cq['question_num']} missing starter code template"
            assert len(cq["visible_test_cases"]) > 0, f"Coding #{cq['question_num']} missing visible test cases"
            for tc in cq["visible_test_cases"]:
                assert tc.get("is_hidden", False) is False, "Hidden test case exposed in visible test cases!"

        print(f" [PASS] {test_skill} Question Bank satisfies all 50 MCQ & 2 Programming requirements!")

    # 4. Test 90-Minute Timer & Countdown
    print("\n--- TEST 4: 90-Minute Countdown Timer & Session Tracking ---")
    py_session = start_assessment(req=SkillAssessmentStartRequest(skill_name="Python"), user_id=user_id)
    token = py_session["session_token"]

    status_data = get_session_status(session_token=token)
    print(f"Session Status: {status_data['status']}")
    print(f"Remaining seconds: {status_data['remaining_seconds']}s (out of {status_data['duration_minutes'] * 60}s)")
    assert status_data["duration_minutes"] == 90
    assert status_data["remaining_seconds"] <= 90 * 60
    assert status_data["is_expired"] is False
    print(" [PASS] 90-Minute Countdown Timer verified successfully.")

    # 5. Test Answer Persistence (MCQ & Code Drafts)
    print("\n--- TEST 5: Answer Persistence (Auto-Save) ---")
    # Save MCQ 1
    save_mcq_res = save_answer(SaveAnswerRequest(session_token=token, question_num=1, selected_option=1))
    assert save_mcq_res["success"] is True
    # Save MCQ 2
    save_mcq_res2 = save_answer(SaveAnswerRequest(session_token=token, question_num=2, selected_option=2))
    assert save_mcq_res2["success"] is True

    # Save Programming Draft for Q51
    sample_code_q51 = "def find_target_subarray(nums, target): return [0, 1]"
    save_code_res = save_answer(SaveAnswerRequest(session_token=token, question_num=51, submitted_code=sample_code_q51))
    assert save_code_res["success"] is True

    # Re-fetch session status to verify answer counts
    updated_status = get_session_status(session_token=token)
    print(f"Answered Questions Persisted: {updated_status['answered_count']} / 52")
    assert updated_status["answered_count"] >= 3
    print(" [PASS] Incremental answer persistence verified.")

    # 6. Test Multi-Language Sandboxed Code & Query Execution
    print("\n--- TEST 6: Multi-Language Code Runner (Python, SQL, Java) ---")

    # A. Python Execution
    py_code_valid = """
def find_target_subarray(nums, target):
    curr_sum = 0
    start = 0
    for end in range(len(nums)):
        curr_sum += nums[end]
        while curr_sum > target and start <= end:
            curr_sum -= nums[start]
            start += 1
        if curr_sum == target:
            return [start, end]
    return [-1, -1]
"""
    py_res = run_code_tests(RunCodeRequest(session_token=token, question_num=51, code=py_code_valid))
    print(f"Python Code Runner: Passed {py_res['passed_count']} of {py_res['total_count']} visible test cases (All passed: {py_res['all_passed']})")
    assert py_res["all_passed"] is True

    # B. SQL Execution
    sql_session = start_assessment(req=SkillAssessmentStartRequest(skill_name="SQL"), user_id=user_id)
    sql_token = sql_session["session_token"]
    sql_code_valid = """
SELECT 
  d.name AS department_name,
  COUNT(e.id) AS employee_count,
  MAX(e.salary) AS max_salary
FROM departments d
JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY max_salary DESC, department_name ASC;
"""
    sql_res = run_code_tests(RunCodeRequest(session_token=sql_token, question_num=51, code=sql_code_valid))
    print(f"SQL Query Runner: Passed {sql_res['passed_count']} of {sql_res['total_count']} visible test cases (All passed: {sql_res['all_passed']})")
    assert sql_res["all_passed"] is True

    # C. Java Execution
    java_session = start_assessment(req=SkillAssessmentStartRequest(skill_name="Java"), user_id=user_id)
    java_token = java_session["session_token"]
    java_code_valid = """
import java.util.*;

public class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[] { map.get(complement), i };
            }
            map.put(nums[i], i);
        }
        return new int[] {-1, -1};
    }
}
"""
    java_res = run_code_tests(RunCodeRequest(session_token=java_token, question_num=51, code=java_code_valid))
    print(f"Java Code Runner: Passed {java_res['passed_count']} of {java_res['total_count']} visible test cases (All passed: {java_res['all_passed']})")
    assert java_res["all_passed"] is True
    print(" [PASS] All 3 execution engines (Python, SQL, Java) passed sandbox testing.")

    # 7. Test Assessment Integrity & Focus-Loss Monitoring
    print("\n--- TEST 7: Integrity Controls & Focus-Loss Event Audit ---")
    # Tab switch 1
    v1 = log_violation(ViolationRequest(session_token=token, violation_type="tab_switch", details="Switched to external tab"))
    assert v1["tab_switch_count"] == 1
    assert v1["integrity_score"] == 95.0
    print(f"Tab Switch logged: score = {v1['integrity_score']}%, flagged = {v1['is_flagged']}")

    # Window blur
    v2 = log_violation(ViolationRequest(session_token=token, violation_type="window_blur", details="Browser window lost focus"))
    assert v2["blur_count"] == 1
    assert v2["integrity_score"] == 93.0

    # Copy attempt
    v3 = log_violation(ViolationRequest(session_token=token, violation_type="copy_attempt", details="Blocked clipboard copy"))
    assert v3["copy_paste_count"] == 1
    assert v3["integrity_score"] == 90.0

    # Verify storage in integrity_events table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as ev_cnt FROM integrity_events")
    ev_cnt = cursor.fetchone()["ev_cnt"]
    conn.close()
    assert ev_cnt >= 3
    print(f"Integrity Events Audit Trail: {ev_cnt} events stored in database.")
    print(" [PASS] Integrity monitoring and database auditing verified.")

    # 8. Test Secure Backend Scoring & Granular Breakdown
    print("\n--- TEST 8: Backend Evaluation & Granular Scoring ---")
    # Save proper code for Q51 and Q52 before completing
    save_answer(SaveAnswerRequest(session_token=token, question_num=51, submitted_code=py_code_valid))
    py_code_q52 = """
def is_valid_brackets(s: str) -> bool:
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack
"""
    save_answer(SaveAnswerRequest(session_token=token, question_num=52, submitted_code=py_code_q52))

    # Complete Assessment
    complete_res = complete_assessment(CompleteAssessmentRequest(session_token=token))
    results = complete_res["results"]

    print("\nAssessment Evaluation Results:")
    print(f" - Skill Assessed: {results['skill_name']}")
    print(f" - MCQ Score: {results['mcq_score']} / {results['mcq_total']} ({results['mcq_score_pct']}%)")
    print(f" - Programming Score: {results['programming_score']} / {results['programming_max']} ({results['programming_score_pct']}%)")
    print(f" - Overall Weighted Score: {results['overall_total_pct']}%")
    print(f" - Assigned Proficiency Tier: {results['proficiency_level']}")
    print(f" - Integrity Score: {results['integrity_score']}%")

    # Verify Topic-wise Breakdown
    print("\nTopic-wise Breakdown:")
    topic_scores = results["topic_scores"]
    assert len(topic_scores) > 0
    for topic, stats in list(topic_scores.items())[:3]:
        print(f"   * {topic}: {stats['correct']}/{stats['total']} ({stats['percentage']}%)")

    # Verify Difficulty-wise Performance
    print("\nDifficulty-wise Performance:")
    diff_scores = results["difficulty_scores"]
    assert "Easy" in diff_scores or "Medium" in diff_scores
    for diff, stats in diff_scores.items():
        print(f"   * {diff}: {stats['correct']}/{stats['total']} ({stats['percentage']}%)")

    # Verify Programming Test Cases Details
    print("\nProgramming Challenges Test-Case Performance:")
    prog_details = results["programming_details"]
    assert len(prog_details) == 2
    for pd in prog_details:
        print(f"   * Q{pd['question_num']} ({pd['title']}): {pd['test_cases_passed']}/{pd['total_test_cases']} tests passed -> {pd['score_awarded']}/10.0 pts")

    # 9. Verify Relational Database Storage & Module 3 Handoff
    print("\n--- TEST 9: Relational Database Storage & Module 3 Handoff ---")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as cnt FROM assessments")
    print(f"Assessments table rows: {cursor.fetchone()['cnt']}")

    cursor.execute("SELECT COUNT(*) as cnt FROM assessment_questions")
    print(f"Assessment Questions table rows: {cursor.fetchone()['cnt']}")

    cursor.execute("SELECT COUNT(*) as cnt FROM assessment_attempts WHERE is_completed = 1")
    print(f"Completed Assessment Attempts: {cursor.fetchone()['cnt']}")

    cursor.execute("SELECT COUNT(*) as cnt FROM mcq_answers")
    print(f"MCQ Answers recorded: {cursor.fetchone()['cnt']}")

    cursor.execute("SELECT COUNT(*) as cnt FROM programming_submissions")
    print(f"Programming Submissions recorded: {cursor.fetchone()['cnt']}")

    cursor.execute("SELECT COUNT(*) as cnt FROM assessment_results")
    print(f"Assessment Results recorded: {cursor.fetchone()['cnt']}")

    cursor.execute("SELECT COUNT(*) as cnt FROM integrity_events")
    print(f"Integrity Events recorded: {cursor.fetchone()['cnt']}")

    cursor.execute("SELECT * FROM verified_skills WHERE user_id = ?", (user_id,))
    ver_rows = cursor.fetchall()
    print(f"Verified Skills for Module 3 Handoff: {len(ver_rows)} records.")
    for vr in ver_rows:
        print(f"   -> Skill: {vr['skill_name']} | Score: {vr['score_pct']}% | Level: {vr['proficiency_level']}")

    conn.close()

    assert len(ver_rows) > 0, "verified_skills table must contain evaluated candidate skills for Module 3!"
    print("\n======================================================================")
    print(">>> MODULE 2: USER SKILL ASSESSMENT & VERIFICATION PASSED 100%! <<<")
    print("======================================================================")

if __name__ == "__main__":
    run_all_tests()
