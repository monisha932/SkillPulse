import os
from backend.routers.auth import (
    register_user, login_user, get_available_roles,
    save_career_profile, get_career_profile
)
from backend.models import (
    UserRegisterRequest, UserLoginRequest,
    CareerProfileRequest, DeclaredSkillItem
)

def run_tests():
    print("Testing Roles API...")
    roles = get_available_roles()
    print(f"Retrieved {len(roles['roles'])} roles.")
    assert len(roles['roles']) >= 4, "Expected at least 4 roles"

    print("\nTesting Login API with Demo User...")
    login_res = login_user(UserLoginRequest(email="student@example.com", password="password123"))
    print("Login success:", login_res["success"], "User ID:", login_res["user"]["id"])
    assert login_res["success"] is True

    print("\nTesting Career Profile & Declared Skills Save...")
    profile_req = CareerProfileRequest(
        target_role_id="fullstack-dev",
        experience_level="Fresher",
        education="B.E. Computer Science and Engineering",
        declared_skills=[
            DeclaredSkillItem(skill_name="Python", self_rating="Intermediate"),
            DeclaredSkillItem(skill_name="JavaScript", self_rating="Intermediate"),
            DeclaredSkillItem(skill_name="SQL", self_rating="Beginner")
        ]
    )
    save_res = save_career_profile(profile_req, user_id=login_res["user"]["id"])
    print("Profile save success:", save_res["success"])
    assert save_res["success"] is True

    print("\nTesting Career Profile Fetch...")
    get_res = get_career_profile(user_id=login_res["user"]["id"])
    print("Has profile:", get_res["has_profile"], "Role title:", get_res["profile"]["role_title"])
    print("Declared skills count:", len(get_res["profile"]["declared_skills"]))
    assert get_res["has_profile"] is True
    assert len(get_res["profile"]["declared_skills"]) == 3

    print("\n>>> Phase 2 Backend Verification Passed 100%! <<<")

if __name__ == "__main__":
    run_tests()
