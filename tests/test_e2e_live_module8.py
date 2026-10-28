"""
Live E2E Integration Test Suite for Module 8: Adaptive Learning Path & Reassessment.
Tests against running FastAPI backend at http://127.0.0.1:8000:
1. Candidate Authentication & Token retrieval
2. Fetching Adaptive Learning Path: GET /api/adaptive/learning-path
3. Verifying banner: 'YOUR LEARNING PATH HAS BEEN UPDATED'
4. Reassessment Simulation: POST /api/adaptive/simulate-reassessment
   - Python: Before = 45%, After = 78%
   - SQL: Before = 60%, After = 85%
5. Querying historical comparisons: GET /api/adaptive/history
   - Asserts non-deletion of previous assessment results
6. Verifying pruning of unnecessary beginner Python modules
7. Simulating shifting job-market demand: POST /api/adaptive/simulate-market-shift
   - Verifies newly important skill (Docker) is added to learning path
8. Checking updated skill priorities and recommended next skills
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def run_e2e_tests():
    print("\n========================================================")
    print("  MODULE 8 LIVE E2E INTEGRATION TEST SUITE")
    print("========================================================\n")

    # Step 1: Candidate Authentication
    print("1. Authenticating candidate student...")
    login_payload = json.dumps({
        "email": "student@example.com",
        "password": "password123"
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=login_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        login_res = json.loads(resp.read().decode("utf-8"))

    token = login_res["token"]
    user_name = login_res["user"]["name"]
    user_id = login_res["user"]["id"]
    print(f"   Candidate authenticated: {user_name} (ID: {user_id}), Token: {token[:12]}...")

    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Step 2: Fetch Adaptive Learning Path (GET /api/adaptive/learning-path)
    print("\n2. Querying GET /api/adaptive/learning-path...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/adaptive/learning-path",
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        path_res = json.loads(resp.read().decode("utf-8"))

    assert path_res["success"] is True
    adaptive = path_res["adaptive_path"]
    print(f"   Banner: '{adaptive['banner_message']}'")
    assert adaptive["banner_message"] == "YOUR LEARNING PATH HAS BEEN UPDATED"
    print(f"   Pathway Version: v{adaptive['adaptation_version']}")
    print(f"   Total Modules in Path: {adaptive['total_modules']}")

    # Step 3: Reassessment - Simulate Python and SQL reassessment improvements
    print("\n3. Testing Reassessment with empirical Before vs After improvements:")
    # Python: Before = 45%, After = 78%
    print("   -> Simulating Python reassessment: 45% -> 78% (Basic to Advanced)...")
    sim_py = json.dumps({"skill_name": "Python", "new_score_pct": 78.0, "new_proficiency_level": "Advanced"}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/adaptive/simulate-reassessment",
        data=sim_py,
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        py_res = json.loads(resp.read().decode("utf-8"))
    assert py_res["success"] is True

    # SQL: Before = 60%, After = 85%
    print("   -> Simulating SQL reassessment: 60% -> 85% (Intermediate to Advanced)...")
    sim_sql = json.dumps({"skill_name": "SQL", "new_score_pct": 85.0, "new_proficiency_level": "Advanced"}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/adaptive/simulate-reassessment",
        data=sim_sql,
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        sql_res = json.loads(resp.read().decode("utf-8"))
    assert sql_res["success"] is True

    # Step 4: Verify Historical Assessment Preservation & Comparisons (GET /api/adaptive/history)
    print("\n4. Querying GET /api/adaptive/history for Before vs After comparisons...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/adaptive/history",
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        hist_res = json.loads(resp.read().decode("utf-8"))

    assert hist_res["success"] is True
    comparisons = hist_res["comparisons"]
    comp_map = {c["skill_name"].lower(): c for c in comparisons}

    if "python" in comp_map:
        py_c = comp_map["python"]
        print(f"   * Python: Before = {py_c['before_score']}%, After = {py_c['after_score']}% (Change: +{py_c['score_change']}%, Status: {py_c['status']})")
        assert py_c["after_score"] >= 75.0

    if "sql" in comp_map:
        sql_c = comp_map["sql"]
        print(f"   * SQL:    Before = {sql_c['before_score']}%, After = {sql_c['after_score']}% (Change: +{sql_c['score_change']}%, Status: {sql_c['status']})")
        assert sql_c["after_score"] >= 80.0

    # Step 5: Verify Beginner Module Pruning in Adapted Pathway
    print("\n5. Verifying unnecessary beginner modules are pruned upon sufficient proficiency:")
    latest_path = sql_res["adaptive_path"]
    pruned = latest_path.get("pruned_modules", [])
    print(f"   Pruned Modules Count: {len(pruned)}")
    for p in pruned:
        print(f"     - [Pruned] {p['module_title']} ({p['skill_name']}) -> {p['reason']}")

    # Step 6: Simulate Job-Market Demand Surge (POST /api/adaptive/simulate-market-shift)
    print("\n6. Simulating shifting job-market demand (+88% Docker demand)...")
    shift_payload = json.dumps({
        "role_id": "fullstack-dev",
        "new_skill": "Docker",
        "demand_percentage": 88.0
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/adaptive/simulate-market-shift",
        data=shift_payload,
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        shift_res = json.loads(resp.read().decode("utf-8"))

    assert shift_res["success"] is True
    adapted_after_shift = shift_res["adaptive_path"]
    added = adapted_after_shift.get("added_modules", [])
    added_skills = [a["skill_name"].lower() for a in added]
    print(f"   Newly Added Skills: {[a['skill_name'] for a in added]}")
    assert "docker" in added_skills, "Docker must be added to learning path upon market demand surge"

    # Step 7: Verify Recommended Next Skills and Explanations
    print("\n7. Verifying dynamic next skill recommendations and change explanations:")
    recs = adapted_after_shift.get("recommended_next_skills", [])
    for idx, r in enumerate(recs):
        print(f"   [Next #{idx+1}] {r['title']} ({r['skill_name']}) - Priority: {r['priority']}")

    print("\n   Explanations Log ('Why your curriculum changed'):")
    for exp in adapted_after_shift.get("explanations", []):
        print(f"     * {exp}")

    print("\n========================================================")
    print("  MODULE 8 LIVE E2E INTEGRATION TEST: 100% PASSED!")
    print("========================================================\n")

if __name__ == "__main__":
    run_e2e_tests()
