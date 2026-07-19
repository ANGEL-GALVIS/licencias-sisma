"""
Asigna un cupo (1-6) al codigo de activacion del cliente y sube a GitHub.

Uso:
  python poner_id.py 1 juan_perez_DESKTOP01
  python poner_id.py 3 --inactivar

Crea: licencia_<ID>.txt (activo)
Actualiza: cupo_0N.txt con el ID
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
MAX_CUPOS = 6


def _slug(cliente_id: str) -> str:
    cid = (cliente_id or "").strip().lower()
    cid = re.sub(r"[^a-z0-9_\-]+", "_", cid)
    cid = re.sub(r"_+", "_", cid).strip("_")
    if not cid or len(cid) < 3:
        raise SystemExit(f"ID invalido: {cliente_id!r}")
    return cid


def _git(*args: str) -> None:
    r = subprocess.run(
        ["git", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        if args and args[0] == "push":
            print(
                "\n  *** El commit quedo en su PC pero NO se subio a GitHub.\n"
                "  Revise internet / login de git y ejecute en esta carpeta:\n"
                "      git push origin HEAD\n",
                file=sys.stderr,
            )
        raise SystemExit(f"git {' '.join(args)} fallo ({r.returncode})")


def _cupo_path(n: int) -> Path:
    return REPO / f"cupo_{n:02d}.txt"


def listar() -> None:
    print("  Cupos de licencia (1-6)")
    print("  " + "-" * 40)
    for i in range(1, MAX_CUPOS + 1):
        p = _cupo_path(i)
        val = p.read_text(encoding="utf-8", errors="ignore").strip() if p.is_file() else "?"
        print(f"  {i:02d}  {val}")


def asignar(n: int, cliente_id: str, *, estado: str = "activo") -> None:
    if n < 1 or n > MAX_CUPOS:
        raise SystemExit(f"Cupo debe ser 1..{MAX_CUPOS}")
    cid = _slug(cliente_id)
    estado = "inactivo" if "inactivo" in estado.lower() else "activo"

    lic = REPO / f"licencia_{cid}.txt"
    lic.write_text(estado + "\n", encoding="utf-8")
    cupo = _cupo_path(n)
    cupo.write_text(f"{cid}\n", encoding="utf-8")

    print(f"  Cupo {n:02d} → {cid} ({estado})")
    print(f"  Archivo: {lic.name}")

    _git("add", lic.name, cupo.name)
    st = subprocess.run(
        ["git", "status", "--porcelain", lic.name, cupo.name],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if not (st.stdout or "").strip():
        print("  Sin cambios que subir.")
        return
    _git("commit", "-m", f"cupo {n:02d}: {cid} ({estado})")
    _git("push", "origin", "master")
    print("  OK subido a GitHub.")


def liberar(n: int) -> None:
    """Desactiva la licencia del cupo y lo deja LIBRE."""
    if n < 1 or n > MAX_CUPOS:
        raise SystemExit(f"Cupo debe ser 1..{MAX_CUPOS}")
    cupo = _cupo_path(n)
    actual = ""
    if cupo.is_file():
        actual = cupo.read_text(encoding="utf-8", errors="ignore").strip()
    if not actual or actual.upper() == "LIBRE":
        print(f"  Cupo {n:02d} ya estaba LIBRE.")
        return

    cid = _slug(actual)
    lic = REPO / f"licencia_{cid}.txt"
    lic.write_text("inactivo\n", encoding="utf-8")
    cupo.write_text("LIBRE\n", encoding="utf-8")

    print(f"  Cupo {n:02d}: {cid} → inactivo")
    print(f"  Cupo {n:02d}: LIBRE")
    print(f"  Archivo: {lic.name}")

    _git("add", lic.name, cupo.name)
    st = subprocess.run(
        ["git", "status", "--porcelain", lic.name, cupo.name],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if not (st.stdout or "").strip():
        print("  Sin cambios que subir.")
        return
    _git("commit", "-m", f"cupo {n:02d}: LIBRE ({cid} inactivo)")
    _git("push", "origin", "master")
    print("  OK subido a GitHub.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Poner ID en un cupo de licencia (1-6)")
    ap.add_argument("cupo", nargs="?", type=int, help="Numero de cupo 1..6")
    ap.add_argument("cliente_id", nargs="?", help="Codigo de activacion del cliente")
    ap.add_argument("--listar", action="store_true", help="Ver cupos")
    ap.add_argument("--inactivar", action="store_true", help="Dejar inactivo")
    ap.add_argument(
        "--liberar",
        type=int,
        metavar="N",
        help="Liberar cupo N (inactiva licencia y deja LIBRE)",
    )
    args = ap.parse_args(argv)

    if args.liberar is not None:
        print("=" * 50)
        liberar(args.liberar)
        print("=" * 50)
        listar()
        return 0

    if args.listar or args.cupo is None:
        listar()
        if args.cupo is None and not args.listar:
            print()
            print("  Uso: poner_id.bat 1 CODIGO_DEL_CLIENTE")
            print("       poner_id.bat --listar")
            print("       liberar_cupo.bat")
        return 0

    if not args.cliente_id:
        print("  Falta el ID del cliente.")
        print("  Uso: poner_id.bat 1 CODIGO_DEL_CLIENTE")
        return 1

    estado = "inactivo" if args.inactivar else "activo"
    print("=" * 50)
    asignar(args.cupo, args.cliente_id, estado=estado)
    print("=" * 50)
    listar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
