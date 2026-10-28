import json
from backend.routers.auth import login_user
from backend.models import UserLoginRequest
from backend.routers.assessment import (
    start_assessment, save_answer, run_code_tests,
    log_violation, complete_assessment,
    SaveAnswerRequest, RunCodeRequest, ViolationRequest, CompleteAssessmentRequest
)

def run_tests():
    print("1. Logging in as student...")
    login_res = login_user(UserLoginRequest(email="student@example.com", password="password123"))
    user_id = login_res["user"]["id"]

    print("2. Starting 90-minute assessment...")
    start_res = start_assessment(user_id=user_id)
    token = start_res["session_token"]
    print(f"   Session started! Token: {token[:8]}..., MCQs: {start_res['total_mcqs']}, Coding: {start_res['total_coding']}")
    assert start_res["total_mcqs"] == 50
    assert start_res["total_coding"] == 2

    print("3. Auto-saving MCQ answers...")
    # Answer question 1 (correct option for Q1 is 1: False, True)
    save_res1 = save_answer(SaveAnswerRequest(session_token=token, question_num=1, selected_option=1))
    print(f"   Saved Q1: {save_res1['success']}")
    assert save_res1["success"] is True

    # Answer question 2 (correct option for Q2 is 1: enumerate())
    save_res2 = save_answer(SaveAnswerRequest(session_token=token, question_num=2, selected_option=1))
    assert save_res2["success"] is True

    print("4. Testing Code Runner on Programming Challenge (Q51)...")
    code_q51 = """
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
    run_res = run_code_tests(RunCodeRequest(session_token=token, question_num=51, code=code_q51))
    print(f"   Code Runner Passed: {run_res['passed_count']} / {run_res['total_count']}, All: {run_res['all_passed']}")
    assert run_res["all_passed"] is True

    # Save code for Q51
    save_code_res = save_answer(SaveAnswerRequest(session_token=token, question_num=51, submitted_code=code_q51))
    assert save_code_res["success"] is True

    print("5. Testing Integrity Control Infraction Logger...")
    violation_res = log_violation(ViolationRequest(session_token=token, violation_type="tab_switch", details="Browser tab hidden for 4s"))
    print(f"   Tab switch logged. Switch count: {violation_res['tab_switch_count']}, Integrity score: {violation_res['integrity_score']}")
    assert violation_res["tab_switch_count"] >= 1

    print("6. Completing assessment and generating verified skill profile...")
    comp_res = complete_assessment(CompleteAssessmentRequest(session_token=token))
    print(f"   Assessment completed! MCQ Score: {comp_res['results']['mcq_score_pct']}%, Coding Score: {comp_res['results']['coding_score_pct']}%")
    print(f"   Overall Score: {comp_res['results']['overall_total_pct']}%, Integrity: {comp_res['results']['integrity_score']}")
    print(f"   Verified Skills Generated: {len(comp_res['results']['verified_skills'])} skills.")
    for vs in comp_res["results"]["verified_skills"][:4]:
        print(f"     - {vs['skill_name']}: {vs['score_pct']}% ({vs['proficiency_level']})")

    assert len(comp_res["results"]["verified_skills"]) > 0
    print("\n>>> Phase 3 Backend Verification Passed 100%! <<<")

if __name__ == "__main__":
    run_tests()
