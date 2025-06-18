import mimetypes

def detect_format(filepath):
    mime, _ = mimetypes.guess_type(filepath)
    return mime or "inconnu"
