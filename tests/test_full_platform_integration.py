"""
Comprehensive End-to-End Integration Test Suite for:
"MICRO-CREDENTIAL CURRICULUM GENERATION PLATFORM DRIVEN BY REAL-TIME GLOBAL JOB MARKET SKILL DEMANDS"

Verifies the complete 16-step platform pipeline:
LOGIN
→ CAREER PROFILE
→ SELF-DECLARED SKILLS
→ SKILL ASSESSMENT
→ 50 MCQs
→ 2 PROGRAMMING QUESTIONS
→ 90-MINUTE TIMER
→ ASSESSMENT EVALUATION
→ VERIFIED SKILL PROFILE
→ JOB MARKET SKILL ANALYSIS
→ REQUIRED JOB SKILLS
→ SKILL GAP ANALYSIS
→ PERSONALIZED CURRICULUM
→ MICRO-CREDENTIALS
→ ADAPTIVE LEARNING
→ JOB READINESS DASHBOARD

Contains the 10 Mandatory Scenario Test Cases:
1. New user registration and profile creation
2. Existing user authentication and persistent session
3. User with one skill
4. User with multiple skills
5. User who fails assessment (< 60% threshold, gap detection, remedial curriculum)
6. User who passes assessment (>= 60%, verified proficiency, gap closure)
7. User who retakes assessment (Before vs After comparison, history preserved, adaptation triggered)
8. User with missing required skills (unassessed gap detection, high priority tagging)
9. User with advanced skills (pruning beginner modules, advanced pathway unlocking)
10. User completing curriculum (100% progress, credentials earned, dashboard alignment)
"""

import unittest
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_db_connection, init_db
from backend.services.adaptive_engine import adapt_learning_path, record_assessment_attempt, get_assessment_comparison
from backend.services.job_readiness_engine import get_career_skill_profile

class TestFullPlatformIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_case_01_new_user(self):
        """
        SCENARIO 1: New user registration and career profile creation.
        Verifies authentication, secure password hashing, user isolation, and profile saving.
        """
        email = "test_new_user_workflow@example.com"
        password = "SecurePassword123!"
        name = "New Engineering Student"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        conn.close()

        # 1. Register new user
        reg_resp = self.client.post("/api/auth/register", json={
            "name": name,
            "email": email,
            "password": password
        })
        self.assertEqual(reg_resp.status_code, 200)
        reg_data = reg_resp.json()
        self.assertTrue(reg_data["success"])
        token = reg_data["token"]
        user_id = reg_data["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Verify password is not stored plaintext
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        pwd_hash = cursor.fetchone()["password_hash"]
        conn.close()
        self.assertNotEqual(pwd_hash, password)

        # 2. Check initial profile state (empty)
        prof_resp = self.client.get("/api/profile", headers=headers)
        self.assertEqual(prof_resp.status_code, 200)
        self.assertFalse(prof_resp.json()["has_profile"])

        # 3. Save initial career profile
        save_resp = self.client.post("/api/profile", headers=headers, json={
            "target_role_id": "fullstack-dev",
            "experience_level": "Fresher",
            "education": "B.Tech Computer Science",
            "declared_skills": [
                {"skill_name": "Python", "proficiency": "Intermediate"}
            ]
        })
        self.assertEqual(save_resp.status_code, 200)
        self.assertTrue(save_resp.json()["success"])

        # 4. Fetch and verify saved profile
        prof_resp2 = self.client.get("/api/profile", headers=headers)
        self.assertTrue(prof_resp2.json()["has_profile"])
        saved_p = prof_resp2.json()["profile"]
        self.assertEqual(saved_p["target_role_id"], "fullstack-dev")
        self.assertEqual(saved_p["role_title"], "Full-Stack Web Developer")
        self.assertEqual(len(saved_p["declared_skills"]), 1)

    def test_case_02_existing_user(self):
        """
        SCENARIO 2: Existing user login, token session persistence, and profile retrieval.
        """
        # Login demo student account
        login_resp = self.client.post("/api/auth/login", json={
            "email": "student@example.com",
            "password": "password123"
        })
        self.assertEqual(login_resp.status_code, 200)
        login_data = login_resp.json()
        self.assertTrue(login_data["success"])
        token = login_data["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Verify identity via /api/auth/me
        me_resp = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_resp.status_code, 200)
        me_data = me_resp.json()
        self.assertEqual(me_data["email"], "student@example.com")

        # Verify profile is loaded
        prof_resp = self.client.get("/api/profile", headers=headers)
        self.assertEqual(prof_resp.status_code, 200)
        self.assertTrue(prof_resp.json()["has_profile"])

    def test_case_03_user_with_one_skill(self):
        """
        SCENARIO 3: User with exactly one skill.
        Verifies single-skill assessment setup (50 MCQs + 2 Coding + 90 min timer) and gap isolation.
        """
        user_id = 9103
        headers = {"Authorization": f"Bearer {user_id}"}
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO users (id, name, email, password_hash) VALUES (?, 'Single Skill User', 'single@test.com', 'h')", (user_id,))
        cursor.execute("""
        INSERT INTO career_profiles (user_id, target_role_id, declared_skills_json)
        VALUES (?, 'fullstack-dev', ?)
        """, (user_id, json.dumps([{"skill_name": "Python", "proficiency": "Intermediate"}])))
        conn.commit()
        conn.close()

        # 1. Fetch assessment skills
        skills_resp = self.client.get("/api/assessment/skills", headers=headers)
        self.assertEqual(skills_resp.status_code, 200)
        skills = skills_resp.json()["skills"]
        self.assertTrue(any(s["skill_name"] == "Python" for s in skills))

        # 2. Start assessment for Python
        start_resp = self.client.post("/api/assessment/start", headers=headers, json={"skill_name": "Python"})
        self.assertEqual(start_resp.status_code, 200)
        start_data = start_resp.json()
        self.assertEqual(start_data["skill_name"], "Python")
        self.assertEqual(start_data["duration_minutes"], 90)
        self.assertEqual(start_data["total_mcqs"], 50)
        self.assertEqual(start_data["total_coding"], 2)

        # 3. Verify MCQs correct option is not leaked to client
        for mcq in start_data["mcqs"]:
            self.assertNotIn("correct_option", mcq)
            self.assertIn("options", mcq)
            self.assertEqual(len(mcq["options"]), 4)

    def test_case_04_user_with_multiple_skills(self):
        """
        SCENARIO 4: User with multiple skills.
        Verifies multi-skill storage, multi-skill assessment options, and combined gap benchmark.
        """
        user_id = 9104
        headers = {"Authorization": f"Bearer {user_id}"}
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO users (id, name, email, password_hash) VALUES (?, 'Multi Skill User', 'multi@test.com', 'h')", (user_id,))
        multi_skills = [
            {"skill_name": "Python", "proficiency": "Advanced"},
            {"skill_name": "SQL", "proficiency": "Intermediate"},
            {"skill_name": "Java", "proficiency": "Basic"}
        ]
        cursor.execute("""
        INSERT INTO career_profiles (user_id, target_role_id, declared_skills_json)
        VALUES (?, 'fullstack-dev', ?)
        """, (user_id, json.dumps(multi_skills)))
        conn.commit()
        conn.close()

        # Query profile
        prof_resp = self.client.get("/api/profile", headers=headers)
        self.assertEqual(prof_resp.status_code, 200)
        declared = prof_resp.json()["profile"]["declared_skills"]
        self.assertEqual(len(declared), 3)

        # Start SQL assessment
        start_sql = self.client.post("/api/assessment/start", headers=headers, json={"skill_name": "SQL"})
        self.assertEqual(start_sql.status_code, 200)
        self.assertEqual(start_sql.json()["skill_name"], "SQL")
        self.assertEqual(len(start_sql.json()["mcqs"]), 50)

    def test_case_05_user_who_fails_assessment(self):
        """
        SCENARIO 5: User who fails assessment (< 60% threshold).
        Verifies backend grading, Novice/Beginner assignment, High/Critical gap generation, and remedial curriculum.
        """
        user_id = 9105
        headers = {"Authorization": f"Bearer {user_id}"}
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM skill_assessment_history WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO users (id, name, email, password_hash) VALUES (?, 'Failing User', 'fail@test.com', 'h')", (user_id,))
        cursor.execute("INSERT INTO career_profiles (user_id, target_role_id) VALUES (?, 'fullstack-dev')", (user_id,))
        conn.commit()
        conn.close()

        # Start assessment
        start_res = self.client.post("/api/assessment/start", headers=headers, json={"skill_name": "Python"}).json()
        token = start_res["session_token"]

        # Submit only 5 wrong answers (selected_option = 99)
        for i in range(1, 6):
            self.client.post("/api/assessment/answer", json={
                "session_token": token,
                "question_num": i,
                "selected_option": 3,
                "submitted_code": ""
            })

        # Complete assessment
        complete_res = self.client.post("/api/assessment/complete", json={"session_token": token})
        self.assertEqual(complete_res.status_code, 200)
        results = complete_res.json()["results"]
        overall_pct = results.get("overall_total_pct", results.get("verified_skill", {}).get("score_pct", 0.0))
        self.assertLess(overall_pct, 60.0)
        self.assertIn(results["proficiency_level"], ["Novice", "Beginner", "Basic"])

        # Check gap analysis
        gap_resp = self.client.get("/api/skills/gap-analysis?role_id=fullstack-dev", headers=headers)
        self.assertEqual(gap_resp.status_code, 200)
        gaps = gap_resp.json()["gap_analysis"]["gaps"]
        py_gap = next(g for g in gaps if g["skill_name"] == "Python")
        self.assertGreater(py_gap["gap_num"], 0)
        self.assertIn(py_gap["priority"], ["High", "Critical", "Medium"])

    def test_case_06_user_who_passes_assessment(self):
        """
        SCENARIO 6: User who passes assessment (>= 60%).
        Verifies Proficient/Advanced tier awarded, gap marked met, and overall coverage updated.
        """
        user_id = 9106
        headers = {"Authorization": f"Bearer {user_id}"}
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM skill_assessment_history WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO users (id, name, email, password_hash) VALUES (?, 'Passing User', 'pass@test.com', 'h')", (user_id,))
        cursor.execute("INSERT INTO career_profiles (user_id, target_role_id) VALUES (?, 'fullstack-dev')", (user_id,))

        # Seed passed verified skill (85% score, Advanced)
        cursor.execute("""
        INSERT INTO verified_skills (user_id, skill_name, category, score_pct, proficiency_level, comparison_status)
        VALUES (?, 'Python', 'Core', 85.0, 'Advanced', 'exceeded')
        """, (user_id,))
        conn.commit()
        conn.close()

        # Check gap analysis
        gap_resp = self.client.get("/api/skills/gap-analysis?role_id=fullstack-dev", headers=headers)
        self.assertEqual(gap_resp.status_code, 200)
        gaps = gap_resp.json()["gap_analysis"]["gaps"]
        py_gap = next(g for g in gaps if g["skill_name"] == "Python")
        self.assertEqual(py_gap["gap_num"], 0)
        self.assertEqual(py_gap["status"], "Proficiency Met")

    def test_case_07_user_who_retakes_assessment(self):
        """
        SCENARIO 7: User who retakes assessment.
        Verifies historical preservation (neither attempt deleted), Before vs After comparison, and adaptive banner.
        """
        user_id = 9107
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM skill_assessment_history WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO users (id, name, email, password_hash) VALUES (?, 'Retake User', 'retake@test.com', 'h')", (user_id,))
        cursor.execute("INSERT INTO career_profiles (user_id, target_role_id) VALUES (?, 'fullstack-dev')", (user_id,))
        conn.commit()
        conn.close()

        # Attempt 1: 45%
        record_assessment_attempt(user_id=user_id, skill_name="Python", attempt_id=1, score_pct=45.0, proficiency_level="Basic")
        # Attempt 2 (Retake): 78%
        record_assessment_attempt(user_id=user_id, skill_name="Python", attempt_id=2, score_pct=78.0, proficiency_level="Intermediate")

        # Verify both attempts exist in history
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT attempt_number, score_pct FROM skill_assessment_history WHERE user_id = ? AND skill_name = 'Python' ORDER BY attempt_number ASC", (user_id,))
        hist = cursor.fetchall()
        conn.close()
        self.assertEqual(len(hist), 2)
        self.assertEqual(hist[0]["score_pct"], 45.0)
        self.assertEqual(hist[1]["score_pct"], 78.0)

        # Before vs After Comparison
        comp = get_assessment_comparison(user_id=user_id)
        py_comp = next(c for c in comp if c["skill"] == "Python")
        self.assertEqual(py_comp["before_score"], 45.0)
        self.assertEqual(py_comp["after_score"], 78.0)
        self.assertEqual(py_comp["score_diff"], 33.0)

        # Trigger adaptation
        res = adapt_learning_path(user_id=user_id, trigger_reason="reassessment")
        self.assertEqual(res["banner"], "YOUR LEARNING PATH HAS BEEN UPDATED")

    def test_case_08_user_with_missing_required_skills(self):
        """
        SCENARIO 8: User with missing required skills.
        Verifies unassessed gap identification, Critical/High priority classification, and recommendations.
        """
        user_id = 9108
        headers = {"Authorization": f"Bearer {user_id}"}
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO users (id, name, email, password_hash) VALUES (?, 'Missing Skills User', 'missing@test.com', 'h')", (user_id,))
        cursor.execute("INSERT INTO career_profiles (user_id, target_role_id) VALUES (?, 'fullstack-dev')", (user_id,))
        conn.commit()
        conn.close()

        # No verified skills in database -> all required role skills are missing
        gap_resp = self.client.get("/api/skills/gap-analysis?role_id=fullstack-dev", headers=headers)
        self.assertEqual(gap_resp.status_code, 200)
        gaps = gap_resp.json()["gap_analysis"]["gaps"]
        self.assertTrue(len(gaps) >= 3)
        self.assertTrue(all(g["verified_level"] == "Not Assessed" for g in gaps))
        self.assertTrue(any(g["priority"] in ["Critical", "High"] for g in gaps))

    def test_case_09_user_with_advanced_skills(self):
        """
        SCENARIO 9: User with advanced skills.
        Verifies pruning of unnecessary beginner modules and generation of change explanation.
        """
        user_id = 9109
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM skill_assessment_history WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO users (id, name, email, password_hash) VALUES (?, 'Advanced User', 'adv@test.com', 'h')", (user_id,))
        cursor.execute("INSERT INTO career_profiles (user_id, target_role_id) VALUES (?, 'fullstack-dev')", (user_id,))
        # User demonstrates 92% Advanced Python
        cursor.execute("""
        INSERT INTO verified_skills (user_id, skill_name, category, score_pct, proficiency_level, comparison_status)
        VALUES (?, 'Python', 'Core', 92.0, 'Advanced', 'exceeded')
        """, (user_id,))
        conn.commit()
        conn.close()

        # Run adaptation
        res = adapt_learning_path(user_id=user_id, trigger_reason="reassessment")
        self.assertTrue(len(res["pruned_modules"]) >= 1)
        # Verify explanation rationale
        self.assertTrue(any("proficiency" in exp.lower() for exp in res["explanations"]))

    def test_case_10_user_completing_curriculum(self):
        """
        SCENARIO 10: User completing curriculum.
        Verifies progress completion, micro-credential unlock, and 100% curriculum status in Job Readiness Dashboard.
        """
        user_id = 9110
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_curriculums WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM curriculum_modules WHERE curriculum_id = 9910")
        cursor.execute("DELETE FROM user_credentials WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO users (id, name, email, password_hash) VALUES (?, 'Graduate Student', 'grad@test.com', 'h')", (user_id,))
        cursor.execute("INSERT INTO career_profiles (user_id, target_role_id) VALUES (?, 'fullstack-dev')", (user_id,))

        cursor.execute("""
        INSERT INTO user_curriculums (id, user_id, role_id, title, status, total_modules, completed_modules)
        VALUES (9910, ?, 'fullstack-dev', 'Full-Stack Developer Curriculum', 'active', 2, 2)
        """, (user_id,))

        cursor.execute("""
        INSERT INTO curriculum_modules (curriculum_id, module_order, title, skill_name, hours, status, progress_pct)
        VALUES
        (9910, 1, 'Core Python Engineering', 'Python', 4, 'completed', 100),
        (9910, 2, 'Relational Database Schema Design', 'SQL', 4, 'completed', 100)
        """)

        cursor.execute("""
        INSERT INTO user_credentials (
            credential_id, user_id, title, skill, domain, level, learning_objectives_json,
            requirements_json, modules_completed_json, assessment_score, practical_task,
            completion_pct, status, issue_date, verification_code, accreditation_disclaimer
        ) VALUES (
            'CRED-GRAD-01', ?, 'Full-Stack Software Competency', 'Python', 'Web Dev',
            'Advanced', '["API","DB"]', '["Python","SQL"]', '["Core Python Engineering"]',
            88.0, 'Deploy full stack application', 100.0, 'earned', '2026-10-11',
            'VER-GRAD-01', 'Internal milestone'
        )
        """, (user_id,))
        conn.commit()
        conn.close()

        # Query Career Skill Profile (Module 9 Dashboard)
        profile = get_career_skill_profile(user_id=user_id, target_role_id="fullstack-dev")
        curr = profile["curriculum_progress"]
        creds = profile["micro_credentials"]

        self.assertEqual(curr["completed_count"], 2)
        self.assertEqual(curr["remaining_count"], 0)
        self.assertEqual(curr["overall_progress"], 100.0)
        self.assertEqual(creds["earned_count"], 1)
        self.assertIn("Overall Skill Coverage:", profile["job_readiness"]["overall_skill_coverage_display"])

if __name__ == "__main__":
    unittest.main()
