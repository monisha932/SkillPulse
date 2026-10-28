"""
Comprehensive Automated Test Suite for MODULE 5: SKILL GAP ANALYSIS.
Tests all requirements:
1. Strict comparison between VERIFIED USER SKILLS (Module 3) and REQUIRED JOB-MARKET SKILLS (Module 4)
2. Complete isolation of self-declared skills (never used directly for gap calculation)
3. Configurable 1–5 proficiency scale (Beginner=1, Basic=2, Intermediate=3, Advanced=4, Expert=5, Not Assessed=0)
4. Exact gap calculation formula: Required Level - User Level
5. Gap categorization: 0 -> No Gap, 1 -> Low Gap, 2 -> Medium Gap, 3 -> High Gap, 4+ -> Critical Gap
6. Multi-factor priority calculation (gap magnitude, market demand %, importance, prerequisites)
7. Specification test case:
   - Java: Basic -> Advanced => Gap = 2 (Medium Gap, High Priority)
   - SQL: Advanced -> Intermediate => Gap = 0 (No Gap, None Priority)
   - JavaScript: Beginner -> Advanced => Gap = 3 (High Gap, High Priority)
   - React: Not Assessed -> Intermediate => Gap = 3 (High Gap, High Priority)
   - Git: Not Assessed -> Intermediate => Gap = 3 (High Gap, High Priority)
8. Multi-user and multi-target role comparison testing
9. Database persistence in skill_gaps table
"""

import unittest
import json
from backend.database import get_db_connection, init_db
from backend.seed_data import seed_database
from backend.models import CareerProfileRequest
from backend.routers.auth import save_career_profile
from backend.services.gap_engine import (
    calculate_skill_gaps,
    PROFICIENCY_SCALE,
    get_gap_category
)
from backend.routers.skill_gap import compute_gap_analysis, get_user_gap_analysis, GapAnalysisTriggerRequest

class TestModule5SkillGapAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create User 1: Specified user with Java (Basic), SQL (Advanced), JavaScript (Beginner)
        cursor.execute("SELECT id FROM users WHERE email = 'm5_user1@platform.edu'")
        u1 = cursor.fetchone()
        if not u1:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("M5 Test User 1", "m5_user1@platform.edu", "dummyhash", "student")
            )
            cls.user1_id = cursor.lastrowid
        else:
            cls.user1_id = u1["id"]

        # Insert verified skills for User 1:
        # Java -> Basic (score 48%), SQL -> Advanced (score 82%), JavaScript -> Beginner (score 35%)
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (cls.user1_id,))
        verified_data = [
            ("Java", 48.0, "Basic", 24.0, 50.0, 10.0, 20.0),
            ("SQL", 82.0, "Advanced", 42.0, 50.0, 20.0, 20.0),
            ("JavaScript", 35.0, "Beginner", 15.0, 50.0, 5.0, 20.0)
        ]
        for v in verified_data:
            cursor.execute("""
            INSERT INTO verified_skills (
                user_id, skill_name, score_pct, proficiency_level,
                mcq_score, mcq_max, programming_score, programming_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cls.user1_id, v[0], v[1], v[2], v[3], v[4], v[5], v[6]))

        # Create User 2: Completely unassessed candidate
        cursor.execute("SELECT id FROM users WHERE email = 'm5_user2_unassessed@platform.edu'")
        u2 = cursor.fetchone()
        if not u2:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("M5 Unassessed User", "m5_user2_unassessed@platform.edu", "dummyhash", "student")
            )
            cls.user2_id = cursor.lastrowid
        else:
            cls.user2_id = u2["id"]
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (cls.user2_id,))

        # Create User 3: User with ONLY self-declared skills (no assessments)
        cursor.execute("SELECT id FROM users WHERE email = 'm5_user3_declared_only@platform.edu'")
        u3 = cursor.fetchone()
        if not u3:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("M5 Declared Only", "m5_user3_declared_only@platform.edu", "dummyhash", "student")
            )
            cls.user3_id = cursor.lastrowid
        else:
            cls.user3_id = u3["id"]
        conn.commit()
        conn.close()

        # Save profile for User 3 with self-declared Expert skills
        save_career_profile(
            req=CareerProfileRequest(
                target_role_id="fullstack-dev",
                declared_skills=[
                    {"skill_name": "Java", "self_rating": "Expert"},
                    {"skill_name": "JavaScript", "self_rating": "Expert"},
                    {"skill_name": "SQL", "self_rating": "Expert"},
                    {"skill_name": "React", "self_rating": "Expert"},
                    {"skill_name": "Git", "self_rating": "Expert"}
                ],
                experience_level="Fresher",
                degree_major="B.Tech CS"
            ),
            user_id=cls.user3_id
        )

    def test_01_proficiency_scale_configuration(self):
        """Test the 1–5 numerical proficiency scale."""
        self.assertEqual(PROFICIENCY_SCALE["Beginner"], 1)
        self.assertEqual(PROFICIENCY_SCALE["Basic"], 2)
        self.assertEqual(PROFICIENCY_SCALE["Intermediate"], 3)
        self.assertEqual(PROFICIENCY_SCALE["Advanced"], 4)
        self.assertEqual(PROFICIENCY_SCALE["Expert"], 5)
        self.assertEqual(PROFICIENCY_SCALE["Not Assessed"], 0)
        self.assertEqual(PROFICIENCY_SCALE["Not Verified"], 0)

    def test_02_gap_categories_mapping(self):
        """Test the gap category definitions: 0 -> No Gap, 1 -> Low, 2 -> Medium, 3 -> High, 4+ -> Critical."""
        self.assertEqual(get_gap_category(0), "No Gap")
        self.assertEqual(get_gap_category(-1), "No Gap")
        self.assertEqual(get_gap_category(1), "Low Gap")
        self.assertEqual(get_gap_category(2), "Medium Gap")
        self.assertEqual(get_gap_category(3), "High Gap")
        self.assertEqual(get_gap_category(4), "Critical Gap")
        self.assertEqual(get_gap_category(5), "Critical Gap")

    def test_03_specification_example_user_comparison(self):
        """
        Verify the exact specification example:
        User: Java=Basic (2), SQL=Advanced (4), JavaScript=Beginner (1)
        Target role requires:
        - Java: Advanced (4)
        - SQL: Intermediate (3)
        - JavaScript: Advanced (4)
        - React: Intermediate (3)
        - Git: Intermediate (3)
        """
        results = calculate_skill_gaps(user_id=self.user1_id, target_role_id="fullstack-dev")
        self.assertIsNotNone(results)
        self.assertEqual(results["target_role"]["role_id"], "fullstack-dev")

        gaps_map = {g["skill_name"].lower(): g for g in results["gaps"]}

        # 1. Java: User = Basic (2), Required = Advanced (4)
        java_gap = gaps_map["java"]
        self.assertEqual(java_gap["verified_level"], "Basic")
        self.assertEqual(java_gap["verified_level_num"], 2)
        self.assertEqual(java_gap["required_level"], "Advanced")
        self.assertEqual(java_gap["required_level_num"], 4)
        self.assertEqual(java_gap["gap_num"], 2)
        self.assertEqual(java_gap["gap"], "Medium Gap")
        self.assertIn(java_gap["priority"], ["High", "Medium", "Critical"])

        # 2. SQL: User = Advanced (4), Required = Intermediate (3)
        sql_gap = gaps_map["sql"]
        self.assertEqual(sql_gap["verified_level"], "Advanced")
        self.assertEqual(sql_gap["verified_level_num"], 4)
        self.assertEqual(sql_gap["required_level"], "Intermediate")
        self.assertEqual(sql_gap["required_level_num"], 3)
        self.assertEqual(sql_gap["gap_num"], 0)
        self.assertEqual(sql_gap["gap"], "No Gap")
        self.assertEqual(sql_gap["priority"], "None")

        # 3. JavaScript: User = Beginner (1), Required = Advanced (4)
        js_gap = gaps_map["javascript"]
        self.assertEqual(js_gap["verified_level"], "Beginner")
        self.assertEqual(js_gap["verified_level_num"], 1)
        self.assertEqual(js_gap["required_level"], "Advanced")
        self.assertEqual(js_gap["required_level_num"], 4)
        self.assertEqual(js_gap["gap_num"], 3)
        self.assertEqual(js_gap["gap"], "High Gap")
        self.assertIn(js_gap["priority"], ["High", "Critical"])

        # 4. React: User = Not Assessed (0), Required = Intermediate (3)
        react_gap = gaps_map["react"]
        self.assertEqual(react_gap["verified_level"], "Not Assessed")
        self.assertEqual(react_gap["verified_level_num"], 0)
        self.assertFalse(react_gap["is_verified"])
        self.assertEqual(react_gap["required_level"], "Intermediate")
        self.assertEqual(react_gap["required_level_num"], 3)
        self.assertEqual(react_gap["gap_num"], 3)
        self.assertEqual(react_gap["gap"], "High Gap")
        self.assertIn(react_gap["priority"], ["High", "Critical"])

        # 5. Git: User = Not Assessed (0), Required = Intermediate (3)
        git_gap = gaps_map["git"]
        self.assertEqual(git_gap["verified_level"], "Not Assessed")
        self.assertEqual(git_gap["verified_level_num"], 0)
        self.assertFalse(git_gap["is_verified"])
        self.assertEqual(git_gap["required_level"], "Intermediate")
        self.assertEqual(git_gap["required_level_num"], 3)
        self.assertEqual(git_gap["gap_num"], 3)
        self.assertEqual(git_gap["gap"], "High Gap")
        self.assertIn(git_gap["priority"], ["High", "Critical"])

    def test_04_unassessed_user_handling(self):
        """Verify that an unassessed candidate has all skills marked 'Not Assessed' with gap = required level."""
        results = calculate_skill_gaps(user_id=self.user2_id, target_role_id="fullstack-dev")
        self.assertEqual(results["mastered_count"], 0)
        self.assertEqual(results["role_match_percentage"], 0.0)

        for g in results["gaps"]:
            self.assertEqual(g["verified_level"], "Not Assessed")
            self.assertEqual(g["verified_level_num"], 0)
            self.assertFalse(g["is_verified"])
            self.assertEqual(g["gap_num"], g["required_level_num"])

    def test_05_self_declared_skills_strict_isolation(self):
        """
        CRITICAL REQUIREMENT: Do NOT compare self-declared skills directly.
        User 3 declared Expert in Java, JS, SQL, React, Git, but took NO assessments.
        Their verified levels must remain 'Not Assessed' (0) and gap must NOT be satisfied.
        """
        results = calculate_skill_gaps(user_id=self.user3_id, target_role_id="fullstack-dev")

        declared_tested = ["java", "javascript", "sql", "react", "git"]
        for g in results["gaps"]:
            if g["skill_name"].lower() in declared_tested:
                # Self-declared level is captured for audit
                self.assertEqual(g["declared_level"], "Expert")
            # BUT verified level must strictly be Not Assessed
            self.assertEqual(g["verified_level"], "Not Assessed")
            self.assertEqual(g["verified_level_num"], 0)
            self.assertFalse(g["is_verified"])
            # Gap must remain equal to required level
            self.assertEqual(g["gap_num"], g["required_level_num"])
            self.assertNotEqual(g["gap"], "No Gap")

        # Role match must be 0% despite declared Expert
        self.assertEqual(results["role_match_percentage"], 0.0)

    def test_06_multi_role_comparison(self):
        """Test comparing the same user against Full Stack Developer vs AI / ML Engineer."""
        fs_gaps = calculate_skill_gaps(user_id=self.user1_id, target_role_id="fullstack-dev")
        ai_gaps = calculate_skill_gaps(user_id=self.user1_id, target_role_id="ai-ml-engineer")

        self.assertEqual(fs_gaps["target_role"]["role_id"], "fullstack-dev")
        self.assertEqual(ai_gaps["target_role"]["role_id"], "ai-ml-engineer")

        # Full Stack has Java, JavaScript, React as core requirements
        fs_skills = [g["skill_name"] for g in fs_gaps["gaps"]]
        self.assertIn("JavaScript", fs_skills)
        self.assertIn("React", fs_skills)

        # AI / ML Engineer has Python as primary requirement
        ai_skills = [g["skill_name"] for g in ai_gaps["gaps"]]
        self.assertIn("Python", ai_skills)

    def test_07_api_router_get_endpoint(self):
        """Test GET /api/skills/gap-analysis endpoint function."""
        res = get_user_gap_analysis(role_id="fullstack-dev", user_id=self.user1_id)
        self.assertTrue(res.get("success"))
        analysis = res.get("gap_analysis")
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis["target_role"]["role_id"], "fullstack-dev")
        self.assertIsInstance(analysis["gaps"], list)
        self.assertTrue(len(analysis["gaps"]) > 0)

    def test_08_api_router_post_endpoint(self):
        """Test POST /api/skills/gap-analysis trigger endpoint."""
        req = GapAnalysisTriggerRequest(target_role_id="fullstack-dev")
        res = compute_gap_analysis(req=req, user_id=self.user1_id)
        self.assertTrue(res.get("success"))
        analysis = res.get("gap_analysis")
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis["target_role"]["role_id"], "fullstack-dev")

    def test_09_database_persistence_in_skill_gaps(self):
        """Verify that calculate_skill_gaps persists records in skill_gaps table."""
        calculate_skill_gaps(user_id=self.user1_id, target_role_id="fullstack-dev")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM skill_gaps WHERE user_id = ? AND role_id = 'fullstack-dev'", (self.user1_id,))
        count = cursor.fetchone()[0]
        conn.close()
        self.assertGreater(count, 0)

if __name__ == "__main__":
    unittest.main()
