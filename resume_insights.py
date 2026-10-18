import re
from collections import Counter

SECTIONS = {
    'Contact': r'@|\+?\d[\d\s()-]{8,}\d',
    'Education': r'\b(education|b\.?tech|b\.?e\.?|bachelor|university|college|degree)\b',
    'Skills': r'\b(skills|technologies|technical skills|tech stack)\b',
    'Projects': r'\b(projects?|portfolio|github)\b',
    'Experience': r'\b(experience|internship|intern|employment)\b',
    'Certifications': r'\b(certifications?|credentials?|courses?)\b',
}

def inspect_resume(text, result):
    matched = list(result.get('matched') or [])
    missing = list(result.get('missing') or [])
    sections = [{'name': name, 'present': bool(re.search(pattern, text, re.I))} for name, pattern in SECTIONS.items()]
    # Experience and certifications are optional for fresher resumes.
    required = [s for s in sections if s['name'] not in ('Experience', 'Certifications')]
    completeness = round(100 * sum(s['present'] for s in required) / len(required))
    keywords = sorted(set(str(x).strip() for x in matched + missing if str(x).strip()), key=str.casefold)
    density = []
    for skill in keywords:
        pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'
        density.append({'name': skill, 'count': len(re.findall(pattern, text, re.I)), 'matched': skill in matched})
    density.sort(key=lambda x: (-x['count'], x['name']))
    suggestions = []
    for section in required:
        if not section['present']:
            suggestions.append('Check whether your resume clearly includes a ' + section['name'] + ' section.')
    if not re.search(r'\b\d+(?:\.\d+)?\s*(?:%|percent|hours|users|records|rows|projects)\b', text, re.I):
        suggestions.append('Where accurate, quantify project results with measurable outcomes.')
    if missing:
        suggestions.append('Review job skills not detected in your resume: ' + ', '.join(map(str, missing[:5])) + '.')
    if not suggestions:
        suggestions.append('Core resume sections were detected. Verify formatting and descriptions manually.')
    return {'sections': sections, 'completeness': completeness, 'density': density, 'suggestions': suggestions}
