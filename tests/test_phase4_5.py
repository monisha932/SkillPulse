import json
import urllib.request
import urllib.parse

BASE = "http://127.0.0.1:8000"

def run_tests():
    print("1. Logging in demo student...")
    login_data = json.dumps({"email": "student@example.com", "password": "password123"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req).read())
    token = res["token"]
    user_id = res["user"]["id"]
    print(f"   Logged in user: {res['user']['name']}, Token: {token[:8]}...")

    print("2. Testing Market Demand & NLP Analytics API...")
    req = urllib.request.Request(f"{BASE}/api/market/analytics?role_id=fullstack-dev")
    market_res = json.loads(urllib.request.urlopen(req).read())
    analytics = market_res["analytics"]
    print(f"   Postings analyzed: {analytics['total_postings_analyzed']}")
    print(f"   Top extracted skills: {[s['skill_name'] + ' (' + str(s['demand_score_pct']) + '%)' for s in analytics['global_top_skills'][:4]]}")
    assert len(analytics["global_top_skills"]) > 0

    print("3. Testing Mathematical Skill Gap Engine...")
    gap_req_data = json.dumps({"target_role_id": "fullstack-dev"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/skills/gap-analysis", data=gap_req_data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    gap_res = json.loads(urllib.request.urlopen(req).read())
    ga = gap_res["gap_analysis"]
    print(f"   Role Match: {ga['role_match_percentage']}%")
    print(f"   Skills evaluated: {ga['total_skills_evaluated']}, Critical Gaps: {ga['critical_gaps_count']}, Medium Gaps: {ga['medium_gaps_count']}")
    print("   Sample Gaps:")
    for g in ga["gaps"][:3]:
        print(f"     - {g['skill_name']}: Required={g['required_proficiency']}, Verified={g['verified_proficiency']}, Gap Score={g['gap_score']}, Priority={g['priority']}")
    assert len(ga["gaps"]) > 0
    assert len(ga["radar_chart_data"]["categories"]) > 0

    print("4. Testing Micro-Credential Curriculum Generation...")
    curr_req_data = json.dumps({"target_role_id": "fullstack-dev"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/curriculum/generate", data=curr_req_data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    curr_res = json.loads(urllib.request.urlopen(req).read())
    curr = curr_res["curriculum"]
    print(f"   Curriculum Synthesized: '{curr['curriculum_title']}'")
    print(f"   Total Modules: {curr['total_modules']}, Total Est Hours: {curr['total_estimated_hours']} hrs")
    print(f"   Stackable Micro-Credentials: {len(curr['micro_credentials'])} badges.")
    for mc in curr["micro_credentials"]:
        print(f"     * [{mc['code']}] {mc['title']} ({mc['estimated_hours']} hrs) - Skill: {mc['target_skill']}")
    assert curr["total_modules"] > 0
    assert len(curr["micro_credentials"]) > 0

    print("5. Testing Curriculum Module Progress Tracking (Step 16)...")
    first_mod_id = curr["modules"][0]["module_id"]
    prog_data = json.dumps({"module_id": first_mod_id, "progress_pct": 100, "status": "completed"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/curriculum/module/progress", data=prog_data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    prog_res = json.loads(urllib.request.urlopen(req).read())
    print(f"   Module {first_mod_id} marked as {prog_res['status']} with {prog_res['progress_pct']}% progress.")
    assert prog_res["status"] == "completed"

    print("6. Testing Curriculum Dynamic Adaptation (Step 17)...")
    adapt_data = json.dumps({"target_role_id": "fullstack-dev"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/curriculum/adapt", data=adapt_data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    adapt_res = json.loads(urllib.request.urlopen(req).read())
    print(f"   Adaptation success: {adapt_res['success']}, Version: {adapt_res['curriculum']['adaptation_version']}")
    assert adapt_res["curriculum"]["adaptation_version"] >= 2

    print("\n>>> Phase 4 & 5 Backend Integration Tests PASSED 100%! <<<")

if __name__ == "__main__":
    run_tests()
