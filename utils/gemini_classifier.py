
import os
import requests
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY

PROMPT_TEMPLATE = """
Tu es un assistant intelligent. À partir du texte brut d’un CV, tu dois renvoyer un JSON structuré selon le modèle suivant :

{
  "informations_personnelles": {
    "nom": "...",
    "email": "...",
    "telephone": "...",
    "adresse": "..."
  },
  "competences": ["...", "..."],
  "experience_professionnelle": [
    {
      "poste": "...",
      "entreprise": "...",
      "dates": "...",
      "responsabilites": "..."
    }
  ],
  "formation": [
    {
      "diplome": "...",
      "etablissement": "...",
      "dates": "..."
    }
  ],
  "certifications": [...],
  "langues": [...],
  "projets": [...],
  "methodologies": [...]
}

Voici le texte du CV à traiter :

"""{cv_text}"""
"""

def classify_with_gemini(cv_text):
    if not GEMINI_API_KEY:
        raise EnvironmentError("La clé GEMINI_API_KEY est manquante dans l'environnement.")

    payload = {
        "contents": [
            {
                "parts": [{"text": PROMPT_TEMPLATE.format(cv_text=cv_text)}]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(GEMINI_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Erreur Gemini API: {response.status_code} {response.text}")

    data = response.json()
    # Trouve le premier bloc JSON valide dans la réponse
    try:
        import re
        match = re.search(r'\{[\s\S]*\}', data["candidates"][0]["content"]["parts"][0]["text"])
        return json.loads(match.group()) if match else {}
    except Exception as e:
        raise RuntimeError(f"Erreur de parsing JSON: {e}")
