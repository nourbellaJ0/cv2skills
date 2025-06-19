import re
import spacy


try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    from spacy.cli.download import download
    download("fr_core_news_sm")
    nlp = spacy.load("fr_core_news_sm")

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

from utils.matcher import classify_block

def extract_sections(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    buffer = {}
    
    for line in lines:
        section = classify_block(line)
        buffer.setdefault(section, []).append(line)

    sections = {k: "\n".join(v) for k, v in buffer.items()}
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

def extract_fields_from_sections(sections):
    nlp = spacy.load('fr_core_news_sm')
    dossier = {
        'informations_personnelles': {},
        'competences': [],
        'experience_professionnelle': [],
        'formation': [],
        'certifications': [],
        'langues': [],
        'projets': [],
        'methodologies': []
    }
    perso = sections.get('informations_personnelles', '')
    doc = nlp(perso)
    for ent in doc.ents:
        if ent.label_ == 'PER':
            dossier['informations_personnelles']['nom'] = ent.text
            break
    email = re.search(r'[\w\.-]+@[\w\.-]+', perso)
    if email:
        dossier['informations_personnelles']['email'] = email.group()
    tel = re.search(r'(\+\d{1,3}[-.\s]?)?(\d{2,3}[-.\s]?){3,5}\d{2,4}', perso)
    if tel:
        dossier['informations_personnelles']['telephone'] = tel.group()
    adresse = re.search(r'(\d{1,4} ?[a-zA-ZéèàêâîôûçÉÈÀÊÂÎÔÛÇ,\.\- ]+)', perso)
    if adresse:
        dossier['informations_personnelles']['adresse'] = adresse.group()
    comp = sections.get('competences', '')
    if comp:
        dossier['competences'] = [c.strip('-• ') for c in comp.split('\n') if c.strip()]
    exp = sections.get('experience_professionnelle', '')
    if exp:
        exp_blocks = re.split(r'\n{2,}', exp)
        for block in exp_blocks:
            doc = nlp(block)
            poste = entreprise = dates = resp = ''
            for ent in doc.ents:
                if ent.label_ == 'ORG':
                    entreprise = ent.text
                elif ent.label_ == 'PER':
                    poste = ent.text
                elif ent.label_ == 'DATE':
                    dates = ent.text
            resp = block
            dossier['experience_professionnelle'].append({
                'poste': poste,
                'entreprise': entreprise,
                'dates': dates,
                'responsabilites': resp
            })
    form = sections.get('formation', '')
    if form:
        form_blocks = re.split(r'\n{2,}', form)
        for block in form_blocks:
            doc = nlp(block)
            diplome = etab = dates = ''
            for ent in doc.ents:
                if ent.label_ == 'ORG':
                    etab = ent.text
                elif ent.label_ == 'DATE':
                    dates = ent.text
                elif ent.label_ == 'MISC':
                    diplome = ent.text
            dossier['formation'].append({
                'diplome': diplome,
                'etablissement': etab,
                'dates': dates
            })
    cert = sections.get('certifications', '')
    if cert:
        dossier['certifications'] = [c.strip('-• ') for c in cert.split('\n') if c.strip()]
    langues = sections.get('langues', '')
    if langues:
        dossier['langues'] = [l.strip('-• ') for l in langues.split('\n') if l.strip()]
    projets = sections.get('projets', '')
    if projets:
        dossier['projets'] = [p.strip('-• ') for p in projets.split('\n') if p.strip()]
    meth = sections.get('methodologies', '')
    if meth:
        dossier['methodologies'] = [m.strip('-• ') for m in meth.split('\n') if m.strip()]
    return dossier
