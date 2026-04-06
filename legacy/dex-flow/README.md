# Legacy DeX / Flow Snapshot

Esta carpeta preserva la automatizacion vieja del root historico de `Note9`
que estaba mezclada en el workspace umbrella antes de la reorganizacion de
2026-04-06.

## Que va aqui

- `AI_HANDOFF_NOTE9_2026-03-27.md`
- `auto_connect_flow.py`
- `iniciar_todo.bat`
- `arreglar_dex.bat`

## Estado

Estos archivos ya no representan el path operativo principal del repo.
Se conservan porque documentan y preservan:

- el trabajo previo de Samsung DeX / Samsung Flow
- el uso del Note9 con pantalla danada
- el contexto del root legado antes de separar el workspace umbrella

## Que sigue vivo hoy

El path actual y recomendado vive en:

- `termux_bridge.py`
- `launch_debian_openclaw.sh`
- `launch_openclaw_gateway.sh`
- `launch_openclaw_tui.sh`
- `check_openclaw_health.sh`

## Que sigue siendo util fuera del archive

- `Abrir_Note9_scrcpy.bat`
- `lanzar_scrcpy.bat`
- `configurar_wifi.bat`
- `bypass_dex.bat`

## Artefactos que no se versionaron aqui

Los dumps, APKs, logs, screenshots unicos y otros binarios del root legado
siguen en la capa local del workspace:

`C:\Users\ZN-\Documents\Antigravity\workspace-local\note9-ops\root-legacy`

Se dejaron fuera del repo canonico para no mezclar evidencia pesada y
machine-specific con el path operativo actual.
