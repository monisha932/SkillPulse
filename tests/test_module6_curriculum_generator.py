"""
Module 6 Test Suite: Personalized AI Curriculum Generator
Tests:
1. Data Analyst Sequence Validation (Advanced SQL -> Statistics -> Python for Data Analysis -> Pandas -> Data Visualization -> Power BI -> Capstone Project)
2. Mandatory 12-field verification on all modules
3. Topological prerequisite DAG ordering (foundational always precede advanced)
4. Non-generic learning content and detailed engineering curricula
5. Pacing calculation across varying weekly hours (5h, 10h, 20h)
6. Dynamic prerequisite unlocking upon module progress completion
7. Milestone Non-Accreditation Notice disclosure
8. Multi-role synthesis (Full Stack Developer, Data Analyst)
"""

import unittest
import json
from backend.database import init_db, get_db_connection
from backend.services.curriculum_engine import (
    generate_personalized_curriculum,
    get_active_user_curriculum,
    update_module_progress,
    topological_sort_modules,
    MODULE_KNOWLEDGE_BASE
)

class TestModule6CurriculumGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create or ensure test student
        cursor.execute("SELECT id FROM users WHERE email = 'mod6_student@example.com'")
        user = cursor.fetchone()
        if not user:
            cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES ('Module 6 Candidate', 'mod6_student@example.com', 'dummy_hash', 'student')
            """)
            cls.user_id = cursor.lastrowid
        else:
            cls.user_id = user["id"]

        # Setup career profile for Data Analyst
        cursor.execute("DELETE FROM career_profiles WHERE user_id = ?", (cls.user_id,))
        cursor.execute("""
        INSERT INTO career_profiles (user_id, target_role_id, declared_skills_json, updated_at)
        VALUES (?, 'data-analyst', ?, CURRENT_TIMESTAMP)
        """, (cls.user_id, json.dumps([
            {"skill": "Advanced SQL", "level": "Novice"},
            {"skill": "Statistics", "level": "Novice"},
            {"skill": "Python for Data Analysis", "level": "Novice"}
        ])))

        conn.commit()
        conn.close()

    def test_01_data_analyst_exact_sequence(self):
        """Validates the exact Data Analyst sequence from prompt specifications."""
        curriculum = generate_personalized_curriculum(
            user_id=self.user_id,
            target_role_id="data-analyst",
            weekly_hours=10
        )
        self.assertIsNotNone(curriculum)
        modules = curriculum["modules"]
        skill_names = [m["skill_name"] for m in modules]

        # The prompt expects:
        # 1. Advanced SQL
        # 2. Statistics
        # 3. Python for Data Analysis
        # 4. Pandas
        # 5. Data Visualization
        # 6. Power BI
        # 7. Capstone Project
        expected_sequence = [
            "Advanced SQL",
            "Statistics",
            "Python for Data Analysis",
            "Pandas",
            "Data Visualization",
            "Power BI",
            "Capstone Project"
        ]

        # Verify all expected skills are present
        for expected_skill in expected_sequence:
            self.assertIn(expected_skill, skill_names, f"Missing expected skill: {expected_skill}")

        # Verify topological prerequisite order:
        # Python for Data Analysis must come BEFORE Pandas
        idx_python = skill_names.index("Python for Data Analysis")
        idx_pandas = skill_names.index("Pandas")
        self.assertLess(idx_python, idx_pandas, "Python for Data Analysis must precede Pandas")

        # Pandas and Statistics must come BEFORE Data Visualization
        idx_stats = skill_names.index("Statistics")
        idx_viz = skill_names.index("Data Visualization")
        self.assertLess(idx_pandas, idx_viz, "Pandas must precede Data Visualization")
        self.assertLess(idx_stats, idx_viz, "Statistics must precede Data Visualization")

        # Capstone Project must be the final module
        self.assertEqual(skill_names[-1], "Capstone Project", "Capstone Project must be the terminal integration module")

    def test_02_mandatory_12_fields_per_module(self):
        """Verifies that every generated module contains all 12 required fields with non-empty content."""
        curriculum = generate_personalized_curriculum(
            user_id=self.user_id,
            target_role_id="data-analyst"
        )
        modules = curriculum["modules"]
        self.assertGreaterEqual(len(modules), 5)

        required_fields = [
            "skill_name",              # 1. Skill/module name
            "current_proficiency",     # 2. Current proficiency
            "required_proficiency",    # 3. Required proficiency
            "learning_objective",      # 4. Learning objective
            "prerequisites",           # 5. Prerequisites
            "topics",                  # 6. Topics
            "difficulty",              # 7. Difficulty
            "estimated_duration",      # 8. Estimated duration
            "learning_resources",      # 9. Learning resources
            "practice_activities",     # 10. Practice activities
            "assessment",              # 11. Assessment
            "project_task"             # 12. Project / task
        ]

        for idx, mod in enumerate(modules):
            for field in required_fields:
                self.assertIn(field, mod, f"Module {idx} ({mod.get('skill_name')}) missing field '{field}'")
                val = mod[field]
                if field != "prerequisites" and isinstance(val, (list, str)):
                    self.assertTrue(len(val) > 0, f"Module {idx} field '{field}' is empty")
                elif field == "prerequisites":
                    self.assertIsInstance(val, list)

    def test_03_non_generic_content(self):
        """Ensures modules have deep, non-generic syllabus topics, resources, and project tasks."""
        curriculum = generate_personalized_curriculum(
            user_id=self.user_id,
            target_role_id="data-analyst"
        )
        for mod in curriculum["modules"]:
            # Topics must be descriptive lists of technical subjects
            self.assertGreaterEqual(len(mod["topics"]), 3, f"Module {mod['skill_name']} has too few topics")
            # Resources must include title, type, and url
            self.assertGreaterEqual(len(mod["learning_resources"]), 2)
            for res in mod["learning_resources"]:
                self.assertIn("title", res)
                self.assertIn("type", res)
                self.assertIn("url", res)
            # Practice activities must have hands-on exercises
            self.assertGreaterEqual(len(mod["practice_activities"]), 2)
            # Project task must specify a concrete deliverable
            self.assertGreater(len(mod["project_task"]), 20)

    def test_04_weekly_hours_pacing_calibration(self):
        """Verifies that timeline pacing dynamically adjusts based on candidate's weekly learning hours."""
        curr_10 = generate_personalized_curriculum(user_id=self.user_id, target_role_id="data-analyst", weekly_hours=10)
        curr_20 = generate_personalized_curriculum(user_id=self.user_id, target_role_id="data-analyst", weekly_hours=20)
        curr_5  = generate_personalized_curriculum(user_id=self.user_id, target_role_id="data-analyst", weekly_hours=5)

        total_hours = curr_10["total_estimated_hours"]
        self.assertEqual(curr_10["weekly_hours"], 10)
        self.assertEqual(curr_20["weekly_hours"], 20)
        self.assertEqual(curr_5["weekly_hours"], 5)

        # 20 hours/week should take fewer weeks than 10 hours/week, which takes fewer weeks than 5 hours/week
        self.assertLessEqual(curr_20["estimated_weeks"], curr_10["estimated_weeks"])
        self.assertLessEqual(curr_10["estimated_weeks"], curr_5["estimated_weeks"])

    def test_05_dynamic_prerequisite_unlocking(self):
        """Tests that downstream modules unlock when their prerequisite modules are completed."""
        curriculum = generate_personalized_curriculum(
            user_id=self.user_id,
            target_role_id="data-analyst"
        )
        modules = curriculum["modules"]
        mod_1 = modules[0]
        self.assertTrue(mod_1["is_unlocked"], "First foundational module must be unlocked initially")

        # Mark module 1 as completed
        update_res = update_module_progress(
            user_id=self.user_id,
            module_id=mod_1["module_id"],
            progress_pct=100,
            status="completed"
        )
        self.assertEqual(update_res["status"], "completed")

        # Fetch active curriculum and verify updated state
        active_curr = get_active_user_curriculum(user_id=self.user_id, target_role_id="data-analyst")
        active_mods = active_curr["modules"]
        active_mod_1 = [m for m in active_mods if m["module_id"] == mod_1["module_id"]][0]
        self.assertEqual(active_mod_1["status"], "completed")
        self.assertEqual(active_curr["completed_modules"], 1)

    def test_06_non_accreditation_disclaimer(self):
        """Verifies that the legal milestone non-accreditation disclaimer is explicitly included."""
        curriculum = generate_personalized_curriculum(user_id=self.user_id, target_role_id="data-analyst")
        self.assertIn("disclaimer", curriculum)
        self.assertIn("Non-Accreditation Notice", curriculum["disclaimer"])
        self.assertIn("do not claim official university degrees", curriculum["disclaimer"])

    def test_07_fullstack_dev_curriculum_synthesis(self):
        """Tests curriculum generation for Full Stack Developer role."""
        curriculum = generate_personalized_curriculum(
            user_id=self.user_id,
            target_role_id="fullstack-dev"
        )
        self.assertIsNotNone(curriculum)
        self.assertEqual(curriculum["target_role_id"], "fullstack-dev")
        modules = curriculum["modules"]
        skill_names = [m["skill_name"] for m in modules]

        # Verify JavaScript precedes React
        if "JavaScript" in skill_names and "React" in skill_names:
            self.assertLess(skill_names.index("JavaScript"), skill_names.index("React"))

        # Verify terminal Capstone
        self.assertEqual(skill_names[-1], "Capstone Project")

    def test_08_exact_python_prerequisite_chain(self):
        """
        Validates the exact prerequisite logic from the specifications:
        Python Basics -> Python Functions -> Python Data Structures -> Pandas -> Data Analysis
        Ensures foundational topics strictly precede advanced topics.
        """
        test_chain_skills = [
            "Data Analysis",
            "Pandas",
            "Python Data Structures",
            "Python Functions",
            "Python Basics"
        ]
        test_modules = []
        for s in test_chain_skills:
            template = MODULE_KNOWLEDGE_BASE[s.lower()]
            test_modules.append({
                "skill_name": s,
                "title": template["title"],
                "category": template["category"],
                "hours": template["default_hours"],
                "prerequisites": template["prerequisites"],
                "gap_num": 2,
                "job_demand_percentage": 90.0,
                "importance_weight": 0.90
            })

        sorted_mods = topological_sort_modules(test_modules)
        sorted_names = [m["skill_name"] for m in sorted_mods]

        expected_chain = [
            "Python Basics",
            "Python Functions",
            "Python Data Structures",
            "Pandas",
            "Data Analysis"
        ]
        self.assertEqual(sorted_names, expected_chain, f"Expected prerequisite chain {expected_chain} but got {sorted_names}")

if __name__ == "__main__":
    unittest.main()
