"""
Live E2E Integration Test Suite for Module 6: Personalized AI Curriculum Generator
Interacts directly with the running FastAPI backend at http://127.0.0.1:8000.
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def run_e2e_tests():
    print("\n========================================================")
    print("  MODULE 6 LIVE E2E INTEGRATION TEST SUITE")
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

    # Step 2: Test POST /api/curriculum/generate (Data Analyst Role)
    print("\n2. Generating Personalized Curriculum for 'Data Analyst' role...")
    gen_payload = json.dumps({
        "target_role_id": "data-analyst",
        "weekly_hours": 10,
        "preferred_difficulty": "Adaptive",
        "learning_preferences": "Hands-on Projects & Coding"
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/curriculum/generate",
        data=gen_payload,
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        gen_res = json.loads(resp.read().decode("utf-8"))

    assert gen_res["success"] is True
    curr = gen_res["curriculum"]
    print(f"   Pathway Generated: '{curr['curriculum_title']}'")
    print(f"   Total Modules: {curr['total_modules']}, Total Est Hours: {curr['total_estimated_hours']} hrs")
    print(f"   Estimated Duration: ~{curr['estimated_weeks']} weeks at {curr['weekly_hours']} hrs/week")
    print(f"   Milestone Badges: {len(curr['micro_credentials'])} credentials available")

    # Check 12 mandatory fields on each module
    modules = curr["modules"]
    assert len(modules) >= 6, f"Expected at least 6 modules, got {len(modules)}"

    print("\n3. Verifying 12 Mandatory Fields on all generated modules:")
    mandatory_fields = [
        "skill_name", "current_proficiency", "required_proficiency",
        "learning_objective", "prerequisites", "topics", "difficulty",
        "estimated_duration", "learning_resources", "practice_activities",
        "assessment", "project_task"
    ]
    for idx, mod in enumerate(modules):
        for field in mandatory_fields:
            assert field in mod, f"Module {idx} missing mandatory field '{field}'"
        print(f"   Module {mod['module_order']}: {mod['skill_name']} ({mod['hours']} hrs) - Prereqs: {mod['prerequisites']}")

    # Check topological sequence: Python for Data Analysis precedes Pandas
    skill_names = [m["skill_name"] for m in modules]
    if "Python for Data Analysis" in skill_names and "Pandas" in skill_names:
        assert skill_names.index("Python for Data Analysis") < skill_names.index("Pandas"), "Python must precede Pandas"
        print("   Topology verified: Python for Data Analysis correctly precedes Pandas.")

    # Check terminal Capstone module
    assert skill_names[-1] == "Capstone Project", "Terminal module must be Capstone Project"
    print("   Capstone verified: Capstone Project is the terminal milestone module.")

    # Check non-accreditation disclaimer
    assert "disclaimer" in curr and "Non-Accreditation Notice" in curr["disclaimer"]
    print(f"   Disclaimer verified: '{curr['disclaimer'][:65]}...'")

    # Step 4: Test GET /api/curriculum
    print("\n4. Testing GET /api/curriculum active retrieval...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/curriculum?target_role_id=data-analyst",
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        get_res = json.loads(resp.read().decode("utf-8"))

    assert get_res["success"] is True
    active_curr = get_res["curriculum"]
    assert active_curr["curriculum_id"] == curr["curriculum_id"]
    print(f"   Retrieved active curriculum ID {active_curr['curriculum_id']} with {len(active_curr['modules'])} modules.")

    # Step 5: Test POST /api/curriculum/module/progress
    print("\n5. Testing POST /api/curriculum/module/progress (Completing Module 1)...")
    first_mod_id = active_curr["modules"][0]["module_id"]
    prog_payload = json.dumps({
        "module_id": first_mod_id,
        "progress_pct": 100,
        "status": "completed"
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/curriculum/module/progress",
        data=prog_payload,
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        prog_res = json.loads(resp.read().decode("utf-8"))

    assert prog_res["success"] is True
    assert prog_res["status"] == "completed"
    print(f"   Module {first_mod_id} successfully marked as completed.")

    # Step 6: Test POST /api/curriculum/adapt
    print("\n6. Testing POST /api/curriculum/adapt (Adapting to Full Stack Developer)...")
    adapt_payload = json.dumps({
        "target_role_id": "fullstack-dev",
        "weekly_hours": 15,
        "preferred_difficulty": "Adaptive"
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/curriculum/adapt",
        data=adapt_payload,
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        adapt_res = json.loads(resp.read().decode("utf-8"))

    assert adapt_res["success"] is True
    adapted_curr = adapt_res["curriculum"]
    print(f"   Adapted pathway: '{adapted_curr['curriculum_title']}' (Version: {adapted_curr['adaptation_version']})")
    assert adapted_curr["target_role_id"] == "fullstack-dev"
    assert len(adapted_curr["modules"]) > 0

    print("\n========================================================")
    print("  >>> MODULE 6 LIVE E2E INTEGRATION SUITE PASSED 100% <<<")
    print("========================================================\n")

if __name__ == "__main__":
    run_e2e_tests()
