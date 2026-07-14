"""
File/image intake for Pɛ Adesua.

Two lanes, by MIME type:
  - Images (jpg/png/webp/gif) -> base64-encoded and handed to the VISION
    model directly. Groq's vision model reads pixels, not documents.
  - Documents (pdf/docx/txt/csv) -> text is extracted here, then that text
    is folded into the prompt sent to the normal TEXT model.

Anything we don't know how to read comes back with status "unsupported" so
the request can still succeed with whatever we *could* read, rather than
failing the whole message over one bad file.
"""

import base64
import io

IMAGE_MIME_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"
}

DOCUMENT_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
}

MAX_DOCUMENT_CHARS = 8000  # keep extracted text from blowing out the prompt/context


def classify_file(filename, mimetype):
    """Return 'image', 'document', or 'unsupported' for a given upload."""
    if mimetype in IMAGE_MIME_TYPES:
        return "image"
    if mimetype in DOCUMENT_MIME_TYPES:
        return "document"

    # Fallback by extension, in case the browser/Capacitor sends a generic
    # mimetype like application/octet-stream for some file pickers.
    lower_name = (filename or "").lower()
    if lower_name.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return "image"
    if lower_name.endswith((".pdf", ".txt", ".csv", ".docx")):
        return "document"

    return "unsupported"


def encode_image_to_base64(file_bytes, mimetype):
    """Return a data URL string ready to drop into a Groq vision message."""
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mimetype};base64,{b64}"


def extract_text_from_document(filename, file_bytes, mimetype):
    """
    Extract readable text from a document. Returns (text, error).
    On failure, text is None and error holds a short reason.
    """
    lower_name = (filename or "").lower()

    try:
        if mimetype == "application/pdf" or lower_name.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()

        elif lower_name.endswith(".docx") or mimetype == (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join(p.text for p in doc.paragraphs).strip()

        elif mimetype in ("text/plain", "text/csv") or lower_name.endswith((".txt", ".csv")):
            text = file_bytes.decode("utf-8", errors="ignore").strip()

        else:
            return None, "unsupported document type"

        if not text:
            return None, "no extractable text found (scanned/empty file?)"

        if len(text) > MAX_DOCUMENT_CHARS:
            text = text[:MAX_DOCUMENT_CHARS] + "\n...[truncated]"

        return text, None

    except Exception as e:
        return None, f"could not read file: {e}"


def process_uploaded_files(files):
    """
    files: list of werkzeug FileStorage objects (from request.files.getlist('files')).

    Returns:
      images: list of data-URL strings (base64), for the vision model
      document_text: single combined string of all extracted document text,
                      ready to prepend to the user's message
      attachment_statuses: list of {"name": ..., "status": "read"|"unsupported"}
                            for the frontend to display per-file
    """
    images = []
    document_texts = []
    attachment_statuses = []

    for f in files:
        filename = f.filename or "unnamed file"
        mimetype = f.mimetype or ""
        file_bytes = f.read()

        kind = classify_file(filename, mimetype)

        if kind == "image":
            images.append(encode_image_to_base64(file_bytes, mimetype or "image/jpeg"))
            attachment_statuses.append({"name": filename, "status": "read"})

        elif kind == "document":
            text, error = extract_text_from_document(filename, file_bytes, mimetype)
            if text:
                document_texts.append(f"[Content of {filename}]\n{text}")
                attachment_statuses.append({"name": filename, "status": "read"})
            else:
                attachment_statuses.append({"name": filename, "status": "unsupported", "reason": error})

        else:
            attachment_statuses.append({"name": filename, "status": "unsupported", "reason": "unrecognized file type"})

    combined_document_text = "\n\n".join(document_texts) if document_texts else ""
    return images, combined_document_text, attachment_statuses
