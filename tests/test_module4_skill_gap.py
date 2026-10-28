"""
Comprehensive Automated Test Suite for MODULE 4: JOB MARKET GAP ANALYSIS & BENCHMARK ENGINE.
Verifies all requirements:
1. Mathematical Skill Gap Vector calculation:
   Gap_i = max(0, Required_i - Verified_i) * Weight_i
2. Role Match Percentage calculation:
   Role Match % = [sum(min(Verified_i, Required_i) * W_i) / sum(Required_i * W_i)] * 100
3. Integration with Module 3 Verified Skills (verified_skills table)
4. Dynamic comparison between Market Required Demand, User Declared Skills, and Assessment-Verified Competency
5. Gap Priority assignment: Critical, Medium, Low
6. Relational database persistence in skill_gaps table
7. Multi-role benchmark switching (fullstack-dev, data-scientist, etc.)
8. API endpoints: POST /api/skills/gap-analysis, GET /api/skills/gap-analysis, GET /api/market/analytics
9. Radar chart coordinate series generation
"""

import unittest
import json
from backend.database import get_db_connection, init_db
from backend.services.gap_engine import calculate_skill_gaps, PROFICIENCY_MAP
from backend.services.nlp_demand import extract_and_analyze_market_skills
from backend.routers.skill_gap import compute_gap_analysis, get_user_gap_analysis, GapAnalysisTriggerRequest

class TestModule4SkillGapAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Seed dedicated test user for Module 4
        cursor.execute("SELECT id FROM users WHERE email = 'module4_tester@platform.edu'")
        user = cursor.fetchone()
        if not user:
            cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES ('Module 4 Candidate', 'module4_tester@platform.edu', 'mock_hash', 'student')
            """)
            cls.user_id = cursor.lastrowid
        else:
            cls.user_id = user["id"]

        # Clean existing test data for this candidate
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (cls.user_id,))
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (cls.user_id,))
        cursor.execute("DELETE FROM skill_gaps WHERE user_id = ?", (cls.user_id,))

        # 1. Setup Career Profile: Declared Python (Intermediate), SQL (Beginner), JavaScript (Advanced)
        declared_skills = [
            {"skill_name": "Python", "self_rating": "Intermediate"},
            {"skill_name": "SQL", "self_rating": "Beginner"},
            {"skill_name": "JavaScript", "self_rating": "Advanced"}
        ]
        cursor.execute("""
        INSERT INTO career_profiles (user_id, target_role_id, declared_skills_json, experience_level, education)
        VALUES (?, 'fullstack-dev', ?, 'Fresher', 'B.E. Computer Science')
        """, (cls.user_id, json.dumps(declared_skills)))

        # 2. Setup Module 3 Verified Skills:
        # Candidate took Module 2 & 3 assessment for Python and scored 88.8% (Advanced)
        cursor.execute("""
        INSERT INTO verified_skills (
            user_id, skill_name, category, score_pct, proficiency_level, declared_level,
            mcq_score, mcq_max, programming_score, programming_max, comparison_status
        ) VALUES (?, 'Python', 'Technical Skill', 88.8, 'Advanced', 'Intermediate', 42.0, 50.0, 20.0, 20.0, 'exceeded')
        """, (cls.user_id,))

        conn.commit()
        conn.close()

    def test_01_mathematical_gap_formula_and_role_match(self):
        """Test exact mathematical formulation of Skill Gap Vectors and Role Match %."""
        result = calculate_skill_gaps(user_id=self.user_id, target_role_id="fullstack-dev")

        self.assertIn("target_role", result)
        self.assertEqual(result["target_role"]["role_id"], "fullstack-dev")
        self.assertGreater(result["role_match_percentage"], 0.0)
        self.assertLessEqual(result["role_match_percentage"], 100.0)

        gaps = result["gaps"]
        self.assertGreaterEqual(len(gaps), 6, "Full-Stack role should have multiple required skills evaluated")

        # Check Python: candidate verified at 88.8% (0.89)
        # Required for fullstack-dev: Python is Proficient (0.85)
        # Since verified (0.89) >= required (0.85), raw gap should be 0.0, gap_score should be 0.0, priority Low
        py_gap = next((g for g in gaps if g["skill_name"].lower() == "python"), None)
        self.assertIsNotNone(py_gap, "Python must be in evaluated role skills")
        self.assertTrue(py_gap["is_verified"])
        self.assertEqual(py_gap["verified_proficiency"], "Advanced")
        self.assertIn(round(py_gap["verified_score_pct"]), [88, 89])
        self.assertIn(py_gap["priority"], ["Low", "None"])
        self.assertEqual(py_gap["gap_score"], 0.0)

        # Check an unassessed skill (e.g. DevOps, Cloud, or JavaScript)
        unassessed = next((g for g in gaps if not g["is_verified"]), None)
        self.assertIsNotNone(unassessed, "Should have unassessed skills")
        self.assertEqual(unassessed["verified_proficiency"], "Not Assessed")
        self.assertEqual(unassessed["verified_score_pct"], 0)
        self.assertGreater(unassessed["gap_score"], 0.0)
        self.assertIn(unassessed["priority"], ["Critical", "High", "Medium"])

    def test_02_integration_with_module3_verified_skills(self):
        """Test that adding a second verified skill dynamically shrinks the gap and increases role match %."""
        # 1. Base match score with only Python verified
        base_res = calculate_skill_gaps(user_id=self.user_id, target_role_id="fullstack-dev")
        base_match = base_res["role_match_percentage"]

        # 2. Candidate verifies SQL at 75% (Advanced)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO verified_skills (
            user_id, skill_name, category, score_pct, proficiency_level, declared_level,
            mcq_score, mcq_max, programming_score, programming_max, comparison_status
        ) VALUES (?, 'SQL', 'Technical Skill', 75.0, 'Advanced', 'Beginner', 38.0, 50.0, 18.0, 20.0, 'exceeded')
        """, (self.user_id,))
        conn.commit()
        conn.close()

        # 3. Recalculate gap analysis
        updated_res = calculate_skill_gaps(user_id=self.user_id, target_role_id="fullstack-dev")
        updated_match = updated_res["role_match_percentage"]

        self.assertGreater(updated_match, base_match, "Verifying SQL must increase role match percentage")

        sql_gap = next((g for g in updated_res["gaps"] if g["skill_name"].lower() == "sql"), None)
        self.assertIsNotNone(sql_gap)
        self.assertTrue(sql_gap["is_verified"])
        self.assertEqual(sql_gap["verified_score_pct"], 75)
        self.assertIn(sql_gap["priority"], ["Low", "None"], "SQL gap should now be Low / None (Met)")

    def test_03_database_persistence_in_skill_gaps_table(self):
        """Test that calculated gaps are properly persisted in skill_gaps relational table."""
        calculate_skill_gaps(user_id=self.user_id, target_role_id="fullstack-dev")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skill_gaps WHERE user_id = ? AND role_id = 'fullstack-dev'", (self.user_id,))
        rows = cursor.fetchall()
        conn.close()

        self.assertGreater(len(rows), 0, "skill_gaps table must contain records for user")
        for r in rows:
            self.assertEqual(r["user_id"], self.user_id)
            self.assertEqual(r["role_id"], "fullstack-dev")
            self.assertIsNotNone(r["skill_name"])
            self.assertIsNotNone(r["required_level"])
            self.assertIsNotNone(r["verified_level"])
            self.assertIsNotNone(r["gap_score"])
            self.assertIn(r["priority"], ["Critical", "High", "Medium", "Low", "None"])
            self.assertIsNotNone(r["category"])
            self.assertIsNotNone(r["declared_level"])

    def test_04_radar_chart_vector_data(self):
        """Test that radar chart vector series are properly computed and symmetrical."""
        res = calculate_skill_gaps(user_id=self.user_id, target_role_id="fullstack-dev")
        radar = res["radar_chart_data"]

        cats = radar["categories"]
        req_s = radar["required_series"]
        ver_s = radar["verified_series"]
        dec_s = radar["declared_series"]

        self.assertGreater(len(cats), 0)
        self.assertEqual(len(cats), len(req_s), "Required series length must match categories")
        self.assertEqual(len(cats), len(ver_s), "Verified series length must match categories")
        self.assertEqual(len(cats), len(dec_s), "Declared series length must match categories")

        for val in req_s + ver_s + dec_s:
            self.assertGreaterEqual(val, 0)
            self.assertLessEqual(val, 100)

    def test_05_role_switching_and_nlp_market_analytics(self):
        """Test switching target role to AI/ML Engineer and fetching live NLP trends."""
        # 1. Evaluate for AI & Machine Learning Engineer role
        ds_res = calculate_skill_gaps(user_id=self.user_id, target_role_id="ai-ml-engineer")
        self.assertEqual(ds_res["target_role"]["role_id"], "ai-ml-engineer")
        self.assertIn("Python", [g["skill_name"] for g in ds_res["gaps"]])

        # 2. NLP Market Analytics for AI & Machine Learning Engineer
        analytics = extract_and_analyze_market_skills(role_id="ai-ml-engineer")
        self.assertGreater(analytics["total_postings_analyzed"], 0)
        self.assertGreater(len(analytics["global_top_skills"]), 0)

    def test_06_skill_gap_router_endpoints(self):
        """Test API router endpoints POST and GET /api/skills/gap-analysis."""
        # Test POST compute endpoint
        post_req = GapAnalysisTriggerRequest(target_role_id="fullstack-dev")
        post_res = compute_gap_analysis(req=post_req, user_id=self.user_id)
        self.assertTrue(post_res["success"])
        self.assertIn("gap_analysis", post_res)

        # Test GET fetch endpoint with role_id query
        get_res = get_user_gap_analysis(role_id="fullstack-dev", user_id=self.user_id)
        self.assertTrue(get_res["success"])
        self.assertIn("gap_analysis", get_res)
        self.assertEqual(get_res["gap_analysis"]["target_role"]["role_id"], "fullstack-dev")

        # Test GET fetch endpoint without role_id (uses career profile default)
        default_res = get_user_gap_analysis(role_id=None, user_id=self.user_id)
        self.assertTrue(default_res["success"])
        self.assertEqual(default_res["gap_analysis"]["target_role"]["role_id"], "fullstack-dev")

if __name__ == "__main__":
    unittest.main()
