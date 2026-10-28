import unittest
import json
import io
import asyncio
from starlette.datastructures import UploadFile
from backend.database import get_db_connection, init_db
from backend.models import CareerProfileRequest
from backend.routers.auth import save_career_profile
from backend.services.market_analyzer import (
    analyze_target_role_skills,
    import_job_postings,
    import_csv_postings,
    get_market_filters,
    seed_default_job_postings_if_empty
)
from backend.routers.market_demand import (
    get_skill_demand,
    get_filters,
    create_job_posting,
    import_json_data,
    import_csv_data,
    upload_job_market_file,
    JobPostingCreate,
    JsonImportRequest,
    CsvImportRequest
)

class TestModule4MarketAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_default_job_postings_if_empty()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create or fetch test user
        cursor.execute("SELECT id FROM users WHERE email = 'm4_tester@platform.edu'")
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("Module 4 Tester", "m4_tester@platform.edu", "dummyhash", "student")
            )
            conn.commit()
            cursor.execute("SELECT id FROM users WHERE email = 'm4_tester@platform.edu'")
            cls.test_user_id = cursor.fetchone()["id"]
        else:
            cls.test_user_id = row["id"]
        conn.close()

    def test_01_seed_data_loaded_and_analyzed(self):
        """Verify initial curated job postings load and can be analyzed for fullstack-dev."""
        analysis = analyze_target_role_skills("fullstack-dev")
        self.assertIsNotNone(analysis)
        self.assertIn("target_role", analysis)
        self.assertEqual(analysis["target_role"]["role_id"], "fullstack-dev")
        self.assertGreater(analysis["total_postings_analyzed"], 0)

        # Check required skills from specification: JavaScript, React, Java, SQL, Git, REST API, HTML/CSS
        skill_names = [s["skill_name"] for s in analysis["skills"]]
        required_specs = ["JavaScript", "React", "Java", "SQL", "Git", "REST API", "HTML/CSS"]
        for req in required_specs:
            self.assertIn(req, skill_names, f"Expected {req} in analyzed skills for fullstack-dev")

    def test_02_skill_demand_percentage_formula(self):
        """Verify mathematical demand % = (frequency / total_postings) * 100."""
        analysis = analyze_target_role_skills("fullstack-dev")
        total = analysis["total_postings_analyzed"]
        self.assertGreater(total, 0)

        for s in analysis["skills"]:
            expected_pct = round((s["frequency"] / total) * 100.0, 1)
            self.assertEqual(s["demand_percentage"], expected_pct)
            self.assertGreaterEqual(s["demand_percentage"], 0.0)
            self.assertLessEqual(s["demand_percentage"], 100.0)

    def test_03_get_skill_demand_endpoint(self):
        """Test get_skill_demand router function."""
        res = get_skill_demand(target_role_id="fullstack-dev", user_id=None)
        self.assertTrue(res.get("success"))
        self.assertEqual(res["target_role"]["role_id"], "fullstack-dev")
        self.assertIsInstance(res["top_skills"], list)
        self.assertIsInstance(res["industry_distribution"], list)
        self.assertIsInstance(res["location_distribution"], list)
        self.assertIsInstance(res["experience_distribution"], list)
        self.assertTrue(len(res["data_sources"]) > 0)

    def test_04_filters_endpoint(self):
        """Test get_filters router function."""
        res = get_filters(target_role_id="fullstack-dev")
        self.assertTrue(res.get("success"))
        filters = res.get("filters", {})
        self.assertIn("industries", filters)
        self.assertIn("locations", filters)
        self.assertIn("experience_levels", filters)
        self.assertTrue(len(filters["industries"]) > 0)

    def test_05_filtered_skill_demand(self):
        """Test filtered analysis for Remote postings."""
        res = get_skill_demand(target_role_id="fullstack-dev", location="Remote", user_id=None)
        self.assertTrue(res.get("success"))
        for loc in res["location_distribution"]:
            self.assertIn("remote", loc["location"].lower())

    def test_06_ingest_single_job_posting_api(self):
        """Test create_job_posting router endpoint."""
        posting = JobPostingCreate(
            job_title="Lead Full Stack Architect",
            target_role_id="fullstack-dev",
            company="Antigravity Global Labs",
            industry="Artificial Intelligence",
            location="Remote",
            required_skills=["JavaScript", "React", "Python", "GraphQL", "Docker"],
            experience_level="Senior Level",
            data_source="Automated Unit Test API"
        )
        res = create_job_posting(posting)
        self.assertTrue(res.get("success"))
        self.assertEqual(res["result"]["imported_count"], 1)

    def test_07_batch_json_import(self):
        """Test import_json_data router endpoint."""
        batch = JsonImportRequest(
            data_source="Batch JSON Test Suite",
            postings=[
                JobPostingCreate(
                    job_title="Full Stack Engineer II",
                    target_role_id="fullstack-dev",
                    company="CloudPeak Software",
                    industry="SaaS & Cloud Platforms",
                    location="Seattle, WA",
                    required_skills=["JavaScript", "React", "Java", "SQL", "Git"],
                    experience_level="Mid Level"
                ),
                JobPostingCreate(
                    job_title="Junior Full Stack Developer",
                    target_role_id="fullstack-dev",
                    company="Startup Innovations",
                    industry="FinTech",
                    location="New York, NY",
                    required_skills=["JavaScript", "React", "HTML/CSS", "Git", "REST API"],
                    experience_level="Entry-Level"
                )
            ]
        )
        res = import_json_data(batch)
        self.assertTrue(res.get("success"))
        self.assertEqual(res["imported_count"], 2)

    def test_08_batch_csv_import(self):
        """Test import_csv_data router endpoint."""
        csv_content = (
            "job_title,target_role_id,company,industry,location,required_skills,experience_level,posting_date,data_source\n"
            "Full Stack Web Dev,fullstack-dev,Alpha Corp,FinTech,Remote,JavaScript;React;SQL;Git,Mid Level,2026-03-01,CSV Test Suite\n"
            "Cloud Full Stack,fullstack-dev,Beta Systems,Technology,Austin TX,Java;Spring;SQL;Docker;REST API,Senior Level,2026-03-02,CSV Test Suite\n"
        )
        req = CsvImportRequest(csv_content=csv_content, data_source="CSV Test Suite")
        res = import_csv_data(req)
        self.assertTrue(res.get("success"))
        self.assertEqual(res["imported_count"], 2)

    def test_09_admin_file_upload_csv(self):
        """Test upload_job_market_file endpoint for CSV."""
        csv_bytes = (
            b"job_title,target_role_id,company,industry,location,required_skills,experience_level,posting_date,data_source\n"
            b"Platform Full Stack,fullstack-dev,Upload Tech,Healthcare,Remote,JavaScript;React;Java;SQL;Git,Mid Level,2026-03-05,Upload Test\n"
        )
        upload = UploadFile(filename="test_postings.csv", file=io.BytesIO(csv_bytes))
        res = asyncio.run(upload_job_market_file(file=upload, data_source="Admin Multipart CSV"))
        self.assertTrue(res.get("success"))
        self.assertEqual(res["imported_count"], 1)

    def test_10_admin_file_upload_json(self):
        """Test upload_job_market_file endpoint for JSON."""
        json_data = [
            {
                "job_title": "AI Full Stack Specialist",
                "target_role_id": "ai-ml-engineer",
                "company": "NeuroLink AI",
                "industry": "Artificial Intelligence",
                "location": "San Francisco, CA",
                "required_skills": ["Python", "PyTorch", "FastAPI", "Docker"],
                "experience_level": "Mid Level",
                "data_source": "Admin Multipart JSON"
            }
        ]
        json_bytes = json.dumps(json_data).encode("utf-8")
        upload = UploadFile(filename="test_postings.json", file=io.BytesIO(json_bytes))
        res = asyncio.run(upload_job_market_file(file=upload, data_source=None))
        self.assertTrue(res.get("success"))
        self.assertEqual(res["imported_count"], 1)

    def test_11_role_connection_with_user_career_profile(self):
        """Verify get_skill_demand connects with user's target role in career profile."""
        # 1. Save profile targeting ai-ml-engineer for test user
        save_career_profile(
            req=CareerProfileRequest(
                target_role_id="ai-ml-engineer",
                declared_skills=[{"skill_name": "Python", "self_rating": "Intermediate"}],
                experience_level="Fresher",
                degree_major="B.Tech AI"
            ),
            user_id=self.test_user_id
        )

        # 2. Call skill demand without target_role_id -> should resolve to ai-ml-engineer via user_id
        res = get_skill_demand(target_role_id=None, user_id=self.test_user_id)
        self.assertTrue(res.get("success"))
        self.assertEqual(res["target_role"]["role_id"], "ai-ml-engineer")
        self.assertIn("Python", [s["skill_name"] for s in res["skills"]])

if __name__ == "__main__":
    unittest.main()
