from pathlib import Path
from typing import Optional
import uuid

from pypdf import PdfReader
from docx import Document

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "uploads"


def save_uploaded_file(uploaded_file, category: str) -> Optional[str]:
    if uploaded_file is None:
        return None
    folder = UPLOAD_DIR / category
    folder.mkdir(parents=True, exist_ok=True)
    suffix = Path(uploaded_file.name).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    destination = folder / safe_name
    destination.write_bytes(uploaded_file.getbuffer())
    return str(destination)


def extract_text(path: Optional[str]) -> str:
    if not path:
        return ""
    file_path = Path(path)
    if not file_path.exists():
        return ""
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            reader = PdfReader(str(file_path))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        if suffix == ".docx":
            doc = Document(str(file_path))
            return "\n".join(p.text for p in doc.paragraphs)
        if suffix in {".txt", ".md"}:
            return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    return ""
