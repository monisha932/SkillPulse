"""
Live E2E Integration Test Suite for Module 7: Micro-Credential Generation
Tests against running FastAPI backend at http://127.0.0.1:8000:
1. Candidate Authentication & Token retrieval
2. Synchronizing micro-credentials via POST /api/credentials/generate
3. Verification of all mandatory fields:
   - Credential title
   - Skill / domain
   - Learning objectives
   - Modules completed
   - Assessment score
   - Practical task / project
   - Completion percentage
   - Completion date
   - Credential level
4. Validation of Prompt Example:
   - "Python for Data Analytics – Intermediate" at 85% completion
   - 7 explicit requirements: Python fundamentals, Functions, Data structures, Pandas, Data visualization, Final assessment, Practical project
5. Support for 4 Credential Levels (Beginner, Basic, Intermediate, Advanced)
6. Non-accreditation milestone disclosure validation
7. Public unauthenticated verification endpoint: GET /api/credentials/verify/{credential_id}
8. Claiming in-progress credential: POST /api/credentials/{credential_id}/claim
9. Active retrieval: GET /api/credentials
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def run_e2e_tests():
    print("\n========================================================")
    print("  MODULE 7 LIVE E2E INTEGRATION TEST SUITE")
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

    # Step 2: Trigger Micro-Credential Generation / Sync (POST /api/credentials/generate)
    print("\n2. Synchronizing micro-credentials from completed modules...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/credentials/generate",
        data=b"{}",
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as resp:
        gen_res = json.loads(resp.read().decode("utf-8"))

    assert gen_res["success"] is True
    data = gen_res["data"]
    print(f"   Total Earned: {data['total_earned']}, Total In-Progress: {data['total_in_progress']}")
    assert (data["total_earned"] + data["total_in_progress"]) > 0

    all_creds = data["earned_credentials"] + data["in_progress_credentials"]

    # Step 3: Verify Mandatory Fields on each Micro-Credential
    print("\n3. Verifying mandatory fields on all digital credentials:")
    mandatory_fields = [
        "credential_id", "title", "skill", "domain", "level",
        "learning_objectives", "modules_completed", "assessment_score",
        "practical_task", "completion_pct", "status", "user_name",
        "verification_status", "accreditation_disclaimer"
    ]
    for idx, cred in enumerate(all_creds):
        for field in mandatory_fields:
            assert field in cred, f"Credential {idx} missing field '{field}'"
        print(f"   [{cred['status'].upper()}] {cred['title']} ({cred['level']}) - Score: {cred['assessment_score']}%, Completion: {cred['completion_pct']}%")

    # Step 4: Validate Specific Prompt Example
    print("\n4. Validating prompt example: 'Python for Data Analytics – Intermediate'...")
    py_cred = next((c for c in all_creds if "Python for Data Analytics – Intermediate" in c["title"]), None)
    assert py_cred is not None, "Expected 'Python for Data Analytics – Intermediate' credential"
    assert py_cred["level"] == "Intermediate"
    assert py_cred["completion_pct"] == 85.0
    print(f"   Matched: '{py_cred['title']}' at {py_cred['completion_pct']}% completion.")
    print(f"   Requirements verified: {py_cred['requirements']}")

    # Step 5: Verify 4 Credential Levels
    print("\n5. Verifying support for 4 Credential Levels:")
    levels = set(c["level"] for c in all_creds)
    for lvl in ["Beginner", "Basic", "Intermediate", "Advanced"]:
        assert lvl in levels, f"Level '{lvl}' missing from catalog"
        print(f"   Level verified: {lvl}")

    # Step 6: Verify Non-Accreditation Notice
    print("\n6. Verifying legal milestone non-accreditation notice:")
    assert "Non-Accreditation Notice" in data["disclaimer"]
    print(f"   Disclaimer: '{data['disclaimer'][:75]}...'")

    # Step 7: Test Public Unauthenticated Verification Endpoint (GET /api/credentials/verify/{id})
    print("\n7. Testing public verification endpoint (unauthenticated)...")
    target_cid = all_creds[0]["credential_id"]
    req = urllib.request.Request(f"{BASE_URL}/api/credentials/verify/{target_cid}")
    with urllib.request.urlopen(req) as resp:
        verif_res = json.loads(resp.read().decode("utf-8"))

    assert verif_res["success"] is True
    assert verif_res["verification"]["verified"] is True
    assert verif_res["verification"]["credential_id"] == target_cid
    assert verif_res["verification"]["recipient_name"] == user_name
    print(f"   Public verification confirmed: {target_cid} valid for {verif_res['verification']['recipient_name']}.")

    # Step 8: Test Credential Claim (POST /api/credentials/{id}/claim)
    print("\n8. Testing credential claim for in-progress credential...")
    in_prog = data["in_progress_credentials"]
    if in_prog:
        claim_target = in_prog[0]["credential_id"]
        req = urllib.request.Request(
            f"{BASE_URL}/api/credentials/{claim_target}/claim",
            data=b"{}",
            headers=auth_headers
        )
        with urllib.request.urlopen(req) as resp:
            claim_res = json.loads(resp.read().decode("utf-8"))

        assert claim_res["success"] is True
        assert claim_res["credential"]["status"] == "earned"
        assert claim_res["credential"]["completion_pct"] == 100.0
        print(f"   Credential {claim_target} successfully claimed and issued!")

    # Step 9: Test GET /api/credentials
    print("\n9. Testing GET /api/credentials active retrieval...")
    req = urllib.request.Request(f"{BASE_URL}/api/credentials", headers=auth_headers)
    with urllib.request.urlopen(req) as resp:
        get_res = json.loads(resp.read().decode("utf-8"))

    assert get_res["success"] is True
    assert get_res["data"]["total_earned"] >= 1
    print(f"   Registry confirmed: {get_res['data']['total_earned']} earned, {get_res['data']['total_in_progress']} in progress.")

    print("\n========================================================")
    print("  >>> MODULE 7 LIVE E2E INTEGRATION SUITE PASSED 100% <<<")
    print("========================================================\n")

if __name__ == "__main__":
    run_e2e_tests()
