"""
Registra (o actualiza) una instalación en el repo GitHub licencias-sisma.

Uso (en la PC del proveedor, con gh autenticado):
  python registrar_instalacion.py <cliente_id>
  python registrar_instalacion.py --desde-solicitud path\\SOLICITUD_LICENCIA.txt
  python registrar_instalacion.py --inactivar <cliente_id>

Crea: licencia_<cliente_id>.txt con "activo" o "inactivo" y hace push.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from git_local import REPO as REPO_DIR, ensure_repo, run_git

ARCHIVO = "licencia_{cliente}.txt"


def _slug_ok(cliente_id: str) -> str:
    cid = (cliente_id or "").strip().lower()
    cid = re.sub(r"[^a-z0-9_\-]+", "_", cid)
    cid = re.sub(r"_+", "_", cid).strip("_")
    if not cid or len(cid) < 3:
        raise SystemExit(f"cliente_id invalido: {cliente_id!r}")
    return cid


def _cliente_desde_solicitud(ruta: Path) -> str:
    texto = ruta.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"cliente_id\s*:\s*(\S+)", texto, re.I)
    if not m:
        raise SystemExit(f"No se encontro cliente_id en {ruta}")
    return _slug_ok(m.group(1))


def _git(*args: str) -> None:
    run_git(*args)


def registrar(cliente_id: str, *, estado: str = "activo") -> Path:
    ensure_repo()
    cid = _slug_ok(cliente_id)
    estado = "inactivo" if "inactivo" in estado.lower() else "activo"
    nombre = ARCHIVO.format(cliente=cid)
    destino = REPO_DIR / nombre
    destino.write_text(estado + "\n", encoding="utf-8")
    print(f"  Archivo: {destino.name} → {estado}")

    _git("add", nombre)
    # Commit solo si hay cambios
    st = run_git("status", "--porcelain", nombre, check=False)
    if not (st.stdout or "").strip():
        print("  Sin cambios que subir (ya estaba igual).")
        return destino

    msg = f"licencia {cid}: {estado}"
    _git("commit", "-m", msg)
    _git("push", "origin", "master")
    print(f"  OK subido a GitHub (licencias-sisma).")
    return destino


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Registrar licencia en GitHub")
    ap.add_argument("cliente_id", nargs="?", help="ID de instalacion")
    ap.add_argument(
        "--desde-solicitud",
        type=Path,
        help="Lee cliente_id desde SOLICITUD_LICENCIA.txt",
    )
    ap.add_argument(
        "--inactivar",
        action="store_true",
        help="Pone inactivo en lugar de activo",
    )
    args = ap.parse_args(argv)

    if args.desde_solicitud:
        cid = _cliente_desde_solicitud(args.desde_solicitud)
    elif args.cliente_id:
        cid = _slug_ok(args.cliente_id)
    else:
        ap.print_help()
        return 1

    estado = "inactivo" if args.inactivar else "activo"
    print("=" * 50)
    print(f"  REGISTRAR LICENCIA — {cid} ({estado})")
    print("=" * 50)
    registrar(cid, estado=estado)
    print("=" * 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
