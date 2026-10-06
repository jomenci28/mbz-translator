# MBZ Translator — Guía para traducir cursos Moodle de ROBOTIX

¡Hola Ana! Este paquete contiene todo lo que necesitas para traducir cursos de
Moodle (archivos `.mbz`) del inglés al español (o cualquier otro idioma) sin
romper el curso al volver a importarlo.

## 0. Requisitos
- macOS o Linux con `python3` instalado (viene de serie en macOS).
- Un editor de texto (Sublime Text, VS Code, BBEdit, TextEdit en modo *plain
  text*, lo que prefieras).

> **NO uses Word ni Pages** para editar los XML — corrompen el archivo.

## 1. La estructura del paquete

```
mbz-translator/
├── LEEME.md                    ← este archivo
├── scripts/
│   └── mbz_tools.py            ← la herramienta (extract / pack / relocalize-images)
├── glosario.md                 ← traducciones estándar que conviene mantener
├── que-traducir.md             ← qué tocar y qué NO tocar dentro de los XML
└── ejemplos/
    └── flujo-completo.sh       ← ejemplo de las 4 órdenes en orden
```

## 2. Flujo de trabajo (las 4 órdenes)

Abre la app **Terminal** (⌘+Espacio → "Terminal") y ejecuta:

```bash
cd ~/Downloads/mbz-translator

# 1) Extraer el .mbz a una carpeta
python3 scripts/mbz_tools.py extract \
    ~/Downloads/curso.en.mbz \
    /tmp/curso/

# 2) Editar los XML traduciendo SOLO los literales (ver que-traducir.md)
#    Abre /tmp/curso/ con tu editor y traduce los textos.

# 3) Reescribir las imágenes workspace al idioma de destino
python3 scripts/mbz_tools.py relocalize-images /tmp/curso/ --target es

# 4) Volver a empaquetar el .mbz traducido
python3 scripts/mbz_tools.py pack \
    /tmp/curso/ \
    ~/Downloads/curso.es.mbz
```

El archivo que sube a Moodle es el `.es.mbz` final.

## 3. Reglas de oro
1. **Solo traduce texto visible**. Si no estás segura, lo más probable es que
   no lo toques.
2. **Nunca cambies números, IDs, claves ni URLs**. La única URL que SÍ
   cambias son las imágenes `workspace_NNN_en.png` → `workspace_NNN_es.png`,
   y eso lo hace el comando `relocalize-images` por ti.
3. **No cambies el nombre de archivos ni la estructura de carpetas** dentro
   del MBZ extraído.
4. **Guarda los XML en UTF-8** (es lo que hacen casi todos los editores por
   defecto).
5. **No tradúzcas las etiquetas HTML** (`<p>`, `<strong>`, `<br>`,
   `&lt;p&gt;`, etc.). Solo el texto entre ellas.
6. **No toques** marcadores Moodle: `$@NULL@$`,
   `$@ROBOTIXVIEWBYID*12345@$`, `@@PLUGINFILE@@/algo.jpg`.

Mira `que-traducir.md` para la lista detallada y `glosario.md` para los
términos comunes.

## 4. Prueba rápida
Antes de mandar el `.mbz` traducido a producción, súbelo a Moodle en modo
*restore* en un curso de prueba. Si Moodle dice algo como
`progress() value out of range`, avísame: probablemente macOS añadió
metadatos al tar (el script ya lo previene, pero por si acaso).

## 5. Si te atascas
- Si un archivo es muy largo (los `robotix.xml` de las lecciones lo son):
  busca con tu editor las etiquetas `<title>`, `<contents>`, `<answer_text>`
  y `<response>` — ahí está todo el texto.
- Si encuentras una frase que no sabes traducir bien, mira en `glosario.md`
  primero.
- Pregúntame y vamos al unísono :)
