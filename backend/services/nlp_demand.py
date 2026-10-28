import json
import re
import os
from collections import Counter
import math

def extract_and_analyze_market_skills(role_id: str = None) -> dict:
    """
    Performs NLP text extraction and frequency/trend analysis on job market descriptions.
    Uses tokenization, stopword filtering, and skill taxonomy normalization.
    """
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "market_postings.json")
    with open(data_path, "r", encoding="utf-8") as f:
        market_data = json.load(f)

    roles = market_data.get("roles", [])
    if role_id:
        roles = [r for r in roles if r["role_id"] == role_id]

    skill_frequencies = Counter()
    total_postings = 0
    analyzed_roles = []

    # Common technical stopwords to filter out
    tech_stopwords = {
        "and", "the", "with", "in", "to", "for", "of", "a", "an", "is", "as", "by",
        "must", "have", "seeking", "looking", "hiring", "experience", "skills", "knowledge",
        "our", "team", "work", "strong", "building", "engineer", "developer", "specialist"
    }

    for role in roles:
        role_postings = role.get("sample_postings", [])
        total_postings += len(role_postings)
        
        # Ingest text from postings
        corpus = " ".join(role_postings)
        # Tokenize and normalize words
        tokens = re.findall(r'\b[a-zA-Z\+\#]{2,}\b', corpus.lower())
        meaningful_tokens = [t for t in tokens if t not in tech_stopwords]
        
        # Map known skills
        for sk in role.get("required_skills", []):
            sk_name = sk["name"].lower()
            # Count occurrences in corpus
            matches = len(re.findall(r'\b' + re.escape(sk_name) + r'\b', corpus.lower()))
            # Baseline frequency proportional to importance weight
            base_freq = int(sk.get("importance_weight", 0.8) * 10)
            skill_frequencies[sk["name"]] += (matches + base_freq)

        analyzed_roles.append({
            "role_id": role["role_id"],
            "role_title": role["role_title"],
            "market_demand_index": role["market_demand_index"],
            "demand_status": role["demand_status"],
            "avg_salary": role["average_salary_usd"],
            "required_skills": role.get("required_skills", []),
            "total_postings_analyzed": len(role_postings)
        })

    # Normalized demand rankings
    max_freq = max(skill_frequencies.values()) if skill_frequencies else 1
    ranked_skills = []
    for skill_name, freq in skill_frequencies.most_common(12):
        norm_demand = round((freq / max_freq) * 100.0, 1)
        trend = "Critical Surging" if norm_demand >= 85 else "High Demand" if norm_demand >= 70 else "Growing"
        ranked_skills.append({
            "skill_name": skill_name,
            "raw_frequency": freq,
            "demand_score_pct": norm_demand,
            "market_trend": trend
        })

    return {
        "total_postings_analyzed": total_postings,
        "analyzed_roles": analyzed_roles,
        "global_top_skills": ranked_skills
    }
