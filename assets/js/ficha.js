/*
========================================================
CHICUREOLOCAL — FICHA MAESTRA
========================================================

Este archivo controla funcionalidades compartidas por
todas las fichas dedicadas:

1. Configuración de la ficha
2. Sistema de reseñas
3. Tracking de WhatsApp en GA4

La página debe definir antes de cargar este archivo:

window.CHICUREOLOCAL_FICHA = {
  businessId: "identificador-unico"
};

========================================================
*/

document.addEventListener("DOMContentLoaded", () => {

  /* ====================================================
     CONFIGURACIÓN
     ==================================================== */

  const config = window.CHICUREOLOCAL_FICHA || {};

  const BUSINESS_ID =
    String(config.businessId || "").trim();

  if (!BUSINESS_ID) {
    console.error(
      "ChicureoLocal: falta businessId en la configuración de la ficha."
    );
    return;
  }

  const WORKER_BASE =
    "https://chicureolocal-reviews.mherrerab1991.workers.dev";

  const GET_ENDPOINT =
    `${WORKER_BASE}/reviews?taller=${encodeURIComponent(BUSINESS_ID)}`;

  const POST_ENDPOINT =
    `${WORKER_BASE}/reviews`;

  const PAGE_SIZE = 10;


  /* ====================================================
     ANALYTICS — WHATSAPP
     ==================================================== */

  const whatsappLinks =
    document.querySelectorAll(
      'a[href*="wa.me"], a[href*="whatsapp.com"]'
    );

  whatsappLinks.forEach(link => {

    link.addEventListener("click", () => {

      if (typeof gtag === "function") {

        gtag(
          "event",
          "whatsapp_click",
          {
            event_category: "contact",
            event_label: BUSINESS_ID,
            page_location: window.location.href
          }
        );

      }

    });

  });


  /* ====================================================
     RESEÑAS
     ==================================================== */

  const reviewsSection =
    document.getElementById("reviews");

  /*
  Algunas fichas futuras podrían no utilizar reseñas.
  En ese caso Analytics seguirá funcionando y simplemente
  terminamos aquí el módulo de reviews.
  */

  if (!reviewsSection) {
    return;
  }


  let allReviews = [];
  let visibleCount = 0;


  /* ====================================================
     ELEMENTOS DOM
     ==================================================== */

  const elAvg =
    document.getElementById("reviews-avg");

  const elCount =
    document.getElementById("reviews-count");

  const elStars =
    document.getElementById("reviews-stars");

  const elList =
    document.getElementById("reviews-list");

  const elStatus =
    document.getElementById("reviews-status");

  const btnMore =
    document.getElementById("reviews-more");

  const form =
    document.getElementById("review-form");

  const msg =
    document.getElementById("rf-msg");

  const btn =
    document.getElementById("rf-submit");

  const elName =
    document.getElementById("rf-name");

  const elEmail =
    document.getElementById("rf-email");

  const elRating =
    document.getElementById("rf-rating");

  const elComment =
    document.getElementById("rf-comment");


  /* ====================================================
     VALIDAR INTEGRACIÓN
     ==================================================== */

  const requiredElements = {
    "reviews-avg": elAvg,
    "reviews-count": elCount,
    "reviews-stars": elStars,
    "reviews-list": elList,
    "reviews-status": elStatus,
    "reviews-more": btnMore,
    "review-form": form,
    "rf-msg": msg,
    "rf-submit": btn,
    "rf-name": elName,
    "rf-email": elEmail,
    "rf-rating": elRating,
    "rf-comment": elComment
  };

  const missing =
    Object.entries(requiredElements)
      .filter(([, element]) => !element)
      .map(([id]) => id);

  if (missing.length) {

    console.error(
      "ChicureoLocal Reviews: faltan IDs:",
      missing
    );

    if (elStatus) {

      elStatus.textContent =
        "Error de integración del módulo de reseñas.";

      elStatus.style.display =
        "block";

    }

    return;

  }


  /* ====================================================
     UTILIDADES
     ==================================================== */

  function setStatus(text, show = true) {

    elStatus.textContent = text;

    elStatus.style.display =
      show ? "block" : "none";

  }


  function setMsg(text, show = true) {

    msg.textContent = text;

    msg.style.display =
      show ? "block" : "none";

  }


  function esc(value) {

    return String(value ?? "")

      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  }


  function formatDate(iso) {

    try {

      const date =
        new Date(iso);

      return date.toLocaleDateString(
        "es-CL",
        {
          year: "numeric",
          month: "short",
          day: "2-digit"
        }
      );

    }

    catch {

      return String(
        iso ?? ""
      );

    }

  }


  function starsFromAvg(avg) {

    const rounded =
      Math.round(avg * 2) / 2;

    const full =
      Math.floor(rounded);

    return {

      rounded,

      out:
        "★".repeat(full) +
        "☆".repeat(5 - full)

    };

  }


  /* ====================================================
     RENDER DE RESEÑA
     ==================================================== */

  function renderReview(review) {

    const rating =
      Number(
        review?.rating || 0
      );

    const clamped =
      Math.max(
        0,
        Math.min(
          5,
          rating
        )
      );

    const stars =
      "★".repeat(clamped) +
      "☆".repeat(5 - clamped);

    const name =
      esc(
        review?.name || "Anónimo"
      );

    const comment =
      esc(
        review?.comment || ""
      );

    const created =
      formatDate(
        review?.created_at
      );

    const box =
      document.createElement("div");

    box.className =
      "review-card";

    box.innerHTML = `

      <div class="review-top">

        <div class="review-name">
          ${name}
        </div>

        <div class="review-date">
          ${created}
        </div>

      </div>

      <div
        class="review-stars"
        aria-label="Evaluación"
      >
        ${stars}
      </div>

      <p class="review-text">
        ${comment}
      </p>

    `;

    return box;

  }


  /* ====================================================
     PAGINACIÓN
     ==================================================== */

  function syncMoreButton() {

    if (
      visibleCount <
      allReviews.length
    ) {

      btnMore.style.display =
        "inline-flex";

      btnMore.disabled =
        false;

      const remaining =
        allReviews.length -
        visibleCount;

      const next =
        Math.min(
          PAGE_SIZE,
          remaining
        );

      btnMore.textContent =
        `Ver más reseñas (+${next})`;

    }

    else {

      btnMore.style.display =
        "none";

    }

  }


  function renderVisible() {

    elList.innerHTML = "";

    const visibleReviews =
      allReviews.slice(
        0,
        visibleCount
      );

    visibleReviews.forEach(
      review => {

        elList.appendChild(
          renderReview(review)
        );

      }
    );

    syncMoreButton();

  }


  function showNextPage() {

    visibleCount =
      Math.min(
        allReviews.length,
        visibleCount + PAGE_SIZE
      );

    renderVisible();

  }


  /* ====================================================
     CARGAR RESEÑAS
     ==================================================== */

  async function loadReviews() {

    setStatus(
      "Cargando opiniones…",
      true
    );

    btnMore.style.display =
      "none";

    try {

      const response =
        await fetch(
          GET_ENDPOINT,
          {
            method: "GET",
            cache: "no-store"
          }
        );

      if (!response.ok) {

        throw new Error(
          `HTTP ${response.status}`
        );

      }

      const data =
        await response.json();

      const count =
        Number(
          data?.summary?.count ?? 0
        );

      const avg =
        data?.summary?.avg === null ||
        data?.summary?.avg === undefined

          ? null

          : Number(
              data.summary.avg
            );


      elCount.textContent =
        String(count);


      elAvg.textContent =

        count &&
        avg !== null &&
        Number.isFinite(avg)

          ? avg.toFixed(1)

          : "—";


      if (
        count &&
        avg !== null &&
        Number.isFinite(avg)
      ) {

        const stars =
          starsFromAvg(avg);

        elStars.textContent =
          stars.out;

        elStars.title =
          `${stars.rounded.toFixed(1)} / 5`;

      }

      else {

        elStars.textContent =
          "☆☆☆☆☆";

        elStars.title =
          "Sin reseñas";

      }


      allReviews =
        Array.isArray(
          data?.reviews
        )

          ? data.reviews

          : [];


      if (!allReviews.length) {

        elList.innerHTML = "";

        setStatus(
          "Aún no hay reseñas publicadas para este servicio.",
          true
        );

        btnMore.style.display =
          "none";

        return;

      }


      visibleCount =
        Math.min(
          PAGE_SIZE,
          allReviews.length
        );


      setStatus(
        "",
        false
      );


      renderVisible();

    }

    catch (error) {

      console.error(
        "ChicureoLocal loadReviews:",
        error
      );

      setStatus(
        "No pudimos cargar las reseñas en este momento. Intenta nuevamente más tarde.",
        true
      );

      btnMore.style.display =
        "none";

    }

  }


  /* ====================================================
     BOTÓN VER MÁS
     ==================================================== */

  btnMore.addEventListener(
    "click",
    showNextPage
  );


  /*
  Se conserva esta función global por compatibilidad
  con posibles integraciones futuras.
  */

  window.__reloadReviews =
    loadReviews;


  /* ====================================================
     PUBLICAR RESEÑA
     ==================================================== */

  form.addEventListener(
    "submit",
    async event => {

      event.preventDefault();

      setMsg(
        "",
        false
      );


      const name =
        elName.value.trim();

      const emailRaw =
        elEmail.value.trim();

      const email =
        emailRaw
          ? emailRaw.toLowerCase()
          : null;

      const comment =
        elComment.value.trim();

      const rating =
        Number(
          elRating.value
        );


      /* -------------------------
         VALIDACIONES
         ------------------------- */

      if (!name) {

        return setMsg(
          "Ingresa tu nombre.",
          true
        );

      }


      if (
        email &&
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
      ) {

        return setMsg(
          "Ingresa un email válido o déjalo vacío.",
          true
        );

      }


      if (
        !comment ||
        comment.length < 10
      ) {

        return setMsg(
          "Tu comentario debe tener al menos 10 caracteres.",
          true
        );

      }


      if (
        !Number.isFinite(rating) ||
        rating < 1 ||
        rating > 5
      ) {

        return setMsg(
          "Selecciona una evaluación válida.",
          true
        );

      }


      btn.disabled =
        true;

      setMsg(
        "Publicando…",
        true
      );


      try {

        /*
        IMPORTANTE:
        El Worker actual utiliza taller_id
        como identificador genérico del negocio.
        */

        const payload = {

          taller_id:
            BUSINESS_ID,

          name,

          rating,

          comment,

          email

        };


        const response =
          await fetch(
            POST_ENDPOINT,
            {

              method: "POST",

              headers: {
                "Content-Type":
                  "application/json"
              },

              body:
                JSON.stringify(
                  payload
                )

            }
          );


        const data =
          await response
            .json()
            .catch(
              () => ({})
            );


        if (!response.ok) {

          throw new Error(
            data?.error ||
            `HTTP ${response.status}`
          );

        }


        setMsg(
          "¡Gracias! Tu reseña fue publicada.",
          true
        );


        /* -------------------------
           ANALYTICS — REVIEW
           ------------------------- */

        if (
          typeof gtag ===
          "function"
        ) {

          gtag(
            "event",
            "review_submit",
            {

              event_category:
                "engagement",

              event_label:
                BUSINESS_ID,

              value:
                rating

            }
          );

        }


        elComment.value = "";

        elRating.value = "5";

        elEmail.value = "";


        await loadReviews();

      }

      catch (error) {

        console.error(
          "ChicureoLocal submitReview:",
          error
        );

        setMsg(
          "No se pudo publicar. Intenta nuevamente en unos minutos.",
          true
        );

      }

      finally {

        btn.disabled =
          false;

      }

    }
  );


  /* ====================================================
     INICIAR
     ==================================================== */

  loadReviews();

});
