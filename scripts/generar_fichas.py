import json
import html
import os
import re
from pathlib import Path
from urllib.parse import quote


# =========================================================
# CHICUREOLOCAL — GENERADOR DE FICHAS
# =========================================================
#
# Lee:
#   data/clientes.json
#   templates/ficha.html
#
# Genera fichas HTML estáticas.
#
# IMPORTANTE:
# Por ahora trabajamos en MODO PRUEBA.
#
# Las páginas se generan dentro de:
#   pruebas/<cliente>/index.html
#
# Por lo tanto, NO reemplazamos ninguna ficha publicada.
# =========================================================


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "clientes.json"
TEMPLATE_FILE = BASE_DIR / "templates" / "ficha.html"

MODO = os.environ.get(
    "CHICUREOLOCAL_MODO",
    "prueba"
).strip().lower()

if MODO not in ("prueba", "produccion"):
    raise ValueError(
        "CHICUREOLOCAL_MODO debe ser 'prueba' o 'produccion'."
    )

PRUEBA = MODO == "prueba"



# =========================================================
# UTILIDADES
# =========================================================

def escapar(valor):
    """
    Escapa texto para insertarlo de forma segura en HTML.
    """

    return html.escape(
        str(valor or ""),
        quote=True
    )


def cargar_json(ruta):
    """
    Carga un archivo JSON en UTF-8.
    """

    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def cargar_texto(ruta):
    """
    Carga un archivo de texto en UTF-8.
    """

    with open(ruta, "r", encoding="utf-8") as archivo:
        return archivo.read()


def escribir_texto(ruta, contenido):
    """
    Crea las carpetas necesarias y escribe el archivo.
    """

    ruta.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)


# =========================================================
# WHATSAPP
# =========================================================

def construir_whatsapp_url(cliente):

    contacto = cliente.get(
        "contacto",
        {}
    )

    numero = str(
        contacto.get(
            "whatsapp",
            ""
        )
    ).strip()

    mensaje = str(
        contacto.get(
            "mensaje_whatsapp",
            ""
        )
    ).strip()

    if not numero:
        return "#"

    if mensaje:
        return (
            f"https://wa.me/{numero}"
            f"?text={quote(mensaje)}"
        )

    return f"https://wa.me/{numero}"


# =========================================================
# RESUMEN
# =========================================================

def construir_resumen(cliente):

    items = cliente.get(
        "resumen",
        []
    )

    bloques = []

    for item in items:

        bloques.append(
            f"""
<span class="pill">
  {escapar(item)}
</span>
            """.strip()
        )

    return "\n".join(bloques)


# =========================================================
# SERVICIOS
# =========================================================

def construir_servicios(cliente):

    servicios = cliente.get(
        "servicios",
        []
    )

    bloques = []

    for servicio in servicios:

        icono = escapar(
            servicio.get(
                "icono",
                ""
            )
        )

        titulo = escapar(
            servicio.get(
                "titulo",
                ""
            )
        )

        descripcion = escapar(
            servicio.get(
                "descripcion",
                ""
            )
        )

        bloques.append(
            f"""
<div class="destination">

  <strong>
    {icono} {titulo}
  </strong>

  <span>
    {descripcion}
  </span>

</div>
            """.strip()
        )

    return "\n".join(bloques)


# =========================================================
# CARACTERÍSTICAS
# =========================================================

def construir_caracteristicas(cliente):

    caracteristicas = cliente.get(
        "caracteristicas",
        []
    )

    bloques = []

    for item in caracteristicas:

        bloques.append(
            f"""
<span class="chip">
  {escapar(item)}
</span>
            """.strip()
        )

    return "\n".join(bloques)


# =========================================================
# INFORMACIÓN PRÁCTICA
# =========================================================

def construir_informacion(cliente):

    informacion = cliente.get(
        "informacion",
        []
    )

    bloques = []

    for item in informacion:

        icono = escapar(
            item.get(
                "icono",
                ""
            )
        )

        etiqueta = escapar(
            item.get(
                "etiqueta",
                ""
            )
        )

        valor = escapar(
            item.get(
                "valor",
                ""
            )
        )

        bloques.append(
            f"""
<div>
  {icono} {etiqueta}:
  <strong>
    {valor}
  </strong>
</div>
            """.strip()
        )

    return "\n".join(bloques)


# =========================================================
# GALERÍA
# =========================================================

def construir_galeria(cliente):

    galeria = cliente.get(
        "galeria",
        []
    )

    if not galeria:
        return ""

    imagenes = []

    for imagen in galeria:

        src = escapar(
            imagen.get(
                "src",
                ""
            )
        )

        alt = escapar(
            imagen.get(
                "alt",
                ""
            )
        )

        if not src:
            continue

        imagenes.append(
            f"""
<div class="g-item">

  <img
    src="{src}"
    alt="{alt}"
    loading="lazy"
  />

</div>
            """.strip()
        )

    if not imagenes:
        return ""

    imagenes_html = "\n".join(imagenes)

    return f"""
<section
  class="card"
  style="margin-top:16px;"
  aria-label="Galería"
>

  <h2>
    Conoce el servicio
  </h2>

  <div class="gallery">

    {imagenes_html}

  </div>

</section>
    """.strip()


# =========================================================
# RESEÑAS — BOTÓN
# =========================================================

def construir_boton_reviews(cliente):

    reviews = cliente.get(
        "reviews",
        {}
    )

    if not reviews.get(
        "activo",
        False
    ):
        return ""

    return """
<a
  class="btn"
  href="#reviews"
>
  ⭐ Ver opiniones
</a>
    """.strip()


# =========================================================
# RESEÑAS — SECCIÓN
# =========================================================

def construir_reviews(cliente):

    reviews = cliente.get(
        "reviews",
        {}
    )

    if not reviews.get(
        "activo",
        False
    ):
        return ""

    titulo = escapar(
        reviews.get(
            "titulo",
            "Opiniones de clientes"
        )
    )

    placeholder = escapar(
        reviews.get(
            "placeholder",
            "Cuéntanos tu experiencia"
        )
    )

    return f"""
<section
  class="card"
  id="reviews"
  style="margin-top:16px;"
  aria-label="{titulo}"
>

  <div class="card-body">

    <h2
      style="
        margin:0;
        font-size:20px;
        letter-spacing:-.2px;
      "
    >
      {titulo}
    </h2>


    <div class="reviews-head">

      <div
        id="reviews-stars"
        class="reviews-stars"
        aria-label="Rating promedio"
      >
        ☆☆☆☆☆
      </div>

      <div class="reviews-meta">

        <strong id="reviews-avg">
          —
        </strong>

        ·

        <span id="reviews-count">
          —
        </span>

        reseñas

      </div>

    </div>


    <div
      id="reviews-status"
      class="note"
      style="margin:0; display:none;"
    ></div>


    <div
      id="reviews-list"
      class="reviews-list"
    ></div>


    <div class="reviews-more-wrap">

      <button
        id="reviews-more"
        class="btn btn-secondary"
        type="button"
        style="display:none;"
      >
        Ver más reseñas
      </button>

    </div>


    <div
      class="review-form-wrap"
      id="review-form-section"
    >

      <h3
        style="
          margin:0 0 10px;
          font-size:16px;
        "
      >
        Dejar una reseña
      </h3>


      <form
        id="review-form"
        class="review-form"
        novalidate
      >

        <label class="field">

          <span class="field-label">
            Tu nombre
          </span>

          <input
            id="rf-name"
            name="name"
            type="text"
            maxlength="40"
            autocomplete="name"
            required
          />

        </label>


        <label class="field">

          <span class="field-label">
            Email (opcional, no se publica)
          </span>

          <input
            id="rf-email"
            name="email"
            type="email"
            maxlength="120"
            autocomplete="email"
            placeholder="tuemail@ejemplo.com"
          />

        </label>


        <label class="field">

          <span class="field-label">
            Evaluación
          </span>

          <select
            id="rf-rating"
            name="rating"
            required
          >

            <option value="5">
              ★★★★★ (5)
            </option>

            <option value="4">
              ★★★★☆ (4)
            </option>

            <option value="3">
              ★★★☆☆ (3)
            </option>

            <option value="2">
              ★★☆☆☆ (2)
            </option>

            <option value="1">
              ★☆☆☆☆ (1)
            </option>

          </select>

        </label>


        <label class="field">

          <span class="field-label">
            Cuéntanos tu experiencia
          </span>

          <textarea
            id="rf-comment"
            name="comment"
            minlength="10"
            maxlength="800"
            placeholder="{placeholder}"
            required
          ></textarea>

        </label>


        <button
          id="rf-submit"
          class="btn btn-primary"
          type="submit"
          style="width:max-content;"
        >
          Publicar reseña
        </button>


        <div
          id="rf-msg"
          class="note"
          style="display:none; margin:0;"
        ></div>

      </form>

    </div>


    <div
      class="disclaimer"
      style="margin-top:10px;"
    >

      <strong>Nota:</strong>
      Las opiniones son publicadas en ChicureoLocal
      y pueden estar sujetas a moderación.

      <br>

      <strong>Privacidad:</strong>
      El email, si lo ingresas,
      <strong>no se publica</strong>
      y se utiliza solo para contacto o seguimiento.

    </div>

  </div>

</section>
    """.strip()


# =========================================================
# SCHEMA.ORG
# =========================================================

def construir_schema(cliente):

    schema_config = cliente.get(
        "schema",
        {}
    )

    contacto = cliente.get(
        "contacto",
        {}
    )

    schema = {
        "@context": "https://schema.org",

        "@type": schema_config.get(
            "tipo",
            "Service"
        ),

        "name": cliente.get(
            "nombre",
            ""
        ),

        "description": cliente.get(
            "descripcion",
            ""
        ),

        "areaServed": schema_config.get(
            "area_served",
            []
        ),

        "serviceType": schema_config.get(
            "service_type",
            cliente.get(
                "categoria",
                ""
            )
        ),

        "provider": {
            "@type": schema_config.get(
                "provider_type",
                "Organization"
            ),

            "telephone": "+" + str(
                contacto.get(
                    "whatsapp",
                    ""
                )
            )
        }
    }

    return json.dumps(
        schema,
        ensure_ascii=False,
        indent=2
    )


# =========================================================
# GENERAR HTML
# =========================================================

def generar_html(template, cliente):

    seo = cliente.get(
        "seo",
        {}
    )

    cta = cliente.get(
        "cta_final",
        {}
    )

    reemplazos = {

        "{{SEO_TITLE}}":
            escapar(
                seo.get(
                    "title",
                    cliente.get(
                        "nombre",
                        ""
                    )
                )
            ),

        "{{SEO_DESCRIPTION}}":
            escapar(
                seo.get(
                    "description",
                    ""
                )
            ),

        "{{SEO_CANONICAL}}":
            escapar(
                seo.get(
                    "canonical",
                    ""
                )
            ),

        "{{OG_TITLE}}":
            escapar(
                seo.get(
                    "og_title",
                    seo.get(
                        "title",
                        ""
                    )
                )
            ),

        "{{OG_DESCRIPTION}}":
            escapar(
                seo.get(
                    "og_description",
                    seo.get(
                        "description",
                        ""
                    )
                )
            ),

        "{{SCHEMA_JSON}}":
            construir_schema(
                cliente
            ),

        "{{BADGE_ICONO}}":
            escapar(
                cliente.get(
                    "badge_icono",
                    ""
                )
            ),

        "{{BADGE_TEXTO}}":
            escapar(
                cliente.get(
                    "badge_texto",
                    ""
                )
            ),

        "{{TITULO}}":
            escapar(
                cliente.get(
                    "titulo",
                    cliente.get(
                        "nombre",
                        ""
                    )
                )
            ),

        "{{DESCRIPCION}}":
            escapar(
                cliente.get(
                    "descripcion",
                    ""
                )
            ),

        "{{RESUMEN_HTML}}":
            construir_resumen(
                cliente
            ),

        "{{WHATSAPP_URL}}":
            escapar(
                construir_whatsapp_url(
                    cliente
                )
            ),

        "{{BOTON_REVIEWS_HTML}}":
            construir_boton_reviews(
                cliente
            ),

        "{{SERVICIOS_HTML}}":
            construir_servicios(
                cliente
            ),

        "{{CARACTERISTICAS_HTML}}":
            construir_caracteristicas(
                cliente
            ),

        "{{INFORMACION_HTML}}":
            construir_informacion(
                cliente
            ),

        "{{NOTA_CONTACTO}}":
            escapar(
                cliente.get(
                    "nota_contacto",
                    ""
                )
            ),

        "{{GALERIA_SECTION}}":
            construir_galeria(
                cliente
            ),

        "{{REVIEWS_SECTION}}":
            construir_reviews(
                cliente
            ),

        "{{CTA_TITULO}}":
            escapar(
                cta.get(
                    "titulo",
                    "¿Quieres contactar?"
                )
            ),

        "{{CTA_TEXTO}}":
            escapar(
                cta.get(
                    "texto",
                    ""
                )
            ),

        "{{CTA_BOTON}}":
            escapar(
                cta.get(
                    "boton",
                    "💬 Contactar por WhatsApp"
                )
            ),

        "{{DISCLAIMER}}":
            escapar(
                cliente.get(
                    "disclaimer",
                    ""
                )
            ),

        "{{BUSINESS_ID}}":
            escapar(
                cliente.get(
                    "business_id",
                    ""
                )
            )
    }

    resultado = template

       for variable, valor in reemplazos.items():
        resultado = resultado.replace(
            variable,
            valor
        )

    # =====================================================
    # VALIDACIÓN DE VARIABLES DE PLANTILLA
    # =====================================================
    #
    # Si por error agregamos una variable nueva a
    # templates/ficha.html y olvidamos programar su
    # reemplazo, detenemos la generación.
    #
    # Esto evita publicar cosas como:
    #
    #   {{TITULO}}
    #   {{WHATSAPP_URL}}
    #   {{VARIABLE_NUEVA}}
    #
    # en una página real.
    # =====================================================

    variables_pendientes = re.findall(
        r"\{\{[A-Z0-9_]+\}\}",
        resultado
    )

    if variables_pendientes:

        variables_unicas = sorted(
            set(variables_pendientes)
        )

        raise ValueError(
            "Variables de plantilla sin reemplazar: "
            + ", ".join(variables_unicas)
        )

    return resultado


# =========================================================
# RUTA DE SALIDA
# =========================================================

def obtener_ruta_salida(cliente_id, cliente):

    # Durante las pruebas generamos una copia segura.
    if PRUEBA:

        return (
            BASE_DIR
            / "pruebas"
            / cliente_id
            / "index.html"
        )

    # En producción se utilizará la ruta definida
    # dentro de clientes.json.
    ruta = str(
        cliente.get(
            "ruta",
            ""
        )
    ).strip("/")

    if not ruta:
        raise ValueError(
            f"El cliente {cliente_id} no tiene ruta."
        )

    return (
        BASE_DIR
        / ruta
        / "index.html"
    )


# =========================================================
# VALIDACIÓN DEL CLIENTE
# =========================================================

def validar_cliente(cliente_id, cliente):

    errores = []

    if not cliente.get("business_id"):
        errores.append(
            "falta business_id"
        )

    if not cliente.get("nombre"):
        errores.append(
            "falta nombre"
        )

    if not cliente.get("ruta"):
        errores.append(
            "falta ruta"
        )

    contacto = cliente.get(
        "contacto",
        {}
    )

    if not contacto.get("whatsapp"):
        errores.append(
            "falta WhatsApp"
        )

    if errores:
        raise ValueError(
            f"{cliente_id}: "
            + ", ".join(errores)
        )


# =========================================================
# GENERADOR PRINCIPAL
# =========================================================

def main():

    print()
    print(
        "=========================================="
    )
    print(
        "CHICUREOLOCAL — GENERADOR DE FICHAS"
    )
    print(
        "=========================================="
    )
    print()


    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"No existe {DATA_FILE}"
        )


    if not TEMPLATE_FILE.exists():

        raise FileNotFoundError(
            f"No existe {TEMPLATE_FILE}"
        )


    clientes = cargar_json(
        DATA_FILE
    )

    template = cargar_texto(
        TEMPLATE_FILE
    )

    generados = 0


    for cliente_id, cliente in clientes.items():

        if not cliente.get(
            "activo",
            True
        ):

            print(
                f"⏭️  {cliente_id}: inactivo"
            )

            continue


        validar_cliente(
            cliente_id,
            cliente
        )


        html_final = generar_html(
            template,
            cliente
        )


        ruta_salida = obtener_ruta_salida(
            cliente_id,
            cliente
        )


        escribir_texto(
            ruta_salida,
            html_final
        )


        print(
            f"✅ {cliente_id}"
        )

        print(
            "   → "
            + str(
                ruta_salida.relative_to(
                    BASE_DIR
                )
            )
        )


        generados += 1


    print()
    print(
        "------------------------------------------"
    )

    print(
        f"Fichas generadas: {generados}"
    )


    if PRUEBA:

        print(
            "MODO PRUEBA ACTIVO"
        )

        print(
            "No se modificaron fichas productivas."
        )


    print(
        "------------------------------------------"
    )
    print()


if __name__ == "__main__":
    main()
