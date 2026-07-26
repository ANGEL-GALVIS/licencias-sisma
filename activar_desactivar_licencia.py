# -*- coding: utf-8 -*-
"""
Activar / desactivar licencias (kill-switch en GitHub).

No libera cupos: solo pone activo o inactivo en licencia_<ID>.txt.
Para liberar el cupo use liberar_cupo.bat.

Uso:
  activar_desactivar_licencia.bat
  activar_desactivar_licencia.bat --listar
  activar_desactivar_licencia.bat activar serviciosemergency_emergency
  activar_desactivar_licencia.bat desactivar serviciosemergency_emergency
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent


def _print(msg: str = "") -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def _slug(cliente_id: str) -> str:
    cid = (cliente_id or "").strip().lower()
    cid = cid.strip('"').strip("'")
    if "/" in cid or "\\" in cid:
        cid = Path(cid).name
    if cid.endswith(".txt"):
        cid = cid[:-4]
    while cid.startswith("licencia_"):
        cid = cid[len("licencia_") :]
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
        if r.stdout:
            _print(r.stdout)
        if r.stderr:
            print(r.stderr, file=sys.stderr)
        if args and args[0] == "push":
            print(
                "\n  *** Commit local OK pero NO subio a GitHub.\n"
                "  Ejecute: git push origin HEAD\n",
                file=sys.stderr,
            )
        raise SystemExit(f"git {' '.join(args)} fallo ({r.returncode})")


def _estado_archivo(ruta: Path) -> str:
    raw = ruta.read_text(encoding="utf-8", errors="ignore").strip().lower()
    if "inactivo" in raw:
        return "inactivo"
    if "activo" in raw:
        return "activo"
    return raw or "(vacio)"


def listar_licencias() -> list[tuple[str, str, Path]]:
    """[(cliente_id, estado, path), ...] ordenado."""
    out: list[tuple[str, str, Path]] = []
    for p in sorted(REPO.glob("licencia_*.txt")):
        nombre = p.name
        if not nombre.startswith("licencia_") or not nombre.endswith(".txt"):
            continue
        cid = nombre[len("licencia_") : -len(".txt")]
        # Evitar mostrar basura licencia_licencia_...
        if cid.startswith("licencia_"):
            continue
        out.append((cid, _estado_archivo(p), p))
    return out


def listar() -> None:
    filas = listar_licencias()
    _print()
    _print("  Licencias (activo / inactivo)")
    _print("  " + "-" * 56)
    if not filas:
        _print("  (ninguna licencia_*.txt en esta carpeta)")
        return
    for i, (cid, est, _) in enumerate(filas, start=1):
        marca = "OK " if est == "activo" else "OFF"
        _print(f"  {i:02d}  [{marca}]  {cid}  →  {est}")
    _print("  " + "-" * 56)
    _print(f"  Total: {len(filas)}")
    _print()


def _commit_y_push(nombre: str, mensaje: str) -> None:
    _git("add", nombre)
    st = subprocess.run(
        ["git", "status", "--porcelain", nombre],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if not (st.stdout or "").strip():
        _print("  Sin cambios que subir (ya estaba igual).")
        return
    _git("commit", "-m", mensaje)
    _git("push", "origin", "master")
    _print("  OK subido a GitHub.")


def set_estado(cliente_id: str, *, activo: bool) -> None:
    cid = _slug(cliente_id)
    estado = "activo" if activo else "inactivo"
    destino = REPO / f"licencia_{cid}.txt"
    destino.write_text(estado + "\n", encoding="utf-8")
    _print(f"  Archivo: {destino.name} → {estado}")
    _commit_y_push(destino.name, f"licencia {cid}: {estado}")
    if activo:
        _print("  El cliente puede entrar (espere 10-20 s si GitHub tarda).")
    else:
        _print("  El cliente queda bloqueado al validar licencia.")
        _print("  (El cupo NO se libera; use liberar_cupo.bat si quiere LIBRE.)")


def _elegir_id_de_lista() -> str:
    filas = listar_licencias()
    if not filas:
        raise SystemExit("No hay licencias para elegir. Pegue el ID a mano.")
    listar()
    try:
        raw = input("  Numero de la lista o ID pegado: ").strip()
    except EOFError:
        raw = ""
    if not raw:
        raise SystemExit("Cancelado.")
    if raw.isdigit():
        n = int(raw)
        if n < 1 or n > len(filas):
            raise SystemExit(f"Numero fuera de rango (1-{len(filas)}).")
        return filas[n - 1][0]
    return raw


def menu() -> int:
    while True:
        _print()
        _print("  ================================================")
        _print("   ACTIVAR / DESACTIVAR LICENCIAS")
        _print("  ================================================")
        _print("   1. Listar licencias")
        _print("   2. Activar")
        _print("   3. Desactivar")
        _print("   4. Salir")
        _print("  ================================================")
        try:
            op = input("  Opcion: ").strip()
        except EOFError:
            op = "4"
        if op == "1":
            listar()
        elif op == "2":
            cid = _elegir_id_de_lista()
            _print(f"  Activar: { _slug(cid) }")
            conf = input("  Confirma (S/N) [S]: ").strip() or "S"
            if conf.upper() == "S":
                set_estado(cid, activo=True)
        elif op == "3":
            cid = _elegir_id_de_lista()
            _print(f"  Desactivar: { _slug(cid) }")
            conf = input("  Confirma (S/N) [S]: ").strip() or "S"
            if conf.upper() == "S":
                set_estado(cid, activo=False)
        elif op == "4" or op.lower() in ("q", "salir", "exit"):
            return 0
        else:
            _print("  Opcion no valida.")


def main(argv: list[str] | None = None) -> int:
    raw = list(argv) if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(
        description="Activar o desactivar licencia_<ID>.txt y subir a GitHub"
    )
    ap.add_argument(
        "accion",
        nargs="?",
        choices=("activar", "desactivar", "listar"),
        help="activar | desactivar | listar",
    )
    ap.add_argument("cliente_id", nargs="?", help="ID de instalacion")
    ap.add_argument("--listar", action="store_true", help="Solo listar")
    args = ap.parse_args(raw)

    if args.listar or args.accion == "listar":
        listar()
        return 0

    if args.accion in ("activar", "desactivar"):
        if not args.cliente_id:
            ap.error("Falta cliente_id")
        set_estado(args.cliente_id, activo=(args.accion == "activar"))
        return 0

    return menu()


if __name__ == "__main__":
    raise SystemExit(main())
