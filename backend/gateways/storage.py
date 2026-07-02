from pathlib import Path

from backend.config import settings

_LOCAL_UPLOAD_DIR = Path(__file__).parent.parent.parent / ".local-uploads"


def upload_bytes(key: str, data: bytes, content_type: str) -> str:
    dest = _LOCAL_UPLOAD_DIR / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return key


def download_bytes(key: str) -> bytes:
    return (_LOCAL_UPLOAD_DIR / key).read_bytes()


def delete_file(key: str) -> None:
    local_path = _LOCAL_UPLOAD_DIR / key
    if local_path.exists():
        local_path.unlink()
