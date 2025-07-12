import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
def extraer_texto_pdf(ruta):
    try:
        with fitz.open(ruta) as doc:
            texto = ""
            for i, pagina in enumerate(doc):
                if 0 < i < len(doc) - 1:  # ignora portada y final
                    texto += pagina.get_text()
            return texto.strip()
    except Exception as e:
        print(f"[Error al leer] {ruta}: {e}")
        return ""


def obtener_respuesta_pregunta(pregunta, rutas_pdf):
    textos = []
    for ruta in rutas_pdf:
        texto = extraer_texto_pdf(ruta)
        if texto:
            textos.append(texto)

    if not textos:
        return "⚠️ No hay contenido útil en los documentos cargados."

    texto_completo = "\n".join(textos)
    parrafos = [p.strip() for p in texto_completo.split("\n") if len(p.strip()) > 50]

    if not parrafos:
        return "🤖 No encontré contenido útil en los documentos."

    vectorizer = TfidfVectorizer().fit_transform([pregunta] + parrafos)
    vectores = vectorizer.toarray()
    similitudes = cosine_similarity([vectores[0]], vectores[1:])[0]
    mejor_indice = similitudes.argmax()

    return parrafos[mejor_indice][:700]