from functools import lru_cache
from sentence_transformers import SentenceTransformer, util
from services.parser import extract_skills

@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def compare(resume_text, job_description):
    model = get_model()
    embeddings = model.encode([resume_text[:12000], job_description[:12000]], convert_to_tensor=True)
    raw_similarity = float(util.cos_sim(embeddings[0], embeddings[1]).item())
    semantic_score = round(max(0, min(100, raw_similarity * 100)), 1)
    resume_skills = set(extract_skills(resume_text))
    required_skills = set(extract_skills(job_description))
    matched = sorted(resume_skills & required_skills)
    missing = sorted(required_skills - resume_skills)
    skill_score = round(100 * len(matched) / len(required_skills), 1) if required_skills else None
    # An interpretable heuristic, NOT a calibrated hiring probability.
    overall = round(0.7 * semantic_score + 0.3 * skill_score, 1) if skill_score is not None else semantic_score
    return {'overall': overall, 'semantic': semantic_score, 'skill_score': skill_score, 'matched': matched, 'missing': missing}
