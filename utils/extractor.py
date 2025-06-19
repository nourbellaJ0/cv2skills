# utils/extractor.py  (seules les fonctions modifiées/ajoutées sont montrées)

# --- nouveau --- #
PARA_SPLIT = re.compile(r"\n{2,}")             # sépare sur 2 sauts de ligne ou plus
DATE_RGX   = re.compile(r"(\w+ \d{4})\s*[–-]\s*(\w+|\d{4}|présent)", re.I)
LANG_RGX   = re.compile(r"\b(anglais|français|arabe|espagnol|allemand|italien)\b", re.I)

def extract_sections(text: str) -> dict:
    """Classe chaque paragraphe plutôt que chaque ligne ⇒ meilleur contexte"""
    paras   = [p.strip() for p in PARA_SPLIT.split(text) if p.strip()]
    buffer  = {}
    for p in paras:
        section = classify_block(p)
        buffer.setdefault(section, []).append(p)
    return {k: "\n\n".join(v) for k, v in buffer.items()}

# --- enrichissement des champs --- #
def extract_fields_from_sections(sections: dict) -> dict:
    nlp = spacy.load("fr_core_news_sm")
    dossier = {k: [] if k not in ("informations_personnelles") else {} 
               for k in ["informations_personnelles","competences","experience_professionnelle",
                         "formation","certifications","langues","projets","methodologies"]}

    # 1. Infos perso ---------------------------------------------------------
    perso = sections.get("informations_personnelles", "")
    doc   = nlp(perso)
    for ent in doc.ents:
        if ent.label_ == "PER":
            dossier["informations_personnelles"]["nom"] = ent.text
        elif ent.label_ == "LOC" and "adresse" not in dossier["informations_personnelles"]:
            dossier["informations_personnelles"]["adresse"] = ent.text
    dossier["informations_personnelles"]["email"]     = re.search(r"[\w\.-]+@[\w\.-]+", perso) or ""
    dossier["informations_personnelles"]["telephone"] = re.search(r"(?:\+?\d[\d\s.-]{7,})", perso) or ""

    # 2. Compétences ---------------------------------------------------------
    comp_raw = sections.get("competences", "")
    dossier["competences"] = [c.strip("-••– ") for c in comp_raw.split("\n") if 3 < len(c) < 60]

    # 3. Langues (extrait dans TOUT le texte) --------------------------------
    langs_found = set(LANG_RGX.findall(text))
    dossier["langues"] = list(langs_found)

    # 4. Formation -----------------------------------------------------------
    for block in PARA_SPLIT.split(sections.get("formation", "")):
        doc = nlp(block)
        etab = dates = diplome = ""
        for ent in doc.ents:
            if ent.label_ == "ORG":   etab = ent.text
            if ent.label_ == "DATE":  dates = ent.text
        dipl_match = re.search(r"(licence|master|bachelor|baccalaur[ée]at)", block, re.I)
        diplome = dipl_match.group(0) if dipl_match else ""
        if block: dossier["formation"].append(
            {"diplome": diplome, "etablissement": etab, "dates": dates}
        )

    # 5. Expérience ----------------------------------------------------------
    for block in PARA_SPLIT.split(sections.get("experience_professionnelle", "")):
        top_line  = block.split("\n")[0]
        poste, entreprise = "", ""
        if "," in top_line:
            poste, entreprise = [x.strip() for x in top_line.split(",", 1)]
        dates = DATE_RGX.search(block)
        dossier["experience_professionnelle"].append(
            {"poste": poste, "entreprise": entreprise,
             "dates": dates.group(0) if dates else "",
             "responsabilites": block}
        )

    # 6. Certifications, projets, méthodos -----------------------------------
    for key in ("certifications","projets","methodologies"):
        bloc = sections.get(key, "")
        dossier[key] = [l.strip("-• ") for l in bloc.split("\n") if l.strip()]

    return dossier
