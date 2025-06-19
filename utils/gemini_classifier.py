import os
import requests

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyBwY7vwRKPsC0NggJrMFFmWZDpDp1PLI_Q"

def classify_with_gemini(text):
    prompt = f"""Voici un texte brut extrait d’un CV. Analyse-le et convertis-le en un JSON structuré avec les champs suivants :
    - Informations Personnelles
    - Compétences
    - Expérience Professionnelle
    - Formation
    - Certifications
    - Langues
    - Projets
    - Méthodologies

    Texte du CV :
    {text}
    """

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json=payload
    )

    response.raise_for_status()
    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']
