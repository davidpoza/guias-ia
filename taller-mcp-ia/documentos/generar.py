# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab", "python-docx", "pillow"]
# ///
"""Genera los documentos de la demo 2: incidencias.pdf e incidencias.docx.

Ambos tienen el mismo contenido: texto a dos columnas con apartados numerados
(§1 a §8, para comprobar el orden de lectura), tres tablas y un diagrama de
flujo incrustado como imagen (su contenido no aparece descrito en el texto).

Uso:  uv run documentos/generar.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DIR = Path(__file__).parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TITULO = "Procedimiento de gestión de incidencias"
SUBTITULO = "Servicio de soporte · Nimbo Servicios (empresa ficticia) · Versión 2.1"

APARTADOS = [
    ("§1 · Objeto y alcance",
     "Este procedimiento describe cómo se recibe, clasifica, resuelve y cierra "
     "una incidencia en el servicio de soporte. Se aplica a todas las "
     "aplicaciones internas y a los puestos de trabajo gestionados. No cubre "
     "las peticiones de nuevo software ni los cambios planificados, que siguen "
     "su propio circuito de aprobación. Cualquier persona de la organización "
     "puede abrir una incidencia; el equipo de soporte es responsable de que "
     "llegue a buen término y de informar al usuario en cada cambio de estado."),
    ("§2 · Roles",
     "El primer nivel (N1) atiende el canal de entrada, registra y diagnostica. "
     "El segundo nivel (N2) agrupa a especialistas de sistemas, redes y "
     "aplicaciones, y mantiene una guardia permanente para las incidencias "
     "críticas. La coordinación del servicio revisa los indicadores, decide "
     "las excepciones y es el único rol que puede reabrir una incidencia "
     "cerrada hace más de diez días. El usuario, por su parte, debe estar "
     "localizable mientras la incidencia permanezca abierta."),
    ("§3 · Recepción",
     "Las incidencias se reciben por el portal, por correo o por teléfono. "
     "Sea cual sea el canal, el agente de N1 crea un registro en la "
     "herramienta antes de empezar a trabajar: sin registro no hay incidencia. "
     "El registro incluye el usuario afectado, el servicio, una descripción "
     "reproducible y, si es posible, una captura del error. Las llamadas "
     "telefónicas se registran durante la propia conversación para no perder "
     "detalles. El usuario recibe un número de seguimiento en el momento."),
    ("§4 · Clasificación",
     "Cada incidencia recibe una prioridad de P1 a P4 en función del impacto "
     "y de la urgencia. Una P1 detiene un servicio para muchas personas o "
     "afecta a datos sensibles; una P4 es una molestia con alternativa "
     "sencilla. La tabla 1 recoge los tiempos de respuesta comprometidos. Si "
     "hay dudas entre dos prioridades se elige la más alta y se revisa en la "
     "primera hora. La prioridad puede cambiar durante la vida de la "
     "incidencia, y cada cambio debe quedar justificado en el registro."),
    ("§5 · Resolución en primer nivel",
     "El N1 aplica las soluciones de la base de conocimiento y las "
     "comprobaciones básicas: conectividad, credenciales, caché y versión del "
     "cliente. Si encuentra la solución, la documenta en el registro con los "
     "pasos exactos, para que otra persona pueda repetirla. El objetivo es "
     "resolver en N1 al menos siete de cada diez incidencias. Ninguna "
     "incidencia se da por resuelta sin que el usuario lo haya confirmado; "
     "si no confirma, el diagnóstico vuelve a empezar."),
    ("§6 · Escalado",
     "Cuando el N1 no puede resolver, escala al equipo de N2 correspondiente "
     "siguiendo la matriz de la tabla 2. El escalado se hace siempre desde la "
     "herramienta, nunca por mensajería personal, y debe incluir lo que ya se "
     "ha probado. Las incidencias P1 no pasan por el diagnóstico de N1: se "
     "avisa directamente a la guardia. El N2 informa al N1 de la solución para "
     "que la incorpore a la base de conocimiento antes del cierre."),
    ("§7 · Cierre y encuesta",
     "Una incidencia solo se cierra con la confirmación del usuario o, si no "
     "responde, tras tres avisos en cinco días laborables. Al cerrar, el "
     "usuario recibe una encuesta breve de satisfacción con una escala de uno "
     "a cinco. Las respuestas por debajo de tres generan una revisión por "
     "parte de la coordinación. El registro cerrado se conserva dos años y "
     "puede consultarse desde el portal."),
    ("§8 · Mejora continua",
     "Cada trimestre la coordinación publica los indicadores de la tabla 3 y "
     "propone acciones de mejora. Las incidencias repetidas más de cinco veces "
     "en un mes se convierten en un problema y se analizan para eliminar la "
     "causa raíz. Este documento se revisa una vez al año o cuando cambie "
     "alguno de los equipos implicados. Las propuestas de cambio se envían a "
     "la coordinación del servicio."),
]

# Segundo párrafo de cada apartado, para que el texto ocupe varias páginas.
AMPLIACION = [
    "Quedan fuera del alcance las incidencias de proveedores externos que "
    "prestan el servicio completo con su propio centro de atención; en esos "
    "casos el equipo de soporte solo deriva la llamada y registra el número "
    "de seguimiento del proveedor. Tampoco se tratan aquí las solicitudes de "
    "acceso, que dependen del responsable de cada aplicación, ni las alertas "
    "automáticas de monitorización, que tienen su propio protocolo.",
    "Cada rol tiene un suplente nombrado para vacaciones y ausencias. La "
    "lista de suplentes se publica en el portal al inicio de cada mes y la "
    "mantiene la coordinación. Cuando un especialista de N2 cambia de equipo, "
    "sus incidencias abiertas se reasignan el mismo día y el usuario recibe "
    "un aviso con el nombre de la nueva persona responsable.",
    "Fuera del horario laboral solo se atiende el teléfono de guardia, "
    "reservado a incidencias críticas. Los correos recibidos por la noche se "
    "registran a primera hora del día siguiente por orden de llegada. Si un "
    "mismo usuario abre varias incidencias por el mismo problema, el N1 las "
    "agrupa en una sola y conserva la más antigua como principal.",
    "La clasificación inicial la hace siempre una persona, aunque la "
    "herramienta sugiera una prioridad a partir de palabras clave. Las "
    "incidencias que afectan a la dirección o a atención al cliente no suben "
    "de prioridad por ese motivo: se aplica el mismo criterio de impacto y "
    "urgencia que al resto. Las excepciones las autoriza la coordinación y "
    "quedan anotadas con su justificación.",
    "Cuando una solución del N1 no está en la base de conocimiento, el agente "
    "redacta un artículo nuevo en borrador. La coordinación lo revisa en un "
    "plazo de una semana y lo publica o lo devuelve con comentarios. Los "
    "artículos sin uso durante un año se archivan para que la base siga "
    "siendo fácil de consultar y no ofrezca soluciones obsoletas.",
    "Si el equipo de N2 necesita a un proveedor externo, abre el caso con él "
    "y enlaza su referencia en el registro. El reloj de la incidencia no se "
    "detiene mientras se espera al proveedor, salvo acuerdo expreso con el "
    "usuario. El N2 mantiene informado al usuario al menos una vez al día en "
    "las P1 y P2, y una vez por semana en las demás prioridades.",
    "Las incidencias reabiertas en los diez días siguientes al cierre "
    "conservan su número y su historial, y cuentan como no resueltas en los "
    "indicadores del mes. La encuesta no es obligatoria, pero su tasa de "
    "respuesta se publica junto con el resto de indicadores para valorar si "
    "los resultados son representativos.",
    "Las acciones de mejora se registran con un responsable y una fecha "
    "objetivo, y su avance se revisa en la reunión mensual del servicio. Una "
    "acción que se retrasa dos veces se eleva a la dirección del área. El "
    "historial de versiones de este procedimiento se mantiene en el portal y "
    "cada versión indica los apartados que han cambiado.",
]

TABLAS = [
    ("Tabla 1 · Prioridades y tiempos comprometidos",
     ["Prioridad", "Ejemplo", "Primera respuesta", "Resolución objetivo"],
     [["P1 · Crítica", "Caída del ERP para toda la sede", "15 min", "4 h"],
      ["P2 · Alta", "Un departamento sin correo", "1 h", "8 h"],
      ["P3 · Media", "Impresora de planta averiada", "4 h", "3 días"],
      ["P4 · Baja", "Cambio de fondo de escritorio", "1 día", "10 días"]]),
    ("Tabla 2 · Matriz de escalado",
     ["Nivel", "Equipo", "Cuándo escalar", "Canal"],
     [["N1", "Centro de atención", "Entrada de toda incidencia", "Portal / teléfono"],
      ["N2", "Sistemas", "Servidores, almacenamiento, copias", "Cola «N2-SIS»"],
      ["N2", "Redes", "Conectividad, VPN, wifi", "Cola «N2-RED»"],
      ["N2", "Aplicaciones", "Errores funcionales del ERP o CRM", "Cola «N2-APP»"],
      ["Guardia", "N2 de guardia", "Cualquier P1, 24×7", "Teléfono de guardia"]]),
    ("Tabla 3 · Indicadores del primer trimestre",
     ["Indicador", "Enero", "Febrero", "Marzo", "Objetivo"],
     [["Incidencias recibidas", "412", "389", "455", "—"],
      ["Resueltas en N1", "68 %", "71 %", "74 %", "≥ 70 %"],
      ["P1 en plazo", "92 %", "100 %", "96 %", "≥ 95 %"],
      ["Satisfacción media", "4,1", "4,3", "4,2", "≥ 4,0"]]),
]

PIE_DIAGRAMA = "Figura 1 · Flujo de una incidencia"
NOTA_DIAGRAMA = ("La figura 1 resume el circuito completo. Ante cualquier "
                 "discrepancia entre la figura y el texto, prevalece el texto.")


# ---------------------------------------------------------------- diagrama

def generar_diagrama(ruta: Path) -> None:
    W, H, S = 1800, 820, 2  # se dibuja al doble y se reduce para suavizar
    img = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 19 * S)
    fl = ImageFont.truetype(FONT_BOLD, 17 * S)
    azul, gris, verde, ambar = "#dbeafe", "#334155", "#dcfce7", "#fef3c7"

    def p(x, y):
        return (x * S, y * S)

    def texto(cx, cy, t, font=f, fill=gris):
        d.multiline_text(p(cx, cy), t, font=font, fill=fill, anchor="mm",
                         align="center", spacing=4 * S)

    def caja(cx, cy, t, color=azul, w=210, h=86):
        d.rounded_rectangle([p(cx - w / 2, cy - h / 2), p(cx + w / 2, cy + h / 2)],
                            radius=14 * S, fill=color, outline=gris, width=2 * S)
        texto(cx, cy, t)

    def rombo(cx, cy, t, w=210, h=130):
        d.polygon([p(cx, cy - h / 2), p(cx + w / 2, cy), p(cx, cy + h / 2),
                   p(cx - w / 2, cy)], fill=ambar, outline=gris, width=2 * S)
        texto(cx, cy, t)

    def flecha(*puntos, etiqueta=None, pos=None):
        pts = [p(x, y) for x, y in puntos]
        d.line(pts, fill=gris, width=3 * S, joint="curve")
        (x1, y1), (x2, y2) = puntos[-2], puntos[-1]
        dx, dy = (x2 > x1) - (x2 < x1), (y2 > y1) - (y2 < y1)
        a, b = 14, 8
        d.polygon([p(x2, y2), p(x2 - dx * a - dy * b, y2 - dy * a - dx * b),
                   p(x2 - dx * a + dy * b, y2 - dy * a + dx * b)], fill=gris)
        if etiqueta:
            texto(*pos, etiqueta, font=fl, fill="#0f172a")

    Y_MID, Y_TOP, Y_BOT = 330, 120, 540
    caja(130, Y_MID, "Usuario\nreporta la\nincidencia", color="#e2e8f0", w=190, h=110)
    caja(390, Y_MID, "Registro y\nclasificación")
    rombo(650, Y_MID, "¿Prioridad\nP1?")
    caja(920, Y_TOP, "Aviso a la\nguardia N2")
    caja(920, Y_BOT, "Diagnóstico\nen N1")
    caja(1190, Y_TOP, "Resolución\nen N2")
    rombo(1190, Y_BOT, "¿Resuelta\nen N1?")
    rombo(1450, Y_MID, "¿El usuario\nconfirma?", w=220)
    caja(1690, Y_MID, "Cierre y\nencuesta", color=verde, w=190)

    flecha((225, Y_MID), (285, Y_MID))
    flecha((495, Y_MID), (545, Y_MID))
    flecha((650, Y_MID - 65), (650, Y_TOP), (815, Y_TOP), etiqueta="Sí", pos=(620, 220))
    flecha((650, Y_MID + 65), (650, Y_BOT), (815, Y_BOT), etiqueta="No", pos=(620, 440))
    flecha((1025, Y_TOP), (1085, Y_TOP))
    flecha((1025, Y_BOT), (1085, Y_BOT))
    flecha((1190, Y_BOT - 65), (1190, Y_TOP + 43), etiqueta="No", pos=(1220, 330))
    flecha((1295, Y_TOP), (1450, Y_TOP), (1450, Y_MID - 65))
    flecha((1295, Y_BOT), (1310, Y_BOT), (1310, Y_MID), (1340, Y_MID), etiqueta="Sí", pos=(1285, 440))
    flecha((1560, Y_MID), (1595, Y_MID), etiqueta="Sí", pos=(1578, 300))
    flecha((1450, Y_MID + 65), (1450, 720), (920, 720), (920, Y_BOT + 43),
           etiqueta="No: vuelve a diagnóstico", pos=(1185, 750))

    img.resize((W, H), Image.LANCZOS).save(ruta)


# ---------------------------------------------------------------- PDF

def generar_pdf(ruta: Path, png: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (BaseDocTemplate, Frame, FrameBreak, Image as RLImage,
                                    NextPageTemplate, PageBreak, PageTemplate,
                                    Paragraph, Spacer, Table, TableStyle)

    pdfmetrics.registerFont(TTFont("DejaVu", FONT))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_BOLD))

    W, H = A4
    m, gap = 2 * cm, 0.8 * cm
    colw = (W - 2 * m - gap) / 2
    cab = 3 * cm

    def pie(canvas, doc):
        canvas.setFont("DejaVu", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(m, 1.2 * cm, f"{TITULO} · v2.1")
        canvas.drawRightString(W - m, 1.2 * cm, f"Página {doc.page}")

    def columnas(alto_cab=0):
        alto = H - 2 * m - alto_cab
        return [Frame(m, m, colw, alto, id="izq"), Frame(m + colw + gap, m, colw, alto, id="der")]

    portada = PageTemplate("portada", [Frame(m, H - m - cab, W - 2 * m, cab, id="cab")] + columnas(cab), onPage=pie)
    dos_col = PageTemplate("dos_col", columnas(), onPage=pie)
    una_col = PageTemplate("una_col", [Frame(m, m, W - 2 * m, H - 2 * m, id="unica")], onPage=pie)

    doc = BaseDocTemplate(str(ruta), pagesize=A4, title=TITULO, author="Nimbo Servicios (ficticia)",
                          pageTemplates=[portada, dos_col, una_col])

    st_t = ParagraphStyle("t", fontName="DejaVu-Bold", fontSize=20, leading=24, spaceAfter=6)
    st_s = ParagraphStyle("s", fontName="DejaVu", fontSize=10, textColor=colors.grey)
    st_h = ParagraphStyle("h", fontName="DejaVu-Bold", fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=4)
    st_p = ParagraphStyle("p", fontName="DejaVu", fontSize=10, leading=14.5, alignment=TA_JUSTIFY)
    st_c = ParagraphStyle("c", fontName="DejaVu", fontSize=9, leading=11)
    st_cb = ParagraphStyle("cb", parent=st_c, fontName="DejaVu-Bold", textColor=colors.white)
    st_cap = ParagraphStyle("cap", fontName="DejaVu-Bold", fontSize=10.5, spaceBefore=14, spaceAfter=6)

    hist = [Paragraph(TITULO, st_t), Paragraph(SUBTITULO, st_s), NextPageTemplate("dos_col"), FrameBreak()]
    for (titulo, cuerpo), extra in zip(APARTADOS, AMPLIACION):
        hist += [Paragraph(titulo, st_h), Paragraph(cuerpo, st_p), Spacer(1, 5), Paragraph(extra, st_p)]

    hist += [NextPageTemplate("una_col"), PageBreak()]
    for cap, cols, filas in TABLAS:
        datos = [[Paragraph(c, st_cb) for c in cols]] + [[Paragraph(c, st_c) for c in f] for f in filas]
        t = Table(datos, repeatRows=1, hAlign="LEFT", colWidths=[(W - 2 * m) / len(cols)] * len(cols))
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef2ff")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        hist += [Paragraph(cap, st_cap), t]

    ancho = W - 2 * m
    hist += [PageBreak(), Paragraph(PIE_DIAGRAMA, st_cap),
             RLImage(str(png), width=ancho, height=ancho * 820 / 1800),
             Spacer(1, 10), Paragraph(NOTA_DIAGRAMA, st_p)]
    doc.build(hist)


# ---------------------------------------------------------------- DOCX

def generar_docx(ruta: Path, png: Path) -> None:
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    def columnas(seccion, n):
        sp = seccion._sectPr
        cols = sp.find(qn("w:cols"))
        if cols is None:
            cols = OxmlElement("w:cols")
            sp.append(cols)
        cols.set(qn("w:num"), str(n))
        cols.set(qn("w:space"), "454")  # 0,8 cm

    def sombrear(celda, color):
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), color)
        celda._tc.get_or_add_tcPr().append(shd)

    doc = Document()
    doc.core_properties.title = TITULO
    doc.core_properties.author = "Nimbo Servicios (ficticia)"
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = "Calibri", Pt(10.5)
    for s in doc.sections:
        s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2)

    doc.add_heading(TITULO, level=0)
    doc.add_paragraph(SUBTITULO).runs[0].font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    doc.add_section(WD_SECTION.CONTINUOUS)
    for (titulo, cuerpo), extra in zip(APARTADOS, AMPLIACION):
        doc.add_heading(titulo, level=2)
        for texto in (cuerpo, extra):
            doc.add_paragraph(texto).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_section(WD_SECTION.NEW_PAGE)
    for cap, cols, filas in TABLAS:
        doc.add_heading(cap, level=3)
        t = doc.add_table(rows=1, cols=len(cols))
        t.style = "Table Grid"
        for celda, c in zip(t.rows[0].cells, cols):
            celda.text = c
            celda.paragraphs[0].runs[0].font.bold = True
            celda.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            sombrear(celda, "1E3A8A")
        for f in filas:
            for celda, c in zip(t.add_row().cells, f):
                celda.text = c
        doc.add_paragraph()

    doc.add_page_break()
    doc.add_heading(PIE_DIAGRAMA, level=3)
    doc.add_picture(str(png), width=Cm(17))
    doc.add_paragraph(NOTA_DIAGRAMA)

    # Secciones: 0 = título, 1 = texto a dos columnas, 2 = tablas y figura
    for seccion, n in zip(doc.sections, (1, 2, 1)):
        columnas(seccion, n)
    doc.save(ruta)


if __name__ == "__main__":
    png = DIR / "figura-incidencias.png"
    generar_diagrama(png)
    generar_pdf(DIR / "incidencias.pdf", png)
    generar_docx(DIR / "incidencias.docx", png)
    print("Generados:", png.name, "incidencias.pdf", "incidencias.docx")
