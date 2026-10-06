# Qué traducir y qué NO tocar dentro del MBZ

Esta es la lista cerrada de campos que tienes que tocar. Todo lo que no
esté aquí, **déjalo igual**. Moodle es muy quisquilloso: un ID cambiado
o un marcador borrado y el curso deja de funcionar o ni siquiera se
restaura.

## ✅ Sí traducir (texto visible)

Dentro de la carpeta extraída del MBZ, traduce **solo** los siguientes
elementos:

### `course/course.xml`
- `<fullname>…</fullname>` → el título del curso.

### `sections/section_*/section.xml` *(una por sección)*
- `<name>…</name>` → nombre de la sección (ej. "Meet the challenge").
- `<summary>…</summary>` → descripción HTML de la sección. El HTML está
  **codificado** (`&lt;p&gt;` en vez de `<p>`); traduce solo el texto
  visible, no toques las etiquetas.

### `activities/label_*/label.xml`
- `<name>…</name>`
- `<intro>…</intro>` → es texto HTML codificado.

### `activities/page_*/page.xml`
- `<name>…</name>`
- `<intro>…</intro>`
- `<content>…</content>` → cuerpo de la página, HTML codificado.

### `activities/robotix_*/robotix.xml` *(suelen ser los ficheros grandes)*
- `<name>…</name>` → nombre de la actividad.
- `<intro>…</intro>`
- Por cada página de la lección:
  - `<title>…</title>`
  - `<contents>…</contents>` → el enunciado, HTML codificado.
  - Por cada respuesta:
    - `<answer_text>…</answer_text>` → la opción visible para el alumno.
    - `<response>…</response>` → el feedback que ve al elegirla.

### `activities/*/grades.xml`
- `<itemname>…</itemname>` → nombre del ítem en el libro de
  calificaciones; debe coincidir con el `<name>` de la actividad.

### `moodle_backup.xml`
- `<original_course_fullname>…</original_course_fullname>`
- Todos los `<title>` que aparezcan en la lista de actividades y
  secciones. **Deben coincidir literalmente** con los `<name>` que has
  traducido en los XML de cada actividad y sección, o Moodle muestra
  títulos descuadrados.

---

## 🚫 NO tocar

### IDs y claves *(romperían el curso)*
- `<activity id="…">`, `moduleid`, `contextid`, `sectionid`,
  `pageid`, `answer_id`, `userid`, `nextpageid`, `prevpageid`, etc.
- `<shortname>` del curso (ej. `C1350.EN.U7.26`).
- Cualquier `idnumber`.

### URLs *(salvo las imágenes workspace, que las cambia el script)*
- Enlaces externos (`https://…`) no se traducen.
- **Excepción**: las imágenes `workspace_<numero>_<idioma>.png` se
  cambian al idioma de destino, pero **lo hace el comando
  `relocalize-images` automáticamente**. Tú no las toques a mano.

### Configuración de lecciones y quizzes
- `<jumpto>`, `<jumpto2>`, `<score>`, `<grade>`, `<maxanswers>`,
  `<minanswers>`, `<retake>`, etc.
- Cualquier número, booleano (`1`/`0`), timestamp o fecha.

### Marcadores especiales de Moodle
- `$@NULL@$` → marcador de valor nulo. No lo cambies por nada.
- `$@ROBOTIXVIEWBYID*12345@$` → enlace interno a una actividad concreta.
  El número es el ID, **no lo toques**.
- `@@PLUGINFILE@@/algo.jpg` → referencia a un archivo del plugin. No
  traducir ni el marcador ni el nombre de archivo. *(El script
  `relocalize-images` sí reescribe los `@@PLUGINFILE@@/workspace_*`, pero
  ese caso ya está contemplado en el comando 3 del flujo.)*

### Etiquetas HTML
- `<p>`, `<br>`, `<strong>`, `<em>`, `<img>`, `<a>`, `<ul>`, `<li>`, etc.
- Cuando aparecen **codificadas** dentro de un XML (`&lt;p&gt;`,
  `&lt;br&gt;`, `&amp;nbsp;`), tampoco se traducen — solo el texto que hay
  entre ellas.
- Atributos HTML como `src="…"`, `href="…"`, `alt="…"`, `class="…"` se
  dejan tal cual. Si el `alt` es un texto humano que se ve en pantalla,
  ese sí lo traduces; pero los nombres de clase, los IDs CSS, etc.,
  no.

### Bloques de Blockly y nombres internos
- Identificadores como `m2_event_start`, `m2_joystick_up`,
  `m2_motor_power`, `blockid="…"`, `category="…"`, etc., no se traducen.
  Son códigos internos.

### Estructura del MBZ
- No renombres archivos ni carpetas dentro de la carpeta extraída.
- No añadas ni borres ficheros del MBZ.
- `.ARCHIVE_INDEX` y `.ARCHIVE_INDEX.orig` se regeneran solos al
  reempaquetar; no los toques a mano.

---

## 🧐 Trucos para no liarla

1. Antes de cambiar algo, pregúntate: *¿esto lo ve el alumno en pantalla?*
   - Si la respuesta es **sí**, tradúcelo.
   - Si la respuesta es **no** o **no estoy segura**, déjalo.

2. **Busca primero**, traduce después. Usa el buscador del editor (en
   VS Code, `⌘F` o `⌘⇧F` para buscar en toda la carpeta) para localizar
   un literal y traducir todas sus apariciones de forma consistente.

3. **Mismo nombre en sitios distintos**: si traduces el nombre de una
   actividad en su `<name>`, recuerda buscar ese mismo texto en
   `moodle_backup.xml` y en `grades.xml` y traducirlo igual.

4. **HTML codificado**: si ves `&lt;p&gt;Texto&lt;/p&gt;`, traduce solo
   `Texto`. Deja `&lt;p&gt;` y `&lt;/p&gt;` tal cual.

5. **Comprueba con grep antes de entregar**. Desde la carpeta extraída:
   ```bash
   grep -nE "That.{0,4}s right|Good try|Nice try|Multiple Choice|Code your|Upgrade your|Discuss with" \
       activities/*/*.xml sections/*/*.xml moodle_backup.xml
   ```
   Si sale algo, es que te has dejado literales sin traducir.
