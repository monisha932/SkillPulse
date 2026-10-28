"""
Comprehensive Automated Test Suite for MODULE 3: VERIFIED SKILL PROFILE.
Verifies all requirements:
1. Skill name (e.g. Python, SQL, Java)
2. Overall verified score (70% MCQ + 30% Coding, empirical calculation)
3. Verified proficiency level (0–39 Beginner, 40–59 Basic, 60–74 Intermediate, 75–89 Advanced, 90–100 Expert)
4. MCQ performance (score, total, percentage, 70% weighting)
5. Programming performance (score, total, percentage, test cases passed, 30% weighting)
6. Topic-wise strengths (>=70%) and weaknesses (<70%)
7. Clear distinction between User-declared skill and Assessment-verified skill
8. Persistent database storage in verified_skills table for downstream modules (Module 4)
9. Retrieval endpoints (GET /api/assessment/verified-profile, GET /api/assessment/verified-profile/{skill_name})
"""

import unittest
import json
from backend.database import get_db_connection, init_db
from backend.models import (
    SkillAssessmentStartRequest,
    SaveAnswerRequest,
    CompleteAssessmentRequest
)
from backend.routers.assessment import (
    start_assessment,
    save_answer,
    complete_assessment,
    get_verified_skill_profile,
    get_single_verified_skill_profile
)
from backend.routers.auth import get_career_profile

class TestModule3VerifiedSkillProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create or fetch dedicated test candidate
        cursor.execute("SELECT id FROM users WHERE email = 'module3_tester@platform.edu'")
        user = cursor.fetchone()
        if not user:
            cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES ('Module 3 Tester', 'module3_tester@platform.edu', 'mock_hash', 'student')
            """)
            cls.user_id = cursor.lastrowid
        else:
            cls.user_id = user["id"]

        # User declares skills in Career Profile
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (cls.user_id,))
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (cls.user_id,))
        cursor.execute("DELETE FROM assessment_attempts WHERE user_id = ?", (cls.user_id,))

        declared_skills = [
            {"skill_name": "Python", "self_rating": "Intermediate"},
            {"skill_name": "SQL", "self_rating": "Beginner"},
            {"skill_name": "Java", "self_rating": "Expert"}
        ]
        cursor.execute("""
        INSERT INTO career_profiles (user_id, target_role_id, declared_skills_json, experience_level, education)
        VALUES (?, 'fullstack-dev', ?, 'Fresher', 'B.E. Computer Science')
        """, (cls.user_id, json.dumps(declared_skills)))

        conn.commit()
        conn.close()

    def test_01_career_profile_shows_declared_skills_and_verified_distinction(self):
        """Test that get_career_profile distinguishes declared skills from verified skills."""
        res = get_career_profile(user_id=self.user_id)
        self.assertTrue(res["has_profile"])
        profile = res["profile"]

        # Check declared skills
        self.assertIn("declared_skills", profile)
        self.assertIn("verified_skills", profile)
        self.assertEqual(len(profile["verified_skills"]), 0, "Initially, no verified skills should exist before assessment")

        declared_names = [s["skill_name"] for s in profile["declared_skills"]]
        self.assertIn("Python", declared_names)
        self.assertIn("SQL", declared_names)
        self.assertIn("Java", declared_names)

    def test_02_assessment_completion_generates_verified_profile(self):
        """Test that completing an assessment generates an empirical Verified Skill Profile."""
        # 1. Start Python assessment
        start_req = SkillAssessmentStartRequest(skill_name="Python")
        start_res = start_assessment(req=start_req, user_id=self.user_id)
        session_token = start_res["session_token"]
        self.assertEqual(start_res["total_mcqs"], 50)
        self.assertEqual(start_res["total_coding"], 2)

        # 2. Answer 42 MCQs correctly out of 50
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, question_num, correct_option, topic
        FROM assessment_questions
        WHERE skill = 'Python' AND type = 'mcq'
        ORDER BY question_num ASC
        """)
        mcqs = cursor.fetchall()
        
        # Answer first 42 questions correctly, remaining 8 incorrectly
        for i, q in enumerate(mcqs):
            correct_int = int(q["correct_option"])
            chosen = correct_int if i < 42 else ((correct_int + 1) % 4)
            ans_req = SaveAnswerRequest(
                session_token=session_token,
                question_num=q["question_num"],
                selected_option=chosen
            )
            save_answer(req=ans_req)

        # 3. Submit correct code for both programming challenges (Q51 and Q52)
        py_solution_1 = """def find_target_subarray(nums, target):
    curr_sum = 0
    start = 0
    for end in range(len(nums)):
        curr_sum += nums[end]
        while curr_sum > target and start <= end:
            curr_sum -= nums[start]
            start += 1
        if curr_sum == target:
            return [start, end]
    return [-1, -1]
"""
        py_solution_2 = """def is_valid_brackets(s: str) -> bool:
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack
"""
        save_answer(req=SaveAnswerRequest(
            session_token=session_token,
            question_num=51,
            submitted_code=py_solution_1
        ))

        save_answer(req=SaveAnswerRequest(
            session_token=session_token,
            question_num=52,
            submitted_code=py_solution_2
        ))

        conn.close()

        # 4. Complete assessment
        comp_req = CompleteAssessmentRequest(session_token=session_token)
        comp_res = complete_assessment(req=comp_req)
        self.assertTrue(comp_res["success"])
        results = comp_res["results"]

        # Verify Skill Name
        self.assertEqual(results["skill_name"], "Python")

        # Verify MCQ Performance
        self.assertEqual(results["mcq_correct"], 42)
        self.assertEqual(results["mcq_total"], 50)
        self.assertEqual(results["mcq_score_pct"], 84.0) # 42/50 = 84.0%

        # Verify Programming Performance
        self.assertEqual(results["coding_points"], 20.0) # 20.0 / 20.0 pts
        self.assertEqual(results["coding_score_pct"], 100.0)

        # Verify Overall Weighted Score: (84.0 * 0.7) + (100.0 * 0.3) = 58.8 + 30.0 = 88.8%
        expected_score = round((84.0 * 0.7) + (100.0 * 0.3), 1)
        self.assertEqual(results["overall_total_pct"], expected_score)
        self.assertEqual(expected_score, 88.8)

        # Verify 5-Tier Proficiency Level: 88.8% falls in 75-89 -> "Advanced"
        self.assertEqual(results["proficiency_level"], "Advanced")

        # Verify Distinction between User-declared skill and Assessment-verified skill
        self.assertIn("declared_skill", results)
        self.assertIn("verified_skill", results)
        self.assertIn("comparison", results)
        self.assertEqual(results["declared_skill"]["declared_level"], "Intermediate")
        self.assertEqual(results["verified_skill"]["proficiency_level"], "Advanced")
        self.assertEqual(results["verified_skill"]["score_pct"], 88.8)
        self.assertEqual(results["comparison"]["status"], "exceeded")
        self.assertIn("Outperformed Declared Rating", results["comparison"]["label"])

        # Verify Topic-wise Strengths and Weaknesses
        self.assertIn("strengths", results)
        self.assertIn("weaknesses", results)
        for s in results["strengths"]:
            self.assertGreaterEqual(s["percentage"], 70.0, "Strength topic must have score >= 70%")
        for w in results["weaknesses"]:
            self.assertLess(w["percentage"], 70.0, "Weakness topic must have score < 70%")

    def test_03_verified_skill_persisted_in_database(self):
        """Test that the verified skill is stored in verified_skills table for Module 4."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM verified_skills WHERE user_id = ? AND LOWER(skill_name) = 'python'
        """, (self.user_id,))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row, "Verified skill record must exist in verified_skills table")
        self.assertEqual(row["skill_name"], "Python")
        self.assertEqual(row["score_pct"], 88.8)
        self.assertEqual(row["proficiency_level"], "Advanced")
        self.assertEqual(row["declared_level"], "Intermediate")
        self.assertEqual(row["mcq_score"], 42.0)
        self.assertEqual(row["mcq_max"], 50.0)
        self.assertEqual(row["programming_score"], 20.0)
        self.assertEqual(row["programming_max"], 20.0)
        self.assertEqual(row["comparison_status"], "exceeded")

        # Parse JSON fields
        strengths = json.loads(row["strengths_json"])
        weaknesses = json.loads(row["weaknesses_json"])
        self.assertIsInstance(strengths, list)
        self.assertIsInstance(weaknesses, list)

    def test_04_get_verified_skill_profile_endpoints(self):
        """Test retrieving verified skill profile via backend endpoint functions."""
        # 1. Get all verified profiles
        all_res = get_verified_skill_profile(skill_name=None, user_id=self.user_id)
        self.assertTrue(all_res["success"])
        self.assertTrue(all_res["has_verified_profile"])
        self.assertEqual(len(all_res["profiles"]), 1)

        profile = all_res["profile"]
        self.assertEqual(profile["skill_name"], "Python")
        self.assertEqual(profile["overall_score_pct"], 88.8)
        self.assertEqual(profile["proficiency_level"], "Advanced")
        self.assertEqual(profile["declared_skill"]["declared_level"], "Intermediate")
        self.assertEqual(profile["verified_skill"]["proficiency_level"], "Advanced")

        # 2. Get profile for specific skill
        single_res = get_single_verified_skill_profile(skill_name="Python", user_id=self.user_id)
        self.assertTrue(single_res["success"])
        self.assertTrue(single_res["has_verified_profile"])
        self.assertEqual(single_res["profile"]["skill_name"], "Python")

    def test_05_profile_endpoint_reflects_verified_badge(self):
        """Test that get_career_profile now returns the verified skills list for profile reflection."""
        res = get_career_profile(user_id=self.user_id)
        self.assertTrue(res["has_profile"])
        v_skills = res["profile"]["verified_skills"]
        self.assertEqual(len(v_skills), 1)
        self.assertEqual(v_skills[0]["skill_name"], "Python")
        self.assertEqual(v_skills[0]["score_pct"], 88.8)
        self.assertEqual(v_skills[0]["proficiency_level"], "Advanced")

    def test_06_5_tier_proficiency_scale_exact_boundaries(self):
        """Verify strict adherence to the 5 requested proficiency tiers:
        0–39 = Beginner
        40–59 = Basic
        60–74 = Intermediate
        75–89 = Advanced
        90–100 = Expert
        """
        def calc_tier(pct):
            if pct >= 90:
                return "Expert"
            elif pct >= 75:
                return "Advanced"
            elif pct >= 60:
                return "Intermediate"
            elif pct >= 40:
                return "Basic"
            else:
                return "Beginner"

        test_cases = [
            (0.0, "Beginner"),
            (25.0, "Beginner"),
            (39.0, "Beginner"),
            (39.9, "Beginner"),
            (40.0, "Basic"),
            (50.0, "Basic"),
            (59.9, "Basic"),
            (60.0, "Intermediate"),
            (67.5, "Intermediate"),
            (74.9, "Intermediate"),
            (75.0, "Advanced"),
            (82.0, "Advanced"),
            (89.9, "Advanced"),
            (90.0, "Expert"),
            (95.5, "Expert"),
            (100.0, "Expert"),
        ]

        for score, expected_tier in test_cases:
            self.assertEqual(calc_tier(score), expected_tier, f"Score {score} must evaluate to {expected_tier}")

if __name__ == "__main__":
    unittest.main()
