/* ChicureoLocal: medición de contactos, sin servicios adicionales. */
(function () {
  var id = 'G-XT9KYK7JP6';
  window.dataLayer = window.dataLayer || [];
  if (typeof window.gtag !== 'function') {
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', id, { anonymize_ip: true });
    var tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(tag);
  }
  document.addEventListener('click', function (event) {
    var a = event.target.closest && event.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var label = (a.textContent || '').trim().toLowerCase();
    var type = '';
    if (/^tel:/i.test(href)) type = 'telefono';
    else if (/wa\.me\/|api\.whatsapp\.com\//i.test(href)) type = /reclamar|actualizar|propietario/.test(label + ' ' + decodeURIComponentSafe(href)) ? 'reclamar_ficha' : 'whatsapp';
    else if (/^https?:\/\//i.test(href) && !/^https?:\/\/(www\.)?chicureolocal\.cl(?:\/|$)/i.test(href)) type = 'sitio_externo';
    if (!type || typeof window.gtag !== 'function') return;
    window.gtag('event', 'contacto_negocio', {
      tipo_contacto: type,
      ficha: location.pathname,
      destino: href.split('?')[0]
    });
  });
  function decodeURIComponentSafe(value) { try { return decodeURIComponent(value); } catch (_) { return value; } }
})();
