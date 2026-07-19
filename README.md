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

Si el repo es privado, el cliente necesita token de solo lectura
(configurado por el proveedor de forma oculta al empacar).
