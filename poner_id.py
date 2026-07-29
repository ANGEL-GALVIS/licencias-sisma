# -*- coding: utf-8 -*-
"""
Activa una licencia con solo el ID del cliente.

Uso sencillo:
  poner_id.bat
      -> pide el ID, usa el primer cupo LIBRE, activa y sube a GitHub

Tambien:
  poner_id.bat serviciosemergency_emergency
  poner_id.bat 3 serviciosemergency_emergency
  poner_id.bat --listar
  poner_id.bat --liberar 3
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from git_local import REPO, ensure_repo, run_git

MAX_CUPOS = 12
LICENSE_OWNER = "ANGEL-GALVIS"
LICENSE_REPO = "licencias-sisma"
LICENSE_BRANCH = "master"


def _print(msg: str = "") -> None:
    """Evita UnicodeEncodeError en consolas Windows cp1252."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def _slug(cliente_id: str) -> str:
    """
    Normaliza el ID que pega el proveedor.
    Acepta: ID puro, licencia_ID, licencia_ID.txt, hasta con licencia_ duplicado.
    """
    cid = (cliente_id or "").strip().lower()
    cid = cid.strip('"').strip("'")
    # Quitar rutas / basura si pegaron path
    if "/" in cid or "\\" in cid:
        cid = Path(cid).name
    if cid.endswith(".txt"):
        cid = cid[:-4]
    # Quitar TODOS los prefijos licencia_ (evita licencia_licencia_...)
    while cid.startswith("licencia_"):
        cid = cid[len("licencia_") :]
    cid = re.sub(r"[^a-z0-9_\-]+", "_", cid)
    cid = re.sub(r"_+", "_", cid).strip("_")
    if not cid or len(cid) < 3:
        raise SystemExit(f"ID invalido: {cliente_id!r}")
    return cid


def _git(*args: str) -> None:
    run_git(*args)


def _cupo_path(n: int) -> Path:
    return REPO / f"cupo_{n:02d}.txt"


def _leer_cupo(n: int) -> str:
    p = _cupo_path(n)
    if not p.is_file():
        return "LIBRE"
    return p.read_text(encoding="utf-8", errors="ignore").strip() or "LIBRE"


def listar() -> None:
    _print("  Cupos de licencia (1-12)")
    _print("  " + "-" * 40)
    for i in range(1, MAX_CUPOS + 1):
        _print(f"  {i:02d}  {_leer_cupo(i)}")


def _primer_cupo_libre() -> int | None:
    for i in range(1, MAX_CUPOS + 1):
        if _leer_cupo(i).upper() == "LIBRE":
            return i
    return None


def _cupo_de_cliente(cid: str) -> int | None:
    """Si el ID ya esta en un cupo, devolver ese numero."""
    for i in range(1, MAX_CUPOS + 1):
        if _leer_cupo(i) == cid:
            return i
    return None


def _limpiar_duplicados_malos(cid: str) -> list[str]:
    """
    Si existe licencia_licencia_<id>.txt (error tipico al pegar mal),
    lo deja inactivo para no confundir.
    """
    tocados: list[str] = []
    malo = REPO / f"licencia_licencia_{cid}.txt"
    if malo.is_file():
        malo.write_text("inactivo\n", encoding="utf-8")
        tocados.append(malo.name)
    return tocados


def _verificar_remoto(cid: str) -> bool:
    """True si GitHub ya sirve licencia_<id>.txt = activo."""
    nombre = f"licencia_{cid}.txt"
    headers = {
        "User-Agent": "SismaLicActivate/1.0",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    urls = [
        (
            f"https://raw.githubusercontent.com/{LICENSE_OWNER}/{LICENSE_REPO}/"
            f"{LICENSE_BRANCH}/{nombre}?t={int(time.time())}"
        ),
        (
            f"https://api.github.com/repos/{LICENSE_OWNER}/{LICENSE_REPO}/"
            f"contents/{nombre}?ref={LICENSE_BRANCH}"
        ),
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8", "ignore").strip()
            # API contents devuelve JSON con content en base64
            if '"content"' in body and '"encoding"' in body:
                data = json.loads(body)
                raw = base64.b64decode(data.get("content", "")).decode(
                    "utf-8", "ignore"
                )
                estado = raw.strip().lower()
            else:
                estado = body.lower()
            ok = "activo" in estado and "inactivo" not in estado
            _print(f"  Remoto {nombre}: {estado or '(vacio)'}{' OK' if ok else ''}")
            return ok
        except urllib.error.HTTPError as exc:
            _print(f"  Remoto {nombre}: HTTP {exc.code} ({url.split('?',1)[0].rsplit('/',1)[-1]})")
            continue
        except Exception as exc:
            _print(f"  Remoto: no se pudo verificar ({exc})")
            continue
    return False


def _commit_y_push(paths: list[str], mensaje: str) -> None:
    if not paths:
        return
    ensure_repo()
    _git("add", *paths)
    st = run_git("status", "--porcelain", *paths, check=False)
    if not (st.stdout or "").strip():
        _print("  Sin cambios locales que commitear (ya estaban iguales).")
        # Igual hay que confirmar remoto: a veces el archivo local existe
        # pero nunca se subio (carpeta sin .git).
        return
    _git("commit", "-m", mensaje)
    _git("push", "origin", "master")
    _print("  OK subido a GitHub.")


def asignar(n: int | None, cliente_id: str, *, estado: str = "activo") -> None:
    ensure_repo()
    cid = _slug(cliente_id)
    estado = "inactivo" if "inactivo" in estado.lower() else "activo"

    # Si ya estaba en un cupo, reutilizar ese (reactivar / actualizar)
    ya = _cupo_de_cliente(cid)
    if n is None:
        if ya is not None:
            n = ya
            _print(f"  ID ya estaba en cupo {n:02d} -> se actualiza")
        else:
            n = _primer_cupo_libre()
            if n is None:
                raise SystemExit("No hay cupos LIBRE (1-12). Libere uno primero.")
            _print(f"  Cupo libre automatico: {n:02d}")
    else:
        if n < 1 or n > MAX_CUPOS:
            raise SystemExit(f"Cupo debe ser 1..{MAX_CUPOS}")
        actual = _leer_cupo(n)
        if actual.upper() != "LIBRE" and actual != cid:
            _print(f"  AVISO: el cupo {n:02d} tenia '{actual}' -> se reemplaza")

    if cliente_id.strip().lower() != cid:
        _print(f"  ID limpio: {cid}")
        _print(f"  (pegado era: {cliente_id.strip()})")

    lic = REPO / f"licencia_{cid}.txt"
    lic.write_text(estado + "\n", encoding="utf-8")
    cupo = _cupo_path(n)
    cupo.write_text(f"{cid}\n", encoding="utf-8")

    extras = _limpiar_duplicados_malos(cid)

    _print(f"  Cupo {n:02d} -> {cid} ({estado})")
    _print(f"  Archivo: {lic.name}")
    if extras:
        _print(f"  Limpieza: {', '.join(extras)} -> inactivo")

    paths = [lic.name, cupo.name, *extras]
    _commit_y_push(paths, f"cupo {n:02d}: {cid} ({estado})")

    if estado == "activo":
        _print("  Verificando GitHub...")
        ok = False
        for intento in range(1, 6):
            if _verificar_remoto(cid):
                ok = True
                break
            if intento < 5:
                _print(f"  Esperando refresco de GitHub ({intento}/5)...")
                time.sleep(3)
        if not ok:
            raise SystemExit(
                "\n  ERROR: el ID NO quedo activo en GitHub.\n"
                "  El cliente NO podra entrar. Revise internet / login git\n"
                "  y vuelva a ejecutar: poner_id.bat " + cid + "\n"
            )
        _print("  Listo: el cliente ya puede entrar con este ID.")


def liberar(n: int) -> None:
    if n < 1 or n > MAX_CUPOS:
        raise SystemExit(f"Cupo debe ser 1..{MAX_CUPOS}")
    cupo = _cupo_path(n)
    actual = _leer_cupo(n)
    if not actual or actual.upper() == "LIBRE":
        _print(f"  Cupo {n:02d} ya estaba LIBRE.")
        return

    cid = _slug(actual)
    lic = REPO / f"licencia_{cid}.txt"
    lic.write_text("inactivo\n", encoding="utf-8")
    cupo.write_text("LIBRE\n", encoding="utf-8")
    extras = _limpiar_duplicados_malos(cid)

    _print(f"  Cupo {n:02d}: {cid} -> inactivo")
    _print(f"  Cupo {n:02d}: LIBRE")
    paths = [lic.name, cupo.name, *extras]
    _commit_y_push(paths, f"cupo {n:02d}: LIBRE ({cid} inactivo)")


def _pedir_id_interactivo() -> str:
    _print()
    _print("  Pegue el ID del cliente (puede pegar licencia_ID.txt; se limpia solo).")
    try:
        raw = input("  ID: ").strip()
    except EOFError:
        raw = ""
    return raw


def main(argv: list[str] | None = None) -> int:
    # Modo interactivo sin argumentos: solo pedir ID
    raw_argv = list(argv) if argv is not None else sys.argv[1:]

    ap = argparse.ArgumentParser(
        description="Activar licencia con el ID del cliente (cupo automatico)"
    )
    ap.add_argument(
        "a",
        nargs="?",
        help="Cupo (1-12) O ID del cliente si no pone cupo",
    )
    ap.add_argument(
        "b",
        nargs="?",
        help="ID del cliente (si el primer argumento fue el cupo)",
    )
    ap.add_argument("--listar", action="store_true", help="Ver cupos")
    ap.add_argument("--inactivar", action="store_true", help="Dejar inactivo")
    ap.add_argument(
        "--liberar",
        type=int,
        metavar="N",
        help="Liberar cupo N",
    )
    ap.add_argument(
        "--interactivo",
        action="store_true",
        help="Preguntar solo el ID (cupo libre automatico)",
    )
    args = ap.parse_args(raw_argv)

    if args.liberar is not None:
        _print("=" * 50)
        liberar(args.liberar)
        _print("=" * 50)
        listar()
        return 0

    if args.listar and args.a is None and args.b is None and not args.interactivo:
        listar()
        return 0

    cupo: int | None = None
    cliente_id: str | None = None

    # Sin args -> interactivo (solo ID)
    if args.interactivo or (args.a is None and args.b is None and not args.listar):
        listar()
        libre = _primer_cupo_libre()
        if libre is None:
            _print()
            _print("  No hay cupos LIBRE. Use liberar_cupo.bat primero.")
            return 1
        _print()
        _print(f"  Se usara el primer cupo libre: {libre:02d}")
        cliente_id = _pedir_id_interactivo()
        if not cliente_id:
            _print("  Cancelado: falta el ID.")
            return 1
        cupo = None  # auto
    elif args.a is not None and args.b is None:
        # Un solo argumento: si es numero = cupo (pedir ID), si no = ID
        if re.fullmatch(r"\d{1,2}", str(args.a).strip()):
            cupo = int(args.a)
            listar()
            _print()
            _print(f"  Cupo elegido: {cupo:02d}")
            cliente_id = _pedir_id_interactivo()
            if not cliente_id:
                _print("  Cancelado: falta el ID.")
                return 1
        else:
            cliente_id = str(args.a)
            cupo = None
    else:
        # Dos argumentos: cupo + ID
        try:
            cupo = int(str(args.a).strip())
        except (TypeError, ValueError):
            raise SystemExit(f"Cupo invalido: {args.a!r}") from None
        cliente_id = str(args.b)

    assert cliente_id is not None
    estado = "inactivo" if args.inactivar else "activo"
    _print("=" * 50)
    asignar(cupo, cliente_id, estado=estado)
    _print("=" * 50)
    listar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
