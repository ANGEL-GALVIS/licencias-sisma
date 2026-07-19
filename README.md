# Licencias Ecosistema Sisma

Control remoto: activo / inactivo por instalacion (PC del cliente).

## Cupos listos (6)

Hay **6 cupos** libres en GitHub. Cuando el cliente le envie el
**codigo de activacion**, solo ponga el ID:

```bat
poner_id.bat 1 codigo_que_envio_el_cliente
poner_id.bat 2 otro_codigo
poner_id.bat --listar
```

| Cupo | Archivo     | Estado inicial |
|------|-------------|----------------|
| 1    | cupo_01.txt | LIBRE          |
| 2    | cupo_02.txt | LIBRE          |
| 3    | cupo_03.txt | LIBRE          |
| 4    | cupo_04.txt | LIBRE          |
| 5    | cupo_05.txt | LIBRE          |
| 6    | cupo_06.txt | LIBRE          |

Eso crea `licencia_<ID>.txt` con `activo` y lo sube solo a GitHub.

Desactivar un cliente:

```bat
poner_id.bat 1 ese_mismo_codigo --inactivar
```

Tambien sirve (sin cupo):

```bat
registrar_instalacion.bat juan_perez_DESKTOP01
registrar_instalacion.bat --inactivar juan_perez_DESKTOP01
```

## Como funciona

1. El cliente ejecuta `CONFIGURAR_PRIMERA_VEZ.bat`
2. Le aparece un **codigo de activacion** y se lo envia a usted
3. Usted: `poner_id.bat N ese_codigo`
4. El bot, al arrancar, lee en GitHub `licencia_<codigo>.txt`
   - `activo` → arranca
   - `inactivo` o no existe → no arranca

## Demo

- `licencia_CLIENTE_DEMO.txt` → prueba / portable antiguo

## Repo privado

Si el repo es privado, el cliente necesita token de solo lectura:
`SISMA_LIC_TOKEN` o `runtime/github_lic_token.txt` (lo configura el proveedor
antes de entregar, de forma oculta).
