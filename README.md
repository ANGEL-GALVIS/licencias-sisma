# licencias-sisma

Repo **público** de kill-switch. Un archivo por instalación:

```text
licencia_<cliente_id>.txt
```

Contenido: `activo` o `inactivo`.

El portable lo lee con la API de contenidos de GitHub y, si el token falla
con HTTP 401, vuelve a leer **sin** token. Por eso una licencia no se cae
cuando se revoca el PAT viejo, siempre que este repo siga público.

## Dos tokens (no se mezclan)

| Archivo en el PC del proveedor | Quién lo usa | ¿Se embarca? |
| --- | --- | --- |
| `comun/_lic_token.txt` | Solo `herramientas/subir_delta_github.py` (escritura en `auto-facturar-updates`) | No |
| `comun/_lic_token_client.txt` | Empaque del portable y lectura de este repo + updates | Sí, como `runtime/github_lic_token.txt` |

El token cliente es un PAT **fine-grained** (`github_pat_`) con
**Contents: Read-only** en:

- `ANGEL-GALVIS/auto-facturar-updates` (privado: manifest y ZIP)
- `ANGEL-GALVIS/licencias-sisma` (este repo, público)

No sirve un token clásico (`gho_`, `ghp_`, `ghu_`, `ghs_`). El empaque
aborta si el archivo falta o si el token tiene uno de esos prefijos.

## Rotar

1. Crear el PAT nuevo (fine-grained, Contents: Read-only en los dos repos)
   y guardarlo en `comun/_lic_token_client.txt` (no va a git).
2. Recompilar los `.exe` que embeben `comun/` (`token_cliente.py`,
   `licencia.py`, `actualizador_portable.py`), incluido `ActualizarPortable.exe`.
3. Publicar el delta con extras (`EMPAQUETAR_DELTA` sin `--sin-extras` y
   `SUBIR_DELTA_GITHUB`) o el ZIP completo (`actualizar_portable.bat`).
   El actualizador ya instalado (1.1.21) no copia
   `runtime/github_lic_token.txt`. La semilla va en `assets/_lic_client.txt`
   y el arranque (`MONITOR.bat` / el código nuevo) pisa el token viejo.
4. Cuando los clientes abrieron el producto después de ese update, revocar
   el PAT anterior.

No hace falta un token para leer una licencia de este repo si sigue público.
El token cliente solo hace falta para el repo privado de updates.
