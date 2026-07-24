import io
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pypdf import PdfReader

from app.shared.config.rag_settings import ALLOWED_EXTENSIONS

logger = logging.getLogger(__name__)

MAX_PDF_WORKERS = 8


class TextExtractionError(ValueError):
    pass


def extract_text(filename: str, data: bytes) -> str:
    extension = Path(filename or "file.txt").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise TextExtractionError("Unsupported file extension.")

    if extension in {".txt", ".md"}:
        return _decode_text(data)

    if extension == ".json":
        return _extract_json(data)

    if extension == ".pdf":
        return _extract_pdf(data)

    if extension == ".docx":
        return _extract_docx(data)

    raise TextExtractionError("Unsupported file extension.")


def _decode_text(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TextExtractionError("Text file must be valid UTF-8.") from exc


def _extract_json(data: bytes) -> str:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TextExtractionError("JSON file must contain valid UTF-8 JSON.") from exc
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _extract_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
    except Exception as exc:
        raise TextExtractionError("Unable to read PDF file.") from exc

    pages = reader.pages
    if not pages:
        raise TextExtractionError("PDF did not contain extractable text.")

    worker_count = min(MAX_PDF_WORKERS, len(pages))

    def extract_page(page_index: int) -> str:
        try:
            return pages[page_index].extract_text() or ""
        except Exception:
            logger.warning("Failed to extract PDF page %s", page_index, exc_info=True)
            return ""

    if worker_count <= 1:
        page_texts = [extract_page(0)]
    else:
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            page_texts = list(executor.map(extract_page, range(len(pages))))

    text = "\n\n".join(page.strip() for page in page_texts if page.strip())
    if not text:
        raise TextExtractionError("PDF did not contain extractable text.")
    return text


def _extract_docx(data: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise TextExtractionError("DOCX support is not installed.") from exc

    try:
        document = Document(io.BytesIO(data))
    except Exception as exc:
        raise TextExtractionError("Unable to read DOCX file.") from exc

    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    text = "\n\n".join(paragraphs)
    if not text:
        raise TextExtractionError("DOCX did not contain extractable text.")
    return text
