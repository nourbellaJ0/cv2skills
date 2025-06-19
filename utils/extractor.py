import re
import spacy
from utils.matcher import classify_block

PARA_SPLIT = re.compile(r"\n{2,}")
DATE_RGX   = re.compile(r"(\w+ \d{4})\s*[–-]\s*(\w+|\d{4}|présent)", re.I)
LANG_RGX   = re.compile(r"\b(anglais|français|arabe|espagnol|allemand|italien)\b", re.I)

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
    return "Format non supporté"

def clean_text(text):
    text = text.replace('\r', '\n').replace('\t', ' ')
    text = re.sub(r' +', ' ', text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    seen = set()
    return '\n'.join(l for l in lines if not (l.lower() in seen or seen.add(l.lower())))

def extract_sections(text):
    paras = [p.strip() for p in PARA_SPLIT.split(text) if p.strip()]
    buffer = {}
    for p in paras:
        section = classify_block(p)
        buffer.setdefault(section, []).append(p)
    return {k: "\n\n".join(v) for k, v in buffer.items()}

def extract_fields_from_sections(sections):
    nlp = spacy.load("fr_core_news_sm")
    dossier = {
        "informations_personnelles": {},
        "competences": [],
        "experience_professionnelle": [],
        "formation": [],
        "certifications": [],
        "langues": [],
        "projets": [],
        "methodologies": []
    }
    perso = sections.get("informations_personnelles", "")
    doc = nlp(perso)
    for ent in doc.ents:
        if ent.label_ == "PER":
            dossier["informations_personnelles"]["nom"] = ent.text
        elif ent.label_ == "LOC" and "adresse" not in dossier["informations_personnelles"]:
            dossier["informations_personnelles"]["adresse"] = ent.text
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", perso)
    dossier["informations_personnelles"]["email"] = email_match.group(0) if email_match else ""
    tel_match = re.search(r"(?:\+?\d[\d\s.-]{7,})", perso)
    dossier["informations_personnelles"]["telephone"] = tel_match.group(0) if tel_match else ""

    dossier["competences"] = [c.strip("-••– ") for c in sections.get("competences", "").split("\n") if 3 < len(c) < 60]
    dossier["langues"] = list(set(LANG_RGX.findall("\n".join(sections.values()))))

    for block in PARA_SPLIT.split(sections.get("formation", "")):
        doc = nlp(block)
        etab = dates = diplome = ""
        for ent in doc.ents:
            if ent.label_ == "ORG": etab = ent.text
            if ent.label_ == "DATE": dates = ent.text
        match = re.search(r"(licence|master|bachelor|baccalaur[ée]at)", block, re.I)
        diplome = match.group(0) if match else ""
        if block: dossier["formation"].append({"diplome": diplome, "etablissement": etab, "dates": dates})

    for block in PARA_SPLIT.split(sections.get("experience_professionnelle", "")):
        top_line = block.split("\n")[0]
        poste, entreprise = "", ""
        if "," in top_line:
            poste, entreprise = [x.strip() for x in top_line.split(",", 1)]
        dates = DATE_RGX.search(block)
        dossier["experience_professionnelle"].append({
            "poste": poste, "entreprise": entreprise,
            "dates": dates.group(0) if dates else "", "responsabilites": block
        })

    for key in ("certifications", "projets", "methodologies"):
        bloc = sections.get(key, "")
        dossier[key] = [l.strip("-• ") for l in bloc.split("\n") if l.strip()]

    return dossier
