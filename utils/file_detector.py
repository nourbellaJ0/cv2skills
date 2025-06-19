import mimetypes

def detect_format(filepath):
    """
    Détecte le type MIME d'un fichier en fonction de son extension.
    
    :param filepath: chemin absolu du fichier
    :return: type MIME (ex: 'application/pdf') ou 'inconnu' si non déterminé
    """
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type or "inconnu"
