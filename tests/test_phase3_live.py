import urllib.request
import urllib.parse
import json

BASE = "http://127.0.0.1:8000"

def run_live_test():
    print("1. Logging in as student...")
    login_data = json.dumps({"email": "student@example.com", "password": "password123"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req).read())
    token = res["token"]
    print(f"   Logged in. User: {res['user']['name']}, Token: {token[:8]}...")

    print("2. Starting 90-minute timed assessment...")
    req = urllib.request.Request(f"{BASE}/api/assessment/start", data=b"{}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    start_res = json.loads(urllib.request.urlopen(req).read())
    sess_token = start_res["session_token"]
    print(f"   Assessment started! MCQs: {start_res['total_mcqs']}, Coding: {start_res['total_coding']}, Token: {sess_token[:8]}...")
    assert start_res["total_mcqs"] == 50
    assert start_res["total_coding"] == 2

    print("3. Saving Answers (Q1 MCQ and Q51 Coding)...")
    save_data = json.dumps({"session_token": sess_token, "question_num": 1, "selected_option": 1}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/assessment/save-answer", data=save_data, headers={"Content-Type": "application/json"})
    save_res = json.loads(urllib.request.urlopen(req).read())
    print(f"   Saved Q1 MCQ option: {save_res['saved']}")
    assert save_res["saved"] is True

    code_solution = """def find_target_subarray(nums, target):
    curr = 0
    s = 0
    for e in range(len(nums)):
        curr += nums[e]
        while curr > target and s <= e:
            curr -= nums[s]
            s += 1
        if curr == target:
            return [s, e]
    return [-1, -1]"""

    print("4. Testing Sandbox Code Execution on Q51...")
    run_data = json.dumps({"session_token": sess_token, "question_num": 51, "code": code_solution}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/assessment/run-code", data=run_data, headers={"Content-Type": "application/json"})
    run_res = json.loads(urllib.request.urlopen(req).read())
    print(f"   Sandbox Q51 passed: {run_res['passed_count']} / {run_res['total_count']} visible test cases in {run_res.get('execution_time_ms')}ms")
    assert run_res["all_passed"] is True

    # Save code answer
    save_code_data = json.dumps({"session_token": sess_token, "question_num": 51, "submitted_code": code_solution}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/assessment/save-answer", data=save_code_data, headers={"Content-Type": "application/json"})
    save_code_res = json.loads(urllib.request.urlopen(req).read())
    assert save_code_res["saved"] is True

    print("5. Logging Integrity Violation (Tab Switch)...")
    viol_data = json.dumps({"session_token": sess_token, "violation_type": "tab_switch", "details": "User switched tabs"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/assessment/violation", data=viol_data, headers={"Content-Type": "application/json"})
    viol_res = json.loads(urllib.request.urlopen(req).read())
    print(f"   Logged switch. Switches: {viol_res['tab_switch_count']}, Integrity Score: {viol_res['integrity_score']}%")
    assert viol_res["tab_switch_count"] >= 1

    print("6. Completing Assessment & Generating Verified Skills...")
    comp_data = json.dumps({"session_token": sess_token}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/assessment/complete", data=comp_data, headers={"Content-Type": "application/json"})
    comp_res = json.loads(urllib.request.urlopen(req).read())
    results = comp_res["results"]
    print(f"   Completed! MCQ Score: {results['mcq_score_pct']}%, Coding Score: {results['coding_score_pct']}%, Overall: {results['overall_total_pct']}%")
    print(f"   Verified Skills Generated: {len(results['verified_skills'])} items.")
    for vs in results["verified_skills"][:4]:
        print(f"     - {vs['skill_name']}: {vs['score_pct']}% ({vs['proficiency_level']})")
    assert len(results["verified_skills"]) > 0

    print("7. Verifying Static Assets...")
    assets = ["/static/css/assessment.css", "/static/js/integrity.js", "/static/js/assessment.js"]
    for a in assets:
        resp = urllib.request.urlopen(f"{BASE}{a}")
        print(f"   Asset {a}: Status {resp.status}, Size {len(resp.read())} bytes")

    print("\n>>> Phase 3 Live Integration Verification PASSED 100%! <<<")

if __name__ == "__main__":
    run_live_test()
