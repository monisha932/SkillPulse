"""
Module 7 Test Suite: Micro-Credential Generation Engine
Tests:
1. Conversion of completed learning modules into structured micro-credentials
2. Mandatory fields validation:
   - Credential title
   - Skill / domain
   - Learning objectives
   - Modules completed
   - Assessment score
   - Practical task / project
   - Completion percentage
   - Completion date
   - Credential level
3. Validation of Prompt Example:
   - "Python for Data Analytics – Intermediate"
   - Requirements: Python fundamentals, Functions, Data structures, Pandas, Data visualization, Final assessment, Practical project
   - Completion: 85%
4. Verification of 4 Credential Levels (Beginner, Basic, Intermediate, Advanced)
5. Digital Credential Record generation with Unique ID, User Name, Skill, Level, Date, Verification status
6. Legal milestone Non-Accreditation Notice disclosure
7. Public digital verification lookup functionality
8. Credential claim and status transition from in_progress to earned
"""

import unittest
import json
from backend.database import init_db, get_db_connection
from backend.services.credential_engine import (
    sync_user_micro_credentials,
    get_user_credentials,
    get_credential_by_id,
    verify_credential_public,
    claim_credential,
    CREDENTIAL_CATALOG,
    ACCREDITATION_DISCLAIMER
)

class TestModule7MicroCredentials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Seed dedicated test student
        cursor.execute("SELECT id FROM users WHERE email = 'mod7_student@example.com'")
        user = cursor.fetchone()
        if not user:
            cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES ('Pooja & Monisha (Candidate)', 'mod7_student@example.com', 'dummy_hash', 'student')
            """)
            cls.user_id = cursor.lastrowid
        else:
            cls.user_id = user["id"]

        # Clean slate for test candidate
        cursor.execute("DELETE FROM user_credentials WHERE user_id = ?", (cls.user_id,))

        # Seed verified skill with assessment score (Module 3)
        cursor.execute("DELETE FROM verified_skills WHERE user_id = ?", (cls.user_id,))
        cursor.execute("""
        INSERT INTO verified_skills (user_id, skill_name, score_pct, proficiency_level)
        VALUES (?, 'Python', 88.5, 'Intermediate')
        """, (cls.user_id,))
        cursor.execute("""
        INSERT INTO verified_skills (user_id, skill_name, score_pct, proficiency_level)
        VALUES (?, 'SQL', 92.0, 'Advanced')
        """, (cls.user_id,))

        # Seed user curriculum and completed modules (Module 6)
        cursor.execute("DELETE FROM user_curriculums WHERE user_id = ?", (cls.user_id,))
        cursor.execute("""
        INSERT INTO user_curriculums (user_id, role_id, title, status, total_modules, completed_modules)
        VALUES (?, 'data-analyst', 'Personalized Micro-Credential Pathway: Data Analyst', 'active', 6, 2)
        """, (cls.user_id,))
        curr_id = cursor.lastrowid

        cursor.execute("DELETE FROM curriculum_modules WHERE curriculum_id = ?", (curr_id,))
        # Module 1 completed: Advanced SQL
        cursor.execute("""
        INSERT INTO curriculum_modules (
            curriculum_id, module_order, title, hours, status, progress_pct,
            skill_name, current_proficiency, required_proficiency, difficulty,
            learning_objective, prerequisites_json, topics_json, resources_json,
            practice_json, assessment_info, project_task, is_unlocked
        ) VALUES (
            ?, 1, 'Advanced SQL Query Architecture', 14, 'completed', 100,
            'Advanced SQL', 'Novice', 'Advanced', 'Advanced',
            'Master advanced SQL analytic functions.', '[]', '["Window Functions", "CTEs"]', '[]',
            '["Query drill"]', '15 MCQs', 'Financial ledger optimization task', 1
        )
        """, (curr_id,))

        # Module 2 in-progress: Python for Data Analysis
        cursor.execute("""
        INSERT INTO curriculum_modules (
            curriculum_id, module_order, title, hours, status, progress_pct,
            skill_name, current_proficiency, required_proficiency, difficulty,
            learning_objective, prerequisites_json, topics_json, resources_json,
            practice_json, assessment_info, project_task, is_unlocked
        ) VALUES (
            ?, 2, 'Python for Data Analysis & Scripting', 12, 'in_progress', 85,
            'Python for Data Analysis', 'Beginner', 'Intermediate', 'Intermediate',
            'Master idiomatic Python and vectorized analysis.', '[]', '["NumPy", "Pandas intro"]', '[]',
            '["Vector drill"]', '15 MCQs', 'Telemetry ETL pipeline project', 1
        )
        """, (curr_id,))

        conn.commit()
        conn.close()

    def test_01_credential_generation_and_mandatory_fields(self):
        """Verifies that micro-credentials contain all required fields with complete data."""
        data = sync_user_micro_credentials(self.user_id)
        self.assertIsNotNone(data)
        self.assertGreater(data["total_earned"] + data["total_in_progress"], 0)

        all_creds = data["earned_credentials"] + data["in_progress_credentials"]

        required_fields = [
            "credential_id",        # Unique credential ID
            "title",                # Credential title
            "skill",                # Skill
            "domain",               # Domain
            "level",                # Credential level
            "learning_objectives",  # Learning objectives
            "modules_completed",    # Modules completed
            "assessment_score",     # Assessment score
            "practical_task",       # Practical task / project
            "completion_pct",       # Completion percentage
            "status",               # Status (earned / in_progress)
            "user_name",            # User name
            "verification_status",  # Verification status
            "accreditation_disclaimer" # Disclaimer
        ]

        for cred in all_creds:
            for field in required_fields:
                self.assertIn(field, cred, f"Missing required field '{field}' in credential {cred.get('title')}")
            # Verify data validity
            self.assertTrue(len(cred["title"]) > 0)
            self.assertTrue(len(cred["skill"]) > 0)
            self.assertGreaterEqual(len(cred["learning_objectives"]), 2)
            self.assertGreaterEqual(cred["assessment_score"], 0)
            self.assertGreater(len(cred["practical_task"]), 10)
            self.assertIn(cred["status"], ["earned", "in_progress"])
            self.assertIn(cred["level"], ["Beginner", "Basic", "Intermediate", "Advanced"])

    def test_02_python_data_analytics_example_alignment(self):
        """
        Validates the exact Prompt Example:
        MICRO-CREDENTIAL: "Python for Data Analytics – Intermediate"
        Requirements:
        * Python fundamentals
        * Functions
        * Data structures
        * Pandas
        * Data visualization
        * Final assessment
        * Practical project
        Completion: 85%
        """
        data = get_user_credentials(self.user_id)
        all_creds = data["earned_credentials"] + data["in_progress_credentials"]

        py_cred = None
        for c in all_creds:
            if "Python for Data Analytics – Intermediate" in c["title"]:
                py_cred = c
                break

        self.assertIsNotNone(py_cred, "Python for Data Analytics – Intermediate must exist in micro-credentials")
        self.assertEqual(py_cred["level"], "Intermediate")
        self.assertEqual(py_cred["completion_pct"], 85.0, "Completion percentage should be 85% as specified in example")

        # Verify requirements checklist matches prompt specifications
        expected_requirements = [
            "Python fundamentals",
            "Functions",
            "Data structures",
            "Pandas",
            "Data visualization",
            "Final assessment",
            "Practical project"
        ]
        for req in expected_requirements:
            self.assertIn(req, py_cred["requirements"], f"Missing requirement '{req}' in Python credential")

    def test_03_credential_levels(self):
        """Verifies support for all 4 defined Credential Levels: Beginner, Basic, Intermediate, Advanced."""
        data = get_user_credentials(self.user_id)
        all_creds = data["earned_credentials"] + data["in_progress_credentials"]
        levels_found = set(c["level"] for c in all_creds)

        self.assertIn("Intermediate", levels_found)
        self.assertIn("Advanced", levels_found)
        self.assertIn("Basic", levels_found)
        self.assertIn("Beginner", levels_found)

    def test_04_digital_credential_record_uniqueness(self):
        """Verifies that each issued credential contains a globally unique ID starting with CRED-."""
        data = get_user_credentials(self.user_id)
        all_creds = data["earned_credentials"] + data["in_progress_credentials"]
        cred_ids = [c["credential_id"] for c in all_creds]

        # Verify uniqueness
        self.assertEqual(len(cred_ids), len(set(cred_ids)), "All credential IDs must be distinct")

        # Verify format
        for cid in cred_ids:
            self.assertTrue(cid.startswith("CRED-"), f"Credential ID '{cid}' must follow 'CRED-' prefix convention")

    def test_05_non_accreditation_disclosure(self):
        """Verifies that platform-generated notice is explicitly attached to prevent false accreditation claims."""
        data = get_user_credentials(self.user_id)
        self.assertIn("Non-Accreditation Notice", data["disclaimer"])
        self.assertIn("does not claim or represent government, university", data["disclaimer"])

        for c in data["earned_credentials"] + data["in_progress_credentials"]:
            self.assertIn("Non-Accreditation Notice", c["accreditation_disclaimer"])

    def test_06_public_digital_verification(self):
        """Tests the public verification function without requiring candidate authentication."""
        data = get_user_credentials(self.user_id)
        first_cred = (data["earned_credentials"] + data["in_progress_credentials"])[0]
        cid = first_cred["credential_id"]

        # Test valid verification
        verif_res = verify_credential_public(cid)
        self.assertTrue(verif_res["verified"])
        self.assertEqual(verif_res["credential_id"], cid)
        self.assertEqual(verif_res["recipient_name"], first_cred["user_name"])
        self.assertIn("Non-Accreditation Notice", verif_res["accreditation_notice"])

        # Test non-existent credential verification
        invalid_res = verify_credential_public("CRED-FAKE-999999")
        self.assertFalse(invalid_res["verified"])
        self.assertEqual(invalid_res["status"], "Invalid Credential ID")

    def test_07_credential_claim_and_completion(self):
        """Tests claiming an eligible credential, transitioning its status from in_progress to earned."""
        data = get_user_credentials(self.user_id)
        in_prog = data["in_progress_credentials"]
        self.assertGreater(len(in_prog), 0, "Expected at least one in-progress credential to test claim")

        target_cred = in_prog[0]
        cid = target_cred["credential_id"]

        claimed = claim_credential(self.user_id, cid)
        self.assertEqual(claimed["status"], "earned")
        self.assertEqual(claimed["completion_pct"], 100.0)
        self.assertIsNotNone(claimed["issue_date"])

        # Verify updated in registry
        updated_data = get_user_credentials(self.user_id)
        earned_ids = [c["credential_id"] for c in updated_data["earned_credentials"]]
        self.assertIn(cid, earned_ids)

if __name__ == "__main__":
    unittest.main()
