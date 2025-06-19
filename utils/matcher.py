# utils/matcher.py
import re
from keybert import KeyBERT
kw_model = KeyBERT()

SECTION_RULES = {
    "competences":  [r"\b(compétence|skills?)\b"],
    "formation":    [r"\b(licence|master|dipl[oô]me|université|baccalaur[ée]at)\b"],
    "experience_professionnelle":
        [r"\b(stage|alternance|cdi|freelance|expériences?)\b", r",\s?(?:sarl|sa|inc|ltd)?\s?$"],
    "langues":      [r"\b(langues?|anglais|français|arabe|espagnol|allemand)\b"],
    "certifications":[r"\b(certifications?|certificat|toeic|pmp|scrum)\b"],
    "methodologies":[r"\b(agile|scrum|kanban|waterfall)\b"],
    "projets":      [r"\b(projet[s]?|project[s]?)\b"],
}

def classify_block(text: str) -> str:
    low = text.lower()
    for section, patterns in SECTION_RULES.items():
        if any(re.search(p, low) for p in patterns):
            return section
    # fallback KeyBERT
    terms = [kw[0].lower() for kw in kw_model.extract_keywords(text, stop_words='french')]
    if any(t in ['python', 'sql', 'docker', 'html', 'marketing'] for t in terms):
        return "competences"
    return "autres"
