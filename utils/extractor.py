
import re

def extract_text(filepath):
    if filepath.endswith('.pdf'):
        import PyPDF2
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
    elif filepath.endswith('.docx'):
        import docx2txt
        return docx2txt.process(filepath)
    elif filepath.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "Format non supporté"

def extract_sections(text):
    sections = {
        'informations_personnelles': '',
        'competences': '',
        'experience_professionnelle': '',
        'formation': '',
        'certifications': '',
        'langues': '',
        'projets': '',
        'methodologies': ''
    }
    keywords = {
        'competences': [r'compétence', r'skills?', r'compétences techniques', r'compétences fonctionnelles'],
        'experience_professionnelle': [r'expériences? professionnelles?', r'parcours professionnel', r'professional experience', r'expériences?'],
        'formation': [r'formation', r'education', r'diplômes?', r'scolarité'],
        'certifications': [r'certifications?', r'certificat'],
        'langues': [r'langues?', r'languages?'],
        'projets': [r'projets?', r'projects?'],
        'methodologies': [r'méthodologies?', r'methodologies?']
    }
    lines = text.split('\n')
    current_section = 'informations_personnelles'
    buffer = {k: [] for k in sections}
    for line in lines:
        line_stripped = line.strip().lower()
        found_section = False
        for section, kw_list in keywords.items():
            for kw in kw_list:
                if re.search(rf'^\s*{kw}\b', line_stripped):
                    current_section = section
                    found_section = True
                    break
            if found_section:
                break
        buffer[current_section].append(line)
    for section in sections:
        content = '\n'.join([l for l in buffer[section] if l.strip()])
        sections[section] = content.strip()
    return sections

def clean_text(text):
    text = text.replace('\r', '\n').replace('\t', ' ')
    text = re.sub(r' +', ' ', text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    seen = set()
    cleaned_lines = []
    for l in lines:
        l_norm = l.lower()
        if l_norm not in seen:
            cleaned_lines.append(l)
            seen.add(l_norm)
    cleaned_text = '\n'.join(cleaned_lines)
    return cleaned_text
