"""
Live End-to-End Test for MODULE 9: JOB READINESS DASHBOARD
Tests against running dev server on http://127.0.0.1:8000:
1. Static asset delivery for readiness.js and index.html
2. User authentication flow
3. GET /api/readiness/dashboard endpoint
4. Title "CAREER SKILL PROFILE" presence
5. User information validation (Name, Target role, Preferred domain, Career goal)
6. Verified skills, required job skills, and skill gaps validation
7. Curriculum progress and micro-credentials validation
8. Transparent "Overall Skill Coverage: XX%" calculation and non-employment disclaimer
9. All 6 visual analytics datasets validation (Radar, Proficiency, Gap, Curriculum, Credential, Demand)
10. Final recommendations validation
11. POST /api/readiness/recalculate endpoint
12. GET /api/readiness/summary endpoint
"""

import unittest
import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

class TestE2ELiveModule9(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. Login with demo credentials
        login_url = f"{BASE_URL}/api/auth/login"
        payload = json.dumps({"email": "student@example.com", "password": "password123"}).encode("utf-8")
        req = urllib.request.Request(
            login_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cls.token = data.get("token") or data.get("session_token")
                cls.user_id = data.get("user", {}).get("id")
        except Exception as e:
            raise unittest.SkipTest(f"Live dev server not reachable or login failed: {e}")

    def test_01_static_assets_delivery(self):
        """Verifies readiness.js and index.html are served correctly with Step 9 included."""
        # Check index.html
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=5) as resp:
            html = resp.read().decode("utf-8")
            self.assertIn("Job Readiness Dashboard", html)
            self.assertIn('data-step="9"', html)
            self.assertIn('data-view="9"', html)
            self.assertIn('readiness.js', html)

        # Check readiness.js
        with urllib.request.urlopen(f"{BASE_URL}/static/js/readiness.js", timeout=5) as resp:
            js = resp.read().decode("utf-8")
            self.assertIn("Readiness", js)
            self.assertIn("CAREER SKILL PROFILE", js)
            self.assertIn("Overall Skill Coverage", js)
            self.assertIn("renderRadarSVG", js)

        print(" [PASS] Static assets and index.html with Step 9 delivered successfully.")

    def test_02_readiness_dashboard_api(self):
        """Verifies GET /api/readiness/dashboard returns complete Career Skill Profile."""
        url = f"{BASE_URL}/api/readiness/dashboard?target_role_id=fullstack-dev"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.token}"})

        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(res["success"])
            profile = res["profile"]

            # Title
            self.assertEqual(profile["title"], "CAREER SKILL PROFILE")
            print(f" [PASS] Title verified: '{profile['title']}'")

            # User Information
            user_info = profile["user_information"]
            self.assertIn("name", user_info)
            self.assertIn("target_job_role", user_info)
            self.assertIn("preferred_domain", user_info)
            self.assertIn("career_goal", user_info)
            print(f" [PASS] User Information verified: Name='{user_info['name']}', Role='{user_info['target_job_role']}'")

            # Verified Skills
            self.assertIn("verified_skills", profile)
            self.assertIsInstance(profile["verified_skills"], list)

            # Required Job Skills
            self.assertIn("required_job_skills", profile)
            self.assertTrue(len(profile["required_job_skills"]) >= 3)

            # Skill Gaps
            self.assertIn("skill_gaps", profile)
            self.assertTrue(len(profile["skill_gaps"]) >= 3)

            # Curriculum Progress
            curr = profile["curriculum_progress"]
            self.assertIn("completed_modules", curr)
            self.assertIn("remaining_modules", curr)
            self.assertIn("overall_progress", curr)

            # Micro-Credentials
            creds = profile["micro_credentials"]
            self.assertIn("earned_credentials", creds)
            self.assertIn("in_progress_credentials", creds)

            # Job Readiness / Skill Coverage
            jr = profile["job_readiness"]
            self.assertIn("Overall Skill Coverage:", jr["overall_skill_coverage_display"])
            self.assertIn("Disclaimer", jr["disclaimer"])
            print(f" [PASS] Job Readiness verified: {jr['overall_skill_coverage_display']}")
            print(f" [PASS] Disclaimer verified: '{jr['disclaimer'][:60]}...'")

            # 6 Visualizations
            vis = profile["visualizations"]
            self.assertIn("skill_radar_chart", vis)
            self.assertIn("skill_proficiency_bars", vis)
            self.assertIn("skill_gap_chart", vis)
            self.assertIn("curriculum_progress", vis)
            self.assertIn("credential_progress", vis)
            self.assertIn("job_market_demand_chart", vis)
            print(" [PASS] All 6 visualization datasets verified successfully.")

            # Final Recommendations
            recs = profile["final_recommendations"]
            self.assertIn("top_remaining_skill_gaps", recs)
            self.assertIn("highest_priority_skills", recs)
            self.assertIn("recommended_next_module", recs)
            self.assertIn("recommended_assessment_retake", recs)
            print(" [PASS] Final recommendations verified successfully.")

    def test_03_recalculate_and_summary_api(self):
        """Verifies POST /api/readiness/recalculate and GET /api/readiness/summary."""
        # Recalculate
        recalc_url = f"{BASE_URL}/api/readiness/recalculate"
        recalc_payload = json.dumps({"target_role_id": "fullstack-dev"}).encode("utf-8")
        req_recalc = urllib.request.Request(
            recalc_url,
            data=recalc_payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        )
        with urllib.request.urlopen(req_recalc, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            res_recalc = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(res_recalc["success"])
            self.assertEqual(res_recalc["profile"]["title"], "CAREER SKILL PROFILE")
            print(" [PASS] POST /api/readiness/recalculate executed successfully.")

        # Summary
        sum_url = f"{BASE_URL}/api/readiness/summary?target_role_id=fullstack-dev"
        req_sum = urllib.request.Request(sum_url, headers={"Authorization": f"Bearer {self.token}"})
        with urllib.request.urlopen(req_sum, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            res_sum = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(res_sum["success"])
            self.assertIn("overall_skill_coverage", res_sum)
            self.assertIn("disclaimer", res_sum)
            print(" [PASS] GET /api/readiness/summary executed successfully.")

if __name__ == "__main__":
    unittest.main()
