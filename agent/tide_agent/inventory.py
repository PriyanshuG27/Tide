"""What code/doc files existed before the exam. Used to spot old solutions being opened or pasted."""
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tide_common.fingerprint import fingerprints, similarity

TEXT_EXTS = {".c", ".cpp", ".cc", ".h", ".hpp", ".py", ".java", ".js", ".ts", ".sql", ".txt", ".md",
             ".ipynb", ".cs", ".go", ".rs", ".sh"}
DOC_EXTS = {".pdf", ".docx", ".doc", ".pptx"}
SKIP_DIRS = {"appdata", "node_modules", ".git", "windows", "program files", "program files (x86)",
             "$recycle.bin", "programdata", "system volume information", ".vscode", ".cache",
             "__pycache__", "site-packages", "venv", ".venv", "library"}
_FILENAME = re.compile(r"([\w\-.]+\.[A-Za-z0-9]{1,5}|Untitled-\d+)\b", re.IGNORECASE)


@dataclass(frozen=True)
class InvFile:
    path: str
    name: str
    fp: frozenset[int] = field(default=frozenset(), compare=False)


@dataclass
class Inventory:
    files: list[InvFile]

    def __post_init__(self) -> None:
        self._by_name: dict[str, list[str]] = {}
        for f in self.files:
            self._by_name.setdefault(f.name.lower(), []).append(f.path)

    def match_title(self, title: str) -> str | None:
        for token in _FILENAME.findall(title):
            paths = self._by_name.get(token.lower())
            if paths:
                return paths[0]
        return None

    def best_match(self, text: str, min_pct: int = 60) -> tuple[str, int] | None:
        fp = fingerprints(text)
        if not fp:
            return None
        best: tuple[str, int] | None = None
        for f in self.files:
            if f.fp:
                pct = round(similarity(fp, f.fp) * 100)
                if pct >= min_pct and (best is None or pct > best[1]):
                    best = (f.path, pct)
        return best


def build_inventory(roots: list[Path], exclude: Path | None = None, max_files: int = 20000,
                    max_bytes: int = 200_000) -> Inventory:
    files: list[InvFile] = []
    excluded = exclude.resolve() if exclude else None
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            ext = root.suffix.lower()
            if ext in TEXT_EXTS or ext in DOC_EXTS:
                fp: frozenset[int] = frozenset()
                if ext in TEXT_EXTS:
                    try:
                        if root.stat().st_size <= max_bytes:
                            fp = fingerprints(root.read_text(encoding="utf-8", errors="ignore"))
                    except OSError:
                        pass
                files.append(InvFile(str(root), root.name, fp))
            continue
        is_backup_dir = "backups" in str(root).lower()
        for dirpath, dirnames, filenames in os.walk(root):
            here = Path(dirpath).resolve()
            if excluded and (here == excluded or excluded in here.parents):
                dirnames[:] = []
                continue
            if not is_backup_dir:
                dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS and not d.startswith(".")]
            for name in filenames:
                ext = Path(name).suffix.lower()
                if ext not in TEXT_EXTS and ext not in DOC_EXTS and not is_backup_dir:
                    continue
                path = Path(dirpath) / name
                fp: frozenset[int] = frozenset()
                if ext in TEXT_EXTS or is_backup_dir:
                    try:
                        if path.stat().st_size <= max_bytes:
                            fp = fingerprints(path.read_text(encoding="utf-8", errors="ignore"))
                    except OSError:
                        pass
                files.append(InvFile(str(path), name, fp))
                if len(files) >= max_files:
                    return Inventory(files)
    return Inventory(files)


def default_roots() -> list[Path]:
    home = Path.home()
    roots = [home / d for d in ("Desktop", "Documents", "Downloads", "OneDrive", "source", "repos",
                                "projects", "code", "workspace", "IdeaProjects", "PycharmProjects", "dev")]
    if sys.platform == "win32":
        for p in ("C:/code", "C:/projects", "C:/src", "C:/dev", "C:/temp", "C:/test"):
            d = Path(p)
            if d.exists():
                roots.append(d)
        appdata = os.environ.get("APPDATA")
        if appdata:
            vscode_backups = Path(appdata) / "Code" / "Backups"
            if vscode_backups.exists():
                roots.append(vscode_backups)
        import psutil
        for part in psutil.disk_partitions(all=False):
            try:
                mount = Path(part.mountpoint)
                if mount.drive.upper() != "C:":
                    roots.append(mount)
            except Exception:
                pass
    return roots
