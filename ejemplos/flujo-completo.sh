#!/usr/bin/env bash
# Ejemplo del flujo completo de traducción de un MBZ.
#
# Este script NO se ejecuta de un tirón porque entre el paso 2 y el 3
# tienes que abrir el editor y traducir los XML a mano. Está pensado
# para que copies y pegues las órdenes una a una en la Terminal.
#
# Antes de empezar:
#   - Pon el .mbz original en ~/Downloads/ (o donde prefieras, pero ajusta las rutas).
#   - Abre la app Terminal.
#   - Sitúate en la carpeta del paquete:
#         cd ~/Downloads/mbz-translator

set -euo pipefail

# ----------------------------------------------------------------------
# Configura aquí los nombres de los ficheros (CAMBIA estas dos líneas):
# ----------------------------------------------------------------------
SRC_MBZ="$HOME/Downloads/curso.en.mbz"          # el .mbz original en inglés
DEST_MBZ="$HOME/Downloads/curso.es.mbz"         # el .mbz traducido al español
WORK_DIR="/tmp/curso_traduccion"                # carpeta temporal de trabajo
TARGET_LANG="es"                                # idioma de destino (es, ca, fr…)

# ----------------------------------------------------------------------
# 1) EXTRAER el .mbz a una carpeta de trabajo
# ----------------------------------------------------------------------
echo "Paso 1: Extrayendo $SRC_MBZ …"
python3 scripts/mbz_tools.py extract "$SRC_MBZ" "$WORK_DIR" --force
echo "   Extraído en: $WORK_DIR"
echo

# ----------------------------------------------------------------------
# 2) EDITAR los XML
# ----------------------------------------------------------------------
cat <<MSG
Paso 2: Abre $WORK_DIR con tu editor (Sublime Text, VS Code, BBEdit…)
        y traduce los literales siguiendo las reglas de:
            ../que-traducir.md
            ../glosario.md

        Ficheros principales que vas a tocar:
          - course/course.xml
          - sections/section_*/section.xml
          - activities/label_*/label.xml
          - activities/page_*/page.xml
          - activities/robotix_*/robotix.xml
          - activities/*/grades.xml
          - moodle_backup.xml

        Cuando termines, vuelve a la Terminal y continúa con el paso 3.

        Pulsa ENTER cuando hayas acabado de traducir...
MSG
read -r _

# ----------------------------------------------------------------------
# 3) RELOCALIZAR las imágenes workspace_<id>_<lang>.png
# ----------------------------------------------------------------------
echo "Paso 3: Reescribiendo las referencias a imágenes workspace…"
python3 scripts/mbz_tools.py relocalize-images "$WORK_DIR" --target "$TARGET_LANG"
echo

# ----------------------------------------------------------------------
# 4) REEMPAQUETAR en un nuevo .mbz
# ----------------------------------------------------------------------
echo "Paso 4: Empaquetando el .mbz traducido…"
python3 scripts/mbz_tools.py pack "$WORK_DIR" "$DEST_MBZ"
echo
echo "✅ Listo. El curso traducido está en:"
echo "   $DEST_MBZ"
echo
echo "Súbelo a Moodle en modo 'restaurar' en un curso de prueba antes"
echo "de pasarlo a producción."
