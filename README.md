# Licencias Ecosistema Sisma

Control remoto: activo / inactivo por instalacion (PC del cliente).

## Cupos listos (12)

Hay **12 cupos** en GitHub. Cuando le llegue el codigo de activacion
por correo, asigne el ID:

```bat
poner_id.bat
liberar_cupo.bat
poner_id.bat --listar
```

| Cupo | Archivo      |
|------|--------------|
| 1-12 | cupo_01.txt … cupo_12.txt |

Eso crea `licencia_<ID>.txt` con `activo` y lo sube a GitHub.

Liberar (inactivo + cupo LIBRE):

```bat
liberar_cupo.bat
```

Tambien sirve (sin cupo):

```bat
registrar_instalacion.bat juan_perez_DESKTOP01
registrar_instalacion.bat --inactivar juan_perez_DESKTOP01
```

## Activar / desactivar (kill-switch)

Sin tocar cupos — solo pone `activo` o `inactivo` y sube a GitHub:

```bat
activar_desactivar_licencia.bat
activar_desactivar_licencia.bat --listar
activar_desactivar_licencia.bat activar serviciosemergency_emergency
activar_desactivar_licencia.bat desactivar serviciosemergency_emergency
```

Menu: listar → elegir numero o pegar ID → activar o desactivar.  
Si quiere liberar el cupo (dejar LIBRE), use `liberar_cupo.bat`.

## Como funciona

1. El cliente ejecuta `CONFIGURAR_PRIMERA_VEZ.bat`
2. Usted recibe el **codigo de activacion** por correo
3. Usted: `poner_id.bat` → cupo + ID
4. El bot lee en GitHub `licencia_<codigo>.txt`
   - `activo` → arranca
   - `inactivo` o no existe → no arranca

## Demo

Las licencias de clientes se crean al usar `poner_id.bat`
(`licencia_<ID>.txt`). Los cupos vacíos solo dicen `LIBRE`.

## Repo privado

Si el repo es **privado**, el portable del cliente **debe** llevar
`runtime/github_lic_token.txt` (token de solo lectura al repo).

1. Cree un PAT (fine-grained) con permiso **Contents: Read** solo en
   `ANGEL-GALVIS/licencias-sisma`
2. Guardelo en su PC de proveedor (NO en Git):

```text
comun/_lic_token.txt
```

3. Al empacar, `herramientas\actualizar_portable.bat` lo copia oculto a:

```text
Ecosistema_Sisma_Portable\runtime\github_lic_token.txt
```

Sin ese token, el cliente recibe HTTP 404 y ve
«Instalacion NO registrada» aunque el ID ya este `activo` en GitHub.

Alternativa: haga el repo **publico** (solo contiene activo/inactivo).
Entonces el portable no necesita token.
