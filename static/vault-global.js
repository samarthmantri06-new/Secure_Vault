(function () {
  function resetGlitchState() {
    if (!document.body) return;
    document.body.classList.remove('vault-glitch-out');
    // restart the entrance animation cleanly
    document.body.classList.remove('vault-glitch-in');
    void document.body.offsetHeight; // force reflow
    document.body.classList.add('vault-glitch-in');
  }

  // Fix blank pages when navigating Back/Forward (bfcache restores old classes)
  window.addEventListener('pageshow', function () {
    resetGlitchState();
  });

  document.addEventListener('DOMContentLoaded', function () {
    resetGlitchState();

    document.querySelectorAll('a[href]').forEach(function (link) {
      if (link.getAttribute('data-no-glitch') === 'true') return;
      if (link.getAttribute('href') && link.getAttribute('href').startsWith('#')) return;
      if (link.target === '_blank') return;
      link.addEventListener('click', function (e) {
        var href = link.getAttribute('href');
        if (!href || href.startsWith('javascript:')) return;
        if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.shiftKey) return;
        e.preventDefault();
        document.body.classList.add('vault-glitch-out');
        setTimeout(function () {
          window.location.href = href;
        }, 220);
      });
    });
  });
})();
