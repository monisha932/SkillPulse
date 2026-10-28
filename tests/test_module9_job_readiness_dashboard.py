"""
Unit Tests for MODULE 9: JOB READINESS DASHBOARD (Career Skill Profile Engine)
Verifies:
- Title "CAREER SKILL PROFILE"
- User Information (Name, Target job role, Preferred domain, Career goal)
- Verified Skills (Skill, Verified proficiency, Assessment score)
- Required Job Skills (Skill, Required level, Job-market demand)
- Skill Gaps (Skill, Current level, Required level, Gap, Priority)
- Curriculum Progress (Completed modules, Current module, Remaining modules, Overall progress)
- Micro-Credentials (Earned credentials, In-progress credentials)
- Job Readiness / Skill Coverage (Transparent percentage, "Overall Skill Coverage: XX%", non-employment disclaimer)
- 6 Visualizations Datasets (Radar chart, Proficiency bars, Gap chart, Curriculum progress, Credential progress, Market demand)
- Final Actionable Recommendations (Top gaps, Highest-priority skills, Recommended next module, Assessment retake)
- API Endpoints (/api/readiness/dashboard, /api/readiness/summary, /api/readiness/recalculate)
"""

import unittest
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_db_connection, init_db
from backend.services.job_readiness_engine import (
    get_career_skill_profile,
    NON_EMPLOYMENT_DISCLAIMER
)

class TestModule9JobReadinessDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.test_user_id = 901
        cls.test_email = "readiness_test_student@example.com"

        conn = get_db_connection()
        cursor = conn.cursor()

        # Clean prior test fixtures
        cursor.execute("DELETE FROM users WHERE id = ? OR email = ?", (cls.test_user_id, cls.test_email))
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (cls.test_user_id,))
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (cls.test_user_id,))
        cursor.execute("DELETE FROM skill_assessment_history WHERE user_id = ?", (cls.test_user_id,))
        cursor.execute("DELETE FROM user_curriculums WHERE user_id = ?", (cls.test_user_id,))
        cursor.execute("DELETE FROM user_credentials WHERE user_id = ?", (cls.test_user_id,))
        cursor.execute("DELETE FROM job_readiness WHERE user_id = ?", (cls.test_user_id,))

        # 1. Create test user
        cursor.execute("""
        INSERT INTO users (id, name, email, password_hash, role)
        VALUES (?, 'Monisha & Pooja Tech Candidate', ?, 'hash123', 'student')
        """, (cls.test_user_id, cls.test_email))

        # 2. Create Career Profile
        cursor.execute("""
        INSERT INTO career_profiles (user_id, target_role_id, experience_level, education, declared_skills_json)
        VALUES (?, 'fullstack-dev', 'Entry-Level (0-1 yrs)', 'B.Tech Computer Science', ?)
        """, (cls.test_user_id, json.dumps([
            {"skill_name": "Python", "proficiency": "Intermediate"},
            {"skill_name": "SQL", "proficiency": "Intermediate"}
        ])))

        # 3. Seed Verified Skills (Modules 2 & 3)
        cursor.execute("""
        INSERT INTO verified_skills (
            user_id, skill_name, category, score_pct, proficiency_level,
            mcq_score, mcq_max, programming_score, programming_max, comparison_status
        ) VALUES
        (?, 'Python', 'Core Backend', 78.5, 'Intermediate', 38.5, 50.0, 40.0, 50.0, 'matched'),
        (?, 'SQL', 'Database & Query', 85.0, 'Advanced', 42.5, 50.0, 42.5, 50.0, 'exceeded')
        """, (cls.test_user_id, cls.test_user_id))

        # 4. Seed Assessment History (Module 8 preservation)
        cursor.execute("""
        INSERT INTO skill_assessment_history (user_id, skill_name, attempt_number, score_pct, proficiency_level, mcq_score, programming_score)
        VALUES
        (?, 'Python', 1, 45.0, 'Basic', 22.5, 22.5),
        (?, 'Python', 2, 78.5, 'Intermediate', 38.5, 40.0),
        (?, 'SQL', 1, 85.0, 'Advanced', 42.5, 42.5)
        """, (cls.test_user_id, cls.test_user_id, cls.test_user_id))

        # 5. Seed User Curriculum (Module 6)
        cursor.execute("""
        INSERT INTO user_curriculums (id, user_id, role_id, title, status, total_modules, completed_modules, adaptation_version)
        VALUES (9901, ?, 'fullstack-dev', 'Full-Stack Developer Micro-Credential Curriculum', 'active', 4, 2, 2)
        """, (cls.test_user_id,))

        cursor.execute("""
        INSERT INTO curriculum_modules (
            curriculum_id, module_order, title, skill_name, hours, status, progress_pct,
            current_proficiency, required_proficiency, difficulty, learning_objective, is_unlocked
        ) VALUES
        (9901, 1, 'Python Web API Architecture', 'Python', 4, 'completed', 100, 'Intermediate', 'Advanced', 'Intermediate', 'Build RESTful APIs with FastAPI', 1),
        (9901, 2, 'Relational Database Indexing', 'SQL', 4, 'completed', 100, 'Intermediate', 'Advanced', 'Advanced', 'Query execution tuning and CTEs', 1),
        (9901, 3, 'React Frontend State Management', 'React', 5, 'in_progress', 50, 'Not Assessed', 'Intermediate', 'Intermediate', 'Master Redux Toolkit and hooks', 1),
        (9901, 4, 'Docker & Container Orchestration', 'Docker', 4, 'pending', 0, 'Not Assessed', 'Intermediate', 'Intermediate', 'Containerize microservices', 0)
        """)

        # 6. Seed Micro-Credentials (Module 7)
        cursor.execute("""
        INSERT INTO user_credentials (
            credential_id, user_id, title, skill, domain, level, learning_objectives_json,
            requirements_json, modules_completed_json, assessment_score, practical_task,
            completion_pct, status, issue_date, verification_status, verification_code, accreditation_disclaimer
        ) VALUES
        (
            'CRED-TEST-PY', ?, 'Python for Data & Web Architecture', 'Python',
            'Full-Stack Engineering', 'Intermediate', '["FastAPI","NumPy"]', '["Python","FastAPI"]',
            '["Python Web API Architecture"]', 78.5, 'Deploy asynchronous API gateway',
            100.0, 'earned', '2026-10-10', 'Verified (Platform Generated)', 'PULSE-VER-PY-9901', 'Internal milestone'
        ),
        (
            'CRED-TEST-REACT', ?, 'Modern Frontend with React & State Architecture', 'React',
            'Frontend Engineering', 'Intermediate', '["Hooks","State"]', '["React","CSS"]',
            '[]', 0.0, 'Build responsive single-page web application',
            50.0, 'in_progress', NULL, 'In Progress', NULL, 'Internal milestone'
        )
        """, (cls.test_user_id, cls.test_user_id))

        conn.commit()
        conn.close()

    def test_01_career_skill_profile_structure(self):
        """Verifies get_career_skill_profile aggregates all required sections with correct keys and title."""
        profile = get_career_skill_profile(user_id=self.test_user_id, target_role_id="fullstack-dev")

        # 1. Title
        self.assertEqual(profile["title"], "CAREER SKILL PROFILE")

        # 2. User Information
        user_info = profile["user_information"]
        self.assertIn("Monisha & Pooja", user_info["name"])
        self.assertEqual(user_info["target_job_role"], "Full-Stack Web Developer")
        self.assertEqual(user_info["preferred_domain"], "Web & Software Engineering")
        self.assertTrue(len(user_info["career_goal"]) > 10)

        # 3. Verified Skills
        ver_skills = profile["verified_skills"]
        self.assertTrue(len(ver_skills) >= 2)
        py_ver = next(s for s in ver_skills if s["skill"] == "Python")
        self.assertEqual(py_ver["verified_proficiency"], "Intermediate")
        self.assertEqual(py_ver["assessment_score"], 78.5)

        # 4. Required Job Skills
        req_skills = profile["required_job_skills"]
        self.assertTrue(len(req_skills) >= 3)
        self.assertTrue(all("skill" in s and "required_level" in s and "job_market_demand" in s for s in req_skills))

        # 5. Skill Gaps
        gaps = profile["skill_gaps"]
        self.assertTrue(len(gaps) >= 3)
        self.assertTrue(all("skill" in g and "current_level" in g and "required_level" in g and "gap" in g and "priority" in g for g in gaps))

        # 6. Curriculum Progress
        curr = profile["curriculum_progress"]
        self.assertEqual(curr["total_modules"], 4)
        self.assertEqual(curr["completed_count"], 2)
        self.assertEqual(curr["remaining_count"], 2)
        self.assertEqual(curr["overall_progress"], 50.0)
        self.assertIsNotNone(curr["current_module"])
        self.assertEqual(curr["current_module"]["skill_name"], "React")

        # 7. Micro-Credentials
        creds = profile["micro_credentials"]
        self.assertEqual(creds["earned_count"], 1)
        self.assertEqual(creds["in_progress_count"], 1)
        self.assertEqual(creds["earned_credentials"][0]["skill"], "Python")

    def test_02_job_readiness_skill_coverage_and_disclaimer(self):
        """Verifies transparent skill coverage calculation and mandatory non-employment disclaimer."""
        profile = get_career_skill_profile(user_id=self.test_user_id, target_role_id="fullstack-dev")
        jr = profile["job_readiness"]

        # Transparent coverage percentage
        coverage = jr["overall_skill_coverage"]
        self.assertIsInstance(coverage, float)
        self.assertTrue(0.0 <= coverage <= 100.0)
        self.assertEqual(jr["overall_skill_coverage_display"], f"Overall Skill Coverage: {coverage}%")

        # Non-employment disclaimer check
        self.assertIn("Disclaimer", jr["disclaimer"])
        self.assertIn("NOT represent or guarantee a probability", jr["disclaimer"])
        self.assertIn("employment", jr["disclaimer"])

        # Metric breakdown
        self.assertTrue(jr["skills_fully_met_count"] >= 1)
        self.assertTrue(jr["total_skills_evaluated"] >= 3)

    def test_03_all_six_visualizations_data(self):
        """Verifies that all 6 required visualization datasets are computed and correctly shaped."""
        profile = get_career_skill_profile(user_id=self.test_user_id, target_role_id="fullstack-dev")
        vis = profile["visualizations"]

        # 1. Skill Radar Chart
        radar = vis["skill_radar_chart"]
        self.assertIn("labels", radar)
        self.assertIn("verified_series", radar)
        self.assertIn("required_series", radar)
        self.assertEqual(len(radar["labels"]), len(radar["verified_series"]))
        self.assertEqual(len(radar["labels"]), len(radar["required_series"]))

        # 2. Skill Proficiency Bars
        prof_bars = vis["skill_proficiency_bars"]
        self.assertTrue(len(prof_bars) >= 2)
        self.assertTrue(all("skill" in b and "score_pct" in b and "proficiency_level" in b for b in prof_bars))

        # 3. Skill Gap Chart
        gap_chart = vis["skill_gap_chart"]
        self.assertTrue(len(gap_chart) >= 3)
        self.assertTrue(all("skill" in g and "verified_level_num" in g and "required_level_num" in g for g in gap_chart))

        # 4. Curriculum Progress
        curr_chart = vis["curriculum_progress"]
        self.assertEqual(curr_chart["completed"], 2)
        self.assertEqual(curr_chart["in_progress"], 1)
        self.assertEqual(curr_chart["total"], 4)
        self.assertEqual(curr_chart["percentage"], 50.0)

        # 5. Credential Progress
        cred_chart = vis["credential_progress"]
        self.assertEqual(cred_chart["earned"], 1)
        self.assertEqual(cred_chart["in_progress"], 1)
        self.assertEqual(cred_chart["completion_rate"], 50.0)

        # 6. Job-Market Demand Chart
        demand_chart = vis["job_market_demand_chart"]
        self.assertTrue(len(demand_chart) >= 3)
        self.assertTrue(all("skill" in d and "demand_percentage" in d and "trend_status" in d for d in demand_chart))

    def test_04_final_recommendations(self):
        """Verifies final recommendations generate top gaps, high priorities, next module, and assessment retake."""
        profile = get_career_skill_profile(user_id=self.test_user_id, target_role_id="fullstack-dev")
        recs = profile["final_recommendations"]

        # Top remaining skill gaps
        self.assertIn("top_remaining_skill_gaps", recs)
        self.assertTrue(isinstance(recs["top_remaining_skill_gaps"], list))

        # Highest-priority skills
        self.assertIn("highest_priority_skills", recs)
        self.assertTrue(len(recs["highest_priority_skills"]) >= 1)

        # Recommended next module
        next_mod = recs["recommended_next_module"]
        self.assertIsNotNone(next_mod)
        self.assertEqual(next_mod["skill"], "React")
        self.assertIn("React", next_mod["title"])

        # Recommended assessment/retake
        retake = recs["recommended_assessment_retake"]
        self.assertIsNotNone(retake)
        self.assertIn("skill", retake)
        self.assertIn("rationale", retake)

    def test_05_job_readiness_database_persistence(self):
        """Verifies that running profile computation persists updated metrics to job_readiness table."""
        profile = get_career_skill_profile(user_id=self.test_user_id, target_role_id="fullstack-dev")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_readiness WHERE user_id = ?", (self.test_user_id,))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row["role_id"], "fullstack-dev")
        self.assertAlmostEqual(row["overall_readiness_pct"], profile["job_readiness"]["overall_skill_coverage"], places=1)
        self.assertEqual(row["credentials_earned"], 1)

    def test_06_api_endpoints(self):
        """Tests /api/readiness/dashboard, /api/readiness/summary, and /api/readiness/recalculate endpoints."""
        headers = {"Authorization": f"Bearer {self.test_user_id}"}

        # 1. GET /api/readiness/dashboard
        resp_dash = self.client.get("/api/readiness/dashboard?target_role_id=fullstack-dev", headers=headers)
        self.assertEqual(resp_dash.status_code, 200)
        dash_json = resp_dash.json()
        self.assertTrue(dash_json["success"])
        self.assertEqual(dash_json["profile"]["title"], "CAREER SKILL PROFILE")
        self.assertIn("job_readiness", dash_json["profile"])
        self.assertIn("visualizations", dash_json["profile"])

        # 2. GET /api/readiness/summary
        resp_sum = self.client.get("/api/readiness/summary?target_role_id=fullstack-dev", headers=headers)
        self.assertEqual(resp_sum.status_code, 200)
        sum_json = resp_sum.json()
        self.assertTrue(sum_json["success"])
        self.assertIn("overall_skill_coverage", sum_json)
        self.assertEqual(sum_json["curriculum_progress"], 50.0)
        self.assertIn("disclaimer", sum_json)

        # 3. POST /api/readiness/recalculate
        resp_recalc = self.client.post(
            "/api/readiness/recalculate",
            json={"target_role_id": "fullstack-dev"},
            headers=headers
        )
        self.assertEqual(resp_recalc.status_code, 200)
        recalc_json = resp_recalc.json()
        self.assertTrue(recalc_json["success"])
        self.assertEqual(recalc_json["profile"]["title"], "CAREER SKILL PROFILE")

if __name__ == "__main__":
    unittest.main()
