import urllib.request
import urllib.parse
import json

BASE = "http://127.0.0.1:8000"

def post_json(endpoint, data, token=None):
    req_bytes = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{endpoint}", data=req_bytes, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_json(endpoint, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{endpoint}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_live_e2e_module5_tests():
    print("======================================================================")
    print("MODULE 5 LIVE HTTP END-TO-END VERIFICATION (http://127.0.0.1:8000)")
    print("======================================================================")

    # 1. Health check
    print("\n[E2E 1] Checking API Health...")
    health = get_json("/api/health")
    assert health["status"] == "online"
    print(" -> API Health: ONLINE")

    # 2. Authentication
    print("\n[E2E 2] Logging in as student...")
    login = post_json("/api/auth/login", {"email": "student@example.com", "password": "password123"})
    token = login["token"]
    user_id = login["user"]["id"]
    print(f" -> Student authenticated: {login['user']['name']} (ID: {user_id})")

    # 3. Save Career Profile (Module 1) targeting fullstack-dev
    print("\n[E2E 3] Setting Career Profile to fullstack-dev...")
    profile_save = post_json("/api/profile", {
        "target_role_id": "fullstack-dev",
        "declared_skills": [
            {"skill_name": "Python", "self_rating": "Intermediate"},
            {"skill_name": "SQL", "self_rating": "Intermediate"},
            {"skill_name": "JavaScript", "self_rating": "Beginner"}
        ],
        "experience_level": "Fresher",
        "education": "B.E. Computer Science"
    }, token=token)
    assert profile_save["success"] is True
    print(" -> Career Profile saved.")

    # 4. Live Module 5 Skill Gap Analysis via GET /api/skills/gap-analysis
    print("\n[E2E 4] Querying GET /api/skills/gap-analysis for fullstack-dev...")
    gap_res = get_json("/api/skills/gap-analysis", token=token)
    assert gap_res["success"] is True
    analysis = gap_res["gap_analysis"]

    role = analysis["target_role"]
    assert role["role_id"] == "fullstack-dev"
    print(f" -> Target Role: {role['role_title']} ({role['domain']})")
    print(f" -> Role Match Readiness: {analysis['role_match_percentage']}%")
    print(f" -> Skills Evaluated: {analysis['total_skills_evaluated']}")
    print(f" -> Proficiencies Met: {analysis['mastered_count']}")
    print(f" -> Critical/High Gaps: {analysis['critical_gaps_count'] + analysis['high_gaps_count']}")
    print(f" -> Medium Gaps: {analysis['medium_gaps_count']}")

    # Verify competencies
    gaps = analysis["gaps"]
    skill_names = [g["skill_name"] for g in gaps]
    print(f" -> Evaluated Skills: {', '.join(skill_names[:8])}...")

    # Required skills verification
    spec_skills = ["JavaScript", "React", "Java", "SQL", "Git", "REST API", "HTML/CSS"]
    for s_name in spec_skills:
        assert s_name in skill_names, f"Expected {s_name} in gap analysis"
        g = next(item for item in gaps if item["skill_name"] == s_name)
        print(f"    * {g['skill_name']:<12} | Verified: {g['verified_level']:<12} ({g['verified_level_num']}/5) | Required: {g['required_level']:<12} ({g['required_level_num']}/5) | Gap: {g['gap']:<12} (+{g['gap_num']}) | Demand: {g['job_demand_percentage']}% | Priority: {g['priority']}")

    # Verify chart data
    assert "chart_data" in analysis
    self_chart = analysis["chart_data"]
    assert len(self_chart["categories"]) == len(gaps)
    assert len(self_chart["required_series"]) == len(gaps)
    assert len(self_chart["verified_series"]) == len(gaps)

    # 5. Live Module 5 Skill Gap Analysis via POST /api/skills/gap-analysis with target_role_id
    print("\n[E2E 5] Querying POST /api/skills/gap-analysis with target_role_id=ai-ml-engineer...")
    post_gap = post_json("/api/skills/gap-analysis", {"target_role_id": "ai-ml-engineer"}, token=token)
    assert post_gap["success"] is True
    ai_analysis = post_gap["gap_analysis"]
    assert ai_analysis["target_role"]["role_id"] == "ai-ml-engineer"
    ai_skills = [g["skill_name"] for g in ai_analysis["gaps"]]
    assert "Python" in ai_skills
    print(f" -> Dynamically switched to {ai_analysis['target_role']['role_title']}. Found {len(ai_skills)} competencies.")

    # 6. Regression: Module 4 Skill Demand
    print("\n[E2E 6] Regression Check: Module 4 Job-Market Skill Demand...")
    demand = get_json("/api/market/skill-demand?target_role_id=fullstack-dev", token=token)
    assert demand["success"] is True
    assert demand["total_postings_analyzed"] > 0
    print(f" -> Module 4 Market Demand online ({demand['total_postings_analyzed']} postings analyzed).")

    # 7. Regression: Module 3 Verified Profile
    print("\n[E2E 7] Regression Check: Module 3 Verified Skill Profile...")
    vprofile = get_json("/api/assessment/verified-profile", token=token)
    assert vprofile["success"] is True
    print(f" -> Module 3 Verified Profile online.")

    # 8. Regression: Module 2 Timed Assessment Start
    print("\n[E2E 8] Regression Check: Module 2 Timed Assessment Flow...")
    start_res = post_json("/api/assessment/start", {"skill_name": "Python"}, token=token)
    assert start_res["success"] is True
    assert start_res["total_mcqs"] == 50
    assert start_res["total_coding"] == 2
    print(" -> Module 2 Assessment Engine online (50 MCQs, 2 Coding questions).")

    print("\n======================================================================")
    print(">>> ALL MODULE 5 LIVE HTTP E2E & REGRESSION TESTS PASSED 100%! <<<")
    print("======================================================================")

if __name__ == "__main__":
    run_live_e2e_module5_tests()
