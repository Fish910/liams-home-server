/* status colouring: tag stat blocks as ok / warn / bad from their text */
(function () {
  try {
    function tag() {
      document.querySelectorAll('.service-block').forEach(function (b) {
        var v = b.firstElementChild;
        if (!v) return;
        var t = (v.textContent || '').trim();
        var s = '';
        if (/^(UP|ONLINE)$/i.test(t)) s = 'ok';
        else if (/^(WARN|START)/i.test(t)) s = 'warn';
        else if (/^(DOWN|OFFLINE|UNREACH)/i.test(t)) s = 'bad';
        if (s) b.setAttribute('data-pal', s); else b.removeAttribute('data-pal');
      });
    }
    setInterval(tag, 2000);
    tag();
  } catch (e) {}
})();
