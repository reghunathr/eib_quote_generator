# download_utils.py
from pathlib import Path
import io, zipfile

def list_pdfs(root: Path) -> set[Path]:
    return set(p for p in root.rglob("*.pdf") if p.is_file())

def read_bytes(p: Path) -> bytes:
    with open(p, "rb") as f:
        return f.read()

def zip_bytes(paths: list[Path]) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            if p.exists():
                zf.writestr(p.name, read_bytes(p))
    buf.seek(0)
    return buf
