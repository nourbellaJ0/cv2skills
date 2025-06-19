import re
from keybert import KeyBERT

kw_model = KeyBERT()

def classify_block(text):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='french')
    terms = [kw[0].lower() for kw in keywords if isinstance(kw[0], str)]

    if any(term in ['python', 'java', 'sql', 'flask', 'html', 'docker'] for term in terms):
        return 'competences'
    elif any(term in ['université', 'diplôme', 'baccalauréat', 'école', 'formation'] for term in terms):
        return 'formation'
    elif any(term in ['stage', 'cdi', 'freelance', 'chez', 'entreprise', 'expérience'] for term in terms):
        return 'experience_professionnelle'
    elif any(term in ['anglais', 'français', 'arabe', 'langue', 'language'] for term in terms):
        return 'langues'
    elif any(term in ['agile', 'scrum', 'kanban', 'waterfall'] for term in terms):
        return 'methodologies'
    elif any(term in ['certification', 'certificat', 'toeic', 'pmp'] for term in terms):
        return 'certifications'
    elif any(term in ['projet', 'project', 'réalisé', 'conception'] for term in terms):
        return 'projets'
    else:
        return 'autres'
