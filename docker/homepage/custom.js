// Page reload disabled: it flashed the kiosk screen white and reset the usage graphs.
// The widgets refresh themselves (refreshInterval), so a reload is not needed.
setInterval(() => {
  // location.reload();
}, 15 * 60 * 1000);

/* equal-height columns: set via JS because the stylesheet rules lose to something */
(function () {
  function fill(el, dir) {
    el.style.setProperty('display', 'flex', 'important');
    el.style.setProperty('flex-direction', dir, 'important');
    el.style.setProperty('flex-grow', '1', 'important');
  }
  function apply() {
    var svc = document.getElementById('services');
    if (svc) svc.style.setProperty('align-items', 'stretch', 'important');
    document.querySelectorAll('.services-group').forEach(function (g) {
      g.style.setProperty('display', 'flex', 'important');
      g.style.setProperty('flex-direction', 'column', 'important');
      var ul = g.querySelector('.services-list');
      if (!ul) return;
      for (var e = ul; e && e !== g; e = e.parentElement) fill(e, 'column');
      ul.querySelectorAll(':scope > li.service').forEach(function (li) {
        fill(li, 'row');
        var card = li.firstElementChild;
        if (card) {
          fill(card, 'column');
          card.style.setProperty('justify-content', 'center', 'important');
        }
      });
    });
  }
  setInterval(apply, 2000);
  apply();
})();
