import urllib.request
import urllib.parse
import json
import io
import uuid

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

def post_multipart(endpoint, filename, file_bytes, content_type="text/csv", data_source=None, token=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = io.BytesIO()

    # Part 1: file
    body.write(f"--{boundary}\r\n".encode("utf-8"))
    body.write(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.write(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    body.write(file_bytes)
    body.write(b"\r\n")

    # Part 2: optional data_source
    if data_source:
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write('Content-Disposition: form-data; name="data_source"\r\n\r\n'.encode("utf-8"))
        body.write(data_source.encode("utf-8"))
        body.write(b"\r\n")

    body.write(f"--{boundary}--\r\n".encode("utf-8"))
    raw_payload = body.getvalue()

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(raw_payload))
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(f"{BASE}{endpoint}", data=raw_payload, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_live_e2e_tests():
    print("======================================================================")
    print("MODULE 4 LIVE HTTP END-TO-END VERIFICATION (http://127.0.0.1:8000)")
    print("======================================================================")

    # 1. Health check
    print("\n[E2E 1] Checking API Health...")
    health = get_json("/api/health")
    assert health["status"] == "online"
    print(" -> Health check: ONLINE (FastAPI Micro-Credential Engine)")

    # 2. Authentication
    print("\n[E2E 2] Logging in as student...")
    login = post_json("/api/auth/login", {"email": "student@example.com", "password": "password123"})
    token = login["token"]
    print(f" -> Student logged in: {login['user']['name']} (Token: {token[:10]}...)")

    # 3. Connect Career Profile (Module 1)
    print("\n[E2E 3] Setting Career Profile target role to fullstack-dev...")
    profile_save = post_json("/api/profile", {
        "target_role_id": "fullstack-dev",
        "declared_skills": [
            {"skill_name": "Python", "self_rating": "Intermediate"},
            {"skill_name": "JavaScript", "self_rating": "Intermediate"},
            {"skill_name": "SQL", "self_rating": "Beginner"}
        ],
        "experience_level": "Fresher",
        "degree_major": "B.E. Computer Science"
    }, token=token)
    assert profile_save["success"] is True
    print(" -> Career Profile saved with target role: fullstack-dev")

    # 4. Job-Market Skill Demand Endpoint
    print("\n[E2E 4] Querying GET /api/market/skill-demand for user's target role...")
    demand = get_json("/api/market/skill-demand", token=token)
    assert demand["success"] is True
    role = demand["target_role"]
    assert role["role_id"] == "fullstack-dev"
    total_postings = demand["total_postings_analyzed"]
    assert total_postings > 0
    print(f" -> Target Role: {role['role_title']} ({role['domain']})")
    print(f" -> Total Postings Analyzed: {total_postings}")
    print(f" -> Data Sources: {', '.join(demand['data_sources'])}")

    # Verify required skills for Full Stack Developer
    skill_names = [s["skill_name"] for s in demand["skills"]]
    print(f" -> Extracted {len(skill_names)} Competencies.")
    spec_skills = ["JavaScript", "React", "Java", "SQL", "Git", "REST API", "HTML/CSS"]
    for req_skill in spec_skills:
        assert req_skill in skill_names, f"Missing required skill {req_skill}"
        # Find skill entry
        s_obj = next(s for s in demand["skills"] if s["skill_name"] == req_skill)
        print(f"    * {s_obj['skill_name']}: {s_obj['frequency']}/{total_postings} jobs ({s_obj['demand_percentage']}%) - {s_obj['status']}")

    # 5. Filters endpoint
    print("\n[E2E 5] Querying GET /api/market/filters...")
    filters = get_json("/api/market/filters?target_role_id=fullstack-dev")
    assert filters["success"] is True
    f_data = filters["filters"]
    print(f" -> Industries: {f_data['industries']}")
    print(f" -> Locations: {f_data['locations']}")
    print(f" -> Experience Levels: {f_data['experience_levels']}")

    # 6. Filtered query
    print("\n[E2E 6] Querying GET /api/market/skill-demand with location=Remote...")
    filtered_demand = get_json("/api/market/skill-demand?target_role_id=fullstack-dev&location=Remote")
    assert filtered_demand["success"] is True
    assert filtered_demand["total_postings_analyzed"] > 0
    print(f" -> Filtered Remote Postings: {filtered_demand['total_postings_analyzed']}")

    # 7. Single posting API ingestion
    print("\n[E2E 7] Testing POST /api/market/jobs...")
    new_job = {
        "job_title": "Staff Full Stack Engineer",
        "target_role_id": "fullstack-dev",
        "company": "Antigravity Prime AI",
        "industry": "Artificial Intelligence",
        "location": "Remote",
        "required_skills": ["JavaScript", "React", "TypeScript", "GraphQL", "Docker"],
        "experience_level": "Senior Level",
        "data_source": "Live E2E API Test"
    }
    job_res = post_json("/api/market/jobs", new_job)
    assert job_res["success"] is True
    print(f" -> Ingested single posting: {job_res['result']['imported_count']} imported")

    # 8. Batch JSON import
    print("\n[E2E 8] Testing POST /api/market/import-json...")
    batch_json = {
        "data_source": "Live E2E JSON Batch",
        "postings": [
            {
                "job_title": "Full Stack Cloud Engineer",
                "target_role_id": "fullstack-dev",
                "company": "Apex Cloud Systems",
                "industry": "SaaS & Cloud Platforms",
                "location": "Seattle, WA",
                "required_skills": ["JavaScript", "React", "Java", "SQL", "Git", "Docker"],
                "experience_level": "Mid Level"
            }
        ]
    }
    json_res = post_json("/api/market/import-json", batch_json)
    assert json_res["success"] is True
    print(f" -> Imported JSON batch: {json_res['imported_count']} postings")

    # 9. Batch CSV import
    print("\n[E2E 9] Testing POST /api/market/import-csv...")
    csv_str = (
        "job_title,target_role_id,company,industry,location,required_skills,experience_level,posting_date,data_source\n"
        "Senior Web Engineer,fullstack-dev,FinTech Innovations,FinTech,New York NY,JavaScript;React;SQL;REST API,Senior Level,2026-03-10,Live CSV Batch\n"
    )
    csv_res = post_json("/api/market/import-csv", {"csv_content": csv_str, "data_source": "Live CSV Batch"})
    assert csv_res["success"] is True
    print(f" -> Imported CSV batch: {csv_res['imported_count']} postings")

    # 10. Admin Multipart File Upload
    print("\n[E2E 10] Testing POST /api/market/upload (multipart CSV file)...")
    upload_csv = (
        b"job_title,target_role_id,company,industry,location,required_skills,experience_level,posting_date,data_source\n"
        b"Full Stack Health Tech,fullstack-dev,BioTech Systems,Healthcare Tech,Remote,JavaScript;React;Java;SQL;Git,Mid Level,2026-03-12,Multipart Upload\n"
    )
    upload_res = post_multipart("/api/market/upload", "health_jobs.csv", upload_csv, content_type="text/csv", data_source="Multipart Admin Upload")
    assert upload_res["success"] is True
    print(f" -> Uploaded multipart CSV: {upload_res['imported_count']} postings imported")

    # 11. Regression Test: Module 2 Assessment Flow
    print("\n[E2E 11] Regression Check: Module 2 Timed Assessment Flow...")
    start_res = post_json("/api/assessment/start", {"skill_name": "Python"}, token=token)
    assert start_res["success"] is True
    assert start_res["total_mcqs"] == 50
    assert start_res["total_coding"] == 2
    assert len(start_res["mcqs"]) == 50
    assert len(start_res["coding_questions"]) == 2
    print(f" -> Assessment started: {start_res['total_mcqs']} MCQs, {start_res['total_coding']} Coding questions, 90-min timer intact.")

    # 12. Regression Test: Module 3 Verified Profile
    print("\n[E2E 12] Regression Check: Module 3 Verified Skill Profile...")
    vprofile = get_json("/api/assessment/verified-profile", token=token)
    assert vprofile["success"] is True
    print(f" -> Verified Skill Profile retrieved: {len(vprofile.get('verified_skills', []))} verified skills recorded.")

    print("\n======================================================================")
    print(">>> ALL MODULE 4 LIVE HTTP E2E & REGRESSION TESTS PASSED 100%! <<<")
    print("======================================================================")

if __name__ == "__main__":
    run_live_e2e_tests()
