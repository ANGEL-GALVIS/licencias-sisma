# -*- coding: utf-8 -*-
"""Git local para licencias_sisma (PC nuevo / PATH / dueño distinto)."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent
REMOTE_URL = "https://github.com/ANGEL-GALVIS/licencias-sisma.git"
DEFAULT_BRANCH = "master"

_GIT_CANDIDATOS = (
    Path(r"C:\Program Files\Git\cmd\git.exe"),
    Path(r"C:\Program Files\Git\bin\git.exe"),
    Path(r"C:\Program Files (x86)\Git\cmd\git.exe"),
)


def encontrar_git() -> str:
    """Ruta a git.exe (PATH o Program Files)."""
    found = shutil.which("git")
    if found:
        return found
    for p in _GIT_CANDIDATOS:
        if p.is_file():
            return str(p)
    raise SystemExit(
        "\n  ERROR: Git no esta instalado o no esta en el PATH.\n"
        "  Solucion: instale Git for Windows (winget install Git.Git)\n"
        "  Luego cierre y abra de nuevo poner_id.bat\n"
    )


def _print(msg: str = "") -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """
    Ejecuta git en este repo.
    Pasa safe.directory en la llamada (sin tocar git config global)
    para PCs donde la carpeta pertenece a otro usuario de Windows.
    """
    git = encontrar_git()
    safe = REPO.resolve().as_posix()
    cmd = [git, "-c", f"safe.directory={safe}", *args]
    r = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and r.returncode != 0:
        if r.stdout:
            try:
                print(r.stdout)
            except UnicodeEncodeError:
                print(r.stdout.encode("ascii", "replace").decode("ascii"))
        if r.stderr:
            print(r.stderr, file=sys.stderr)
        if args and args[0] == "push":
            print(
                "\n  *** El commit quedo en su PC pero NO se subio a GitHub.\n"
                "  Revise internet / login de git y ejecute en esta carpeta:\n"
                "      git push origin master\n",
                file=sys.stderr,
            )
        raise SystemExit(f"git {' '.join(args)} fallo ({r.returncode})")
    return r


def ensure_repo() -> None:
    """
    Garantiza que licencias_sisma sea un clone de GitHub.
    Si falta .git (copia sin historial), lo restaura sin borrar archivos locales.
    """
    git_dir = REPO / ".git"
    if git_dir.is_dir():
        rem = run_git("remote", "get-url", "origin", check=False)
        url = (rem.stdout or "").strip()
        if rem.returncode != 0 or "licencias-sisma" not in url:
            run_git("remote", "remove", "origin", check=False)
            run_git("remote", "add", "origin", REMOTE_URL)
        return

    _print("  AVISO: faltaba .git en licencias_sisma — restaurando desde GitHub...")
    tmp = Path(tempfile.mkdtemp(prefix="licencias-sisma-git-"))
    try:
        git = encontrar_git()
        r = subprocess.run(
            [
                git,
                "clone",
                "--depth",
                "1",
                "--branch",
                DEFAULT_BRANCH,
                REMOTE_URL,
                str(tmp / "clone"),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if r.returncode != 0:
            if r.stderr:
                print(r.stderr, file=sys.stderr)
            raise SystemExit(
                "No se pudo clonar licencias-sisma. Revise internet / acceso a GitHub."
            )
        src_git = tmp / "clone" / ".git"
        if not src_git.is_dir():
            raise SystemExit("Clone incompleto: no hay .git")
        shutil.copytree(src_git, git_dir)
        # Apuntar HEAD/working tree al remoto sin pisar archivos locales
        run_git("reset", "--mixed", f"origin/{DEFAULT_BRANCH}")
        _print("  OK: repositorio Git restaurado (archivos locales conservados).")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
