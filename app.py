import os
import tempfile
import mimetypes
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime
from groq import Groq

from utils.file_detector import detect_format
from utils.extractor import extract_text, clean_text

import sys
from apryse_sdk import *

sys.path.append("PDFNetC6/Samples/LicenseKey/PYTHON")
from PDFNetC6.Samples.LicenseKey.PYTHON.LicenseKey import *

import PyPDF2  # Forcer l'inclusion de PyPDF2

from apryse_sdk import PDFNet, TemplateDocument, PDFDoc, OfficeToPDFOptions, Convert, SDFDoc

# 🔗 Connexion à MongoDB Atlas (via .env)

client = MongoClient("mongodb+srv://nourbellaaj:NBkumK0rXzGLPYuX@cluster0.nq7jkzm.mongodb.net/")
db = client["cv2skills_db"]
collection = db["cv_documents"]

# Flask init
app = Flask(__name__)
CORS(app)
load_dotenv()

# Configuration API Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "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"
groq_client = Groq(api_key=GROQ_API_KEY)

SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
]

DEFAULT_STRUCTURE = {
    "competences_techniques_categories": [],
    "experiences_cles_recentes": [],
    "experiences_professionnelles": [],
    "formation_et_certifications": [],
    "informations_personnelles": {
        "nom": "",
        "prenom": "",
        "resume": "",
        "titre": ""
    },
    "langues": [],
    "methodologies": [],
    "projets_interessants": []
}

def sanitize_technologies(techs):
    # Transforme ["Python", "Flask"] en [{"item": "Python"}, ...] si besoin
    if isinstance(techs, list):
        return [t if isinstance(t, dict) and "item" in t else {"item": t} for t in techs]
    return []

def sanitize_json(data):
    def sanitize_value(val):
        if isinstance(val, str):
            return val.strip() or "Aucune information"
        elif isinstance(val, list):
            return [sanitize_value(v) for v in val] or []
        elif isinstance(val, dict):
            return {k: sanitize_value(v) for k, v in val.items()}
        return "Aucune information"

    def normalize_contenu(contenu):
        """Normalise le champ contenu en array de strings"""
        if isinstance(contenu, str):
            return contenu
        elif isinstance(contenu, list):
            # Si c'est une liste de dicts avec 'listes' et 'nom', extraire les valeurs
            if contenu and isinstance(contenu[0], dict):
                if 'listes' in contenu[0] and 'nom' in contenu[0]:
                    # Format complexe, extraire les éléments
                    result = []
                    for item in contenu:
                        if 'listes' in item and isinstance(item['listes'], list):
                            result.extend(item['listes'])
                    return ", ".join(str(x) for x in result) if result else "Aucune information"
            # Format simple array
            return ", ".join(str(x) for x in contenu) if contenu else "Aucune information"
        return "Aucune information"

    # Forcer le format des listes d'objets pour le template
    def force_list_of_dicts(lst, keys):
        result = []
        for item in lst:
            if isinstance(item, dict):
                obj = {}
                for k in keys:
                    if k == "technologies":
                        # S'assurer que technologies est toujours un tableau
                        techs = item.get(k, [])
                        if isinstance(techs, str):
                            obj[k] = [{"item": techs}]
                        elif isinstance(techs, list):
                            obj[k] = [{"item": t} if isinstance(t, str) else t for t in techs]
                        else:
                            obj[k] = [{"item": "Aucune technologie"}]
                    elif k == "missions":
                        # S'assurer que missions est toujours un tableau
                        missions = item.get(k, [])
                        if isinstance(missions, str):
                            obj[k] = [{"item": missions}]
                        elif isinstance(missions, list):
                            obj[k] = [{"item": m} if isinstance(m, str) else m for m in missions]
                        else:
                            obj[k] = [{"item": "Aucune mission"}]
                    elif k == "livrables":
                        # S'assurer que livrables est toujours un tableau
                        livrables = item.get(k, [])
                        if isinstance(livrables, str):
                            obj[k] = [{"item": livrables}]
                        elif isinstance(livrables, list):
                            obj[k] = [{"item": l} if isinstance(l, str) else l for l in livrables]
                        else:
                            obj[k] = [{"item": "Aucun livrable"}]
                    elif k == "contenu":
                        # Normaliser le contenu
                        obj[k] = normalize_contenu(item.get(k, ""))
                    else:
                        obj[k] = sanitize_value(item.get(k, ""))
            elif isinstance(item, str):
                obj = {k: (item if i == 0 else "") for i, k in enumerate(keys)}
            else:
                obj = {k: "" for k in keys}
            result.append(obj)
        return result

    return {
        "competences_techniques_categories": force_list_of_dicts(
            data.get("competences_techniques_categories", []),
            ["titre", "contenu"]
        ),
        "experiences_cles_recentes": force_list_of_dicts(
            data.get("experiences_cles_recentes", []),
            ["intitule", "entreprise", "duree"]
        ),
        "experiences_professionnelles": force_list_of_dicts(
            data.get("experiences_professionnelles", []),
            ["poste", "entreprise", "periode", "contexte", "missions", "livrables", "environnement"]
        ),
        "formation_et_certifications": force_list_of_dicts(
            data.get("formation_et_certifications", []),
            ["diplome_certification", "etablissement", "annee"]
        ),
        "informations_personnelles": {
            "nom": sanitize_value(data.get("informations_personnelles", {}).get("nom", "")),
            "prenom": sanitize_value(data.get("informations_personnelles", {}).get("prenom", "")),
            "resume": sanitize_value(data.get("informations_personnelles", {}).get("resume", "")),
        },
        "langues": force_list_of_dicts(
            data.get("langues", []),
            ["langue", "niveau"]
        ),
        "methodologies": force_list_of_dicts(
            data.get("methodologies", []),
            ["item"]
        ),
        "projets_interessants": force_list_of_dicts(
            data.get("projets_interessants", []),
            ["titre", "description", "technologies"]
        ),
    }


@app.route("/upload", methods=["POST"])
def upload_cv():
    try:
        file = request.files.get("cv")
        if not file:
            return jsonify({"success": False, "error": "Aucun fichier reçu."}), 400

        filename = file.filename or "uploaded"
        offre_recherchee = request.form.get("offre", "").strip()
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else "tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            file.save(tmp.name)
            file_format = detect_format(tmp.name)
            print(f"Format MIME détecté : {file_format}")
            if file_format not in SUPPORTED_MIME_TYPES:
                return jsonify({
                    "success": False,
                    "error": f"Format de fichier non supporté : {file_format}",
                    "format_detecté": file_format
                }), 400
            text = extract_text(tmp.name)

        if not text.strip():
            return jsonify({"success": False, "error": "Le texte extrait est vide ou illisible."}), 400

        cleaned_text = clean_text(text)

        # Adapter le prompt selon l'offre si elle est spécifiée
        offre_instruction = ""
        if offre_recherchee:
            offre_instruction = f"""

🎯 **ADAPTATION POUR L'OFFRE CIBLE:** {offre_recherchee}

INSTRUCTIONS CRITIQUES:
1. REFORMULE les expériences professionnelles pour les adapter au poste "{offre_recherchee}"
2. DÉVELOPPE et ENRICHIS les descriptions des expériences pertinentes pour ce poste
3. METS EN VALEUR les aspects techniques et contextuels pertinents pour "{offre_recherchee}"
4. Ajoute des détails sur comment les expériences correspondent au poste
5. Les expériences NON pertinentes pour "{offre_recherchee}" doivent être réduites au minimum

Exemple: Pour un poste de Data Science, développe les projets ML/IA, reformule les missions autour de l'analyse de données, mets en avant les outils data (Python, SQL, etc.)
"""

        prompt = f"""Voici un texte brut extrait d'un CV. Analyse-le et convertis-le en un JSON structuré qui suit **strictement** le format suivant :{offre_instruction}

{{
  "competences_techniques_categories": [
    {{
      "titre": "Nom de la catégorie",
      "contenu": "Liste des compétences de cette catégorie"
    }}
  ],
  "experiences_cles_recentes": [
    {{
      "intitule": "Titre du poste",
      "entreprise": "Nom de l'entreprise",
      "duree": "Durée ou période"
    }}
  ],
  "experiences_professionnelles": [
    {{
      "poste": "Titre du poste",
      "entreprise": "Nom de l'entreprise",
      "periode": "Période d'emploi",
      "contexte": "Contexte du projet/mission",
      "missions": [
        {{
          "item": "Description de la mission"
        }}
      ],
      "livrables": [
        {{
          "item": "Description du livrable"
        }}
      ],
      "environnement": "Technologies et outils utilisés"
    }}
  ],
  "formation_et_certifications": [
    {{
      "diplome_certification": "Nom du diplôme/certification",
      "etablissement": "Nom de l'établissement",
      "annee": "Année d'obtention"
    }}
  ],
  "informations_personnelles": {{
    "nom": "Nom de famille",
    "prenom": "Prénom",
    "resume": "Résumé professionnel"
  }},
  "langues": [
    {{
      "langue": "Nom de la langue",
      "niveau": "Niveau de maîtrise"
    }}
  ],
  "methodologies": [
    {{
      "item": "Nom de la méthodologie"
    }}
  ],
  "projets_interessants": [
    {{
      "titre": "Titre du projet",
      "description": "Description du projet",
      "technologies": [
        {{
          "item": "Nom de la technologie"
        }}
      ]
    }}
  ]
}}

Texte du CV :
{cleaned_text}
"""
        
        # Ajouter un dernier rappel au prompt si une offre est spécifiée
        if offre_recherchee:
            reminder = f"⚠️ RAPPEL FINAL: Reformule et enrichis le contenu pour adapter au poste '{offre_recherchee}' - les expériences doivent être différentes et détaillées pour ce poste spécifique!"
            prompt += "\n\n" + reminder

        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_completion_tokens=8192
            )
            print(f"Groq API status: Success")
            generated_text = response.choices[0].message.content
            print("Groq full response:", generated_text[:1000])
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": f"Erreur API Groq: {str(e)}"}), 500

        # Parse/validate Groq response
        try:
            if not generated_text:
                raise ValueError("Empty response from Groq")
        except Exception as e:
            print("Impossible de parser la réponse de Groq:", str(e))
            raise

        if not isinstance(generated_text, str) or not generated_text.strip():
            return jsonify({"success": False, "error": "Réponse Groq inattendue: texte manquant"}), 500

        generated_text = generated_text.strip()
        
        # Extract JSON from markdown code blocks or find raw JSON
        # Groq often returns: "Voici... ```json { ... } ```"
        if "```json" in generated_text:
            start_idx = generated_text.find("```json") + len("```json")
            end_idx = generated_text.rfind("```")
            if end_idx > start_idx:
                generated_text = generated_text[start_idx:end_idx].strip()
        else:
            # Try to find JSON object directly
            json_start = generated_text.find("{")
            json_end = generated_text.rfind("}")
            if json_start >= 0 and json_end > json_start:
                generated_text = generated_text[json_start:json_end+1].strip()
        
        print("📄 Cleaned text ready to parse:", generated_text[:200])

        try:
            structured_json = json.loads(generated_text)

            # Contrôle de saisie sur les champs essentiels
            infos = structured_json.get("informations_personnelles", {})
            
            print("Raw Groq data (before sanitize):", json.dumps(structured_json, ensure_ascii=False)[:500])
            print("Raw competences count:", len(structured_json.get("competences_techniques_categories", [])))
           
            # Return RAW data from Groq, don't sanitize yet
            # Sanitization will happen in PDF generation
            return jsonify({
                "success": True, 
                "data": structured_json,  # Return raw Groq data
                "filename": filename,
                "offre_recherchee": offre_recherchee if offre_recherchee else None
            })

        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            return jsonify({
                "success": False, 
                "error": "Le résultat n'est pas un JSON valide", 
                "data": DEFAULT_STRUCTURE
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        # For dev: include brief error message in response to aid debugging
        return jsonify({"success": False, "error": f"Erreur d'extraction : {str(e)}"}), 500

from flask import send_from_directory

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static_file(filename):
    return send_from_directory('static', filename)

# Initialisation Apryse
PDFNet.Initialize("demo:1752070393300:61bdca4403000000007b61d7537372fcfa3852aafb5c2f90c5c1d0335e")


@app.route("/generate-pdf-apryse-template", methods=["POST"])
def generate_pdf_apryse_template():
    try:
        print("Requete recue pour generation Apryse")
        json_data = request.form.get("jsonData")
        if not json_data:
            print("ERREUR: Aucune jsonData recue!")
            print("Available form keys:", list(request.form.keys()))
            return jsonify({"success": False, "error": "Données JSON manquantes"}), 400

        print("jsonData recu (debut):", json_data[:500])
        parsed_json = json.loads(json_data)
        print("Parsed JSON keys:", list(parsed_json.keys()))
        print("Raw competences count:", len(parsed_json.get("competences_techniques_categories", [])))
        
        # Sanitize ONLY when generating PDF
        data = sanitize_json(parsed_json)
        print("After sanitize_json competences count:", len(data.get("competences_techniques_categories", [])))


        input_template = os.path.join("template_new.docx")
        if not os.path.exists(input_template):
            return jsonify({"success": False, "error": "Template DOCX introuvable"}), 500

        # Créer le document à partir du template Word
        template_doc = Convert.CreateOfficeTemplate(input_template, None)

        # Remplir le document avec les données JSON
        filled_pdf = template_doc.FillTemplateJson(json.dumps(data))

        output_pdf_path = os.path.join("cv2skills_result_apryse.pdf")
        filled_pdf.Save(output_pdf_path, SDFDoc.e_linearized)

        print("PDF genere avec succes")
        return send_file(output_pdf_path, as_attachment=True)

    except Exception as e:
        print("Erreur Apryse:", str(e))
        return jsonify({"success": False, "error": f"Erreur Apryse : {str(e)}"}), 500

# ✅ Route alias pour éviter les 404 sur /generate-pdf
@app.route("/generate-pdf", methods=["POST"])
def generate_pdf_alias():
    return generate_pdf_apryse_template()

@app.route("/documents", methods=["GET"])
def list_documents():
    try:
        docs = collection.find({})
        docs_list = []
        for doc in docs:
            # Convert ObjectId to string for JSON serialization
            doc['_id'] = str(doc['_id']) if '_id' in doc else None
            doc['uploaded_at'] = doc['uploaded_at'].isoformat() if 'uploaded_at' in doc else None
            docs_list.append(doc)
        return jsonify(docs_list)
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur lors de la récupération des documents : {str(e)}"}), 500

@app.route("/add-to-db", methods=["POST"])
def add_to_db():
    try:
        # Use force=True, silent=True to avoid exceptions if JSON is missing or invalid
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "Aucune donnée JSON reçue."}), 400
        structured_json = data.get("structured_data")
        filename = data.get("filename", "uploaded")
        if not structured_json:
            return jsonify({"success": False, "error": "Aucune donnée structurée reçue."}), 400
        collection.insert_one({
            "uploaded_at": datetime.datetime.utcnow(),
            "filename": filename,
            "structured_data": structured_json
        })
        return jsonify({"success": True, "message": "Document ajouté à la base de données."})
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Log the full traceback for debugging
        return jsonify({"success": False, "error": f"Erreur serveur : {str(e)}"}), 500

@app.route("/update-document", methods=["POST"])
def update_document():
    try:
        from bson.objectid import ObjectId
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "Aucune donnée reçue."}), 400
        
        doc_id = data.get("_id")
        filename = data.get("filename")
        structured_data = data.get("structured_data")
        
        if not doc_id or not filename:
            return jsonify({"success": False, "error": "ID et filename requis."}), 400
        
        try:
            obj_id = ObjectId(doc_id)
        except:
            return jsonify({"success": False, "error": "ID invalide."}), 400
        
        update_data = {
            "filename": filename,
            "structured_data": structured_data if structured_data else {},
            "updated_at": datetime.datetime.utcnow()
        }
        
        result = collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Document non trouvé."}), 404
        
        return jsonify({"success": True, "message": "Document mis à jour avec succès."})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": f"Erreur serveur : {str(e)}"}), 500

@app.route("/delete-document", methods=["POST"])
def delete_document():
    try:
        from bson.objectid import ObjectId
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "Aucune donnée reçue."}), 400
        
        doc_id = data.get("_id")
        if not doc_id:
            return jsonify({"success": False, "error": "ID requis."}), 400
        
        try:
            obj_id = ObjectId(doc_id)
        except:
            return jsonify({"success": False, "error": "ID invalide."}), 400
        
        result = collection.delete_one({"_id": obj_id})
        
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Document non trouvé."}), 404
        
        return jsonify({"success": True, "message": "Document supprimé avec succès."})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": f"Erreur serveur : {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
