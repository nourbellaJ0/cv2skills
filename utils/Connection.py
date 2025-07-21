import os
import datetime
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient

from utils.extractor import extract_text, clean_text  # assure-toi que ce module existe
from utils.file_detector import detect_format         # facultatif si utilisé ailleurs

# 🔒 Charger les variables d'environnement
load_dotenv()

# 🔗 Connexion à MongoDB Atlas (via .env)
MONGO_URI = os.getenv("mongodb+srv://nourbellaaj:NBkumK0rXzGLPYuX@cluster0.nq7jkzm.mongodb.net/")
client = MongoClient(MONGO_URI)
db = client["cv2skills_db"]
collection = db["cv_documents"]

# 🌐 App Flask
app = Flask(__name__)
CORS(app)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("cv")
    if not file:
        return jsonify({"error": "Aucun fichier reçu"}), 400

    try:
        # 🔍 Traitement du fichier
        text = extract_text(file)
        cleaned = clean_text(text)
        json_data = extract_and_structure(cleaned)  # à implémenter si pas encore fait

        # 💾 Insertion dans MongoDB
        collection.insert_one({
            "uploaded_at": datetime.datetime.utcnow(),
            "filename": file.filename,
            "structured_data": json_data
        })

        return jsonify({"success": True, "data": json_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/documents", methods=["GET"])
def get_documents():
    docs = collection.find({}, {"_id": 0, "filename": 1, "uploaded_at": 1})
    return jsonify(list(docs))

if __name__ == "__main__":
    app.run(debug=True)
