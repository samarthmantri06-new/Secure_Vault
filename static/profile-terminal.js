(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var box = document.getElementById('terminal-lines');
    if (!box) return;
    var lines = box.querySelectorAll('[data-line]');
    var i = 0;

    function typeLine(el, text, done) {
      var j = 0;
      el.textContent = '';
      function tick() {
        if (j <= text.length) {
          el.textContent = text.slice(0, j);
          j++;
          setTimeout(tick, j < 4 ? 30 : 18);
        } else done();
      }
      tick();
    }

    function next() {
      if (i >= lines.length) return;
      var el = lines[i];
      var text = el.getAttribute('data-line') || '';
      el.style.opacity = '1';
      typeLine(el, text, function () {
        i++;
        setTimeout(next, 120);
      });
    }

    lines.forEach(function (l) {
      l.style.opacity = '0';
    });
    next();
  });
})();
