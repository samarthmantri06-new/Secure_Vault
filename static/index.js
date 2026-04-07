(function () {
  function initStatsOnView() {
    var bar = document.getElementById('stats-bar');
    if (!bar) return;
    var nums = bar.querySelectorAll('.stat-num[data-target]');
    if (!nums.length) return;

    function run() {
      nums.forEach(function (n) {
        var t = parseInt(n.getAttribute('data-target'), 10);
        var cur = 0;
        var step = Math.max(1, Math.ceil(t / 20));
        var id = setInterval(function () {
          cur += step;
          if (cur >= t) {
            cur = t;
            clearInterval(id);
          }
          n.textContent = cur;
        }, 45);
      });
    }

    var started = false;
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!started && entry.isIntersecting) {
            started = true;
            run();
            io.disconnect();
          }
        });
      },
      { threshold: 0.4 }
    );
    io.observe(bar);
  }

  function initNeuralCanvas() {
    var c = document.getElementById('neural-canvas');
    if (!c) return;
    var ctx = c.getContext('2d');
    var nodes = [
      { x: 0.24, y: 0.3, label: 'NODE-A' },
      { x: 0.75, y: 0.3, label: 'NODE-B' },
      { x: 0.56, y: 0.62, label: 'NODE-C' }
    ];
    var t = 0;

    function resize() {
      c.width = window.innerWidth;
      c.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    function draw() {
      t += 0.01;
      ctx.clearRect(0, 0, c.width, c.height);
      var pts = nodes.map(function (n) {
        return {
          x: n.x * c.width + Math.sin(t + n.x * 8) * 4,
          y: n.y * c.height + Math.cos(t * 0.8 + n.y * 7) * 4,
          label: n.label
        };
      });
      ctx.strokeStyle = 'rgba(192,57,43,0.12)';
      ctx.lineWidth = 1;
      for (var i = 0; i < pts.length; i++) {
        for (var j = i + 1; j < pts.length; j++) {
          ctx.beginPath();
          ctx.moveTo(pts[i].x, pts[i].y);
          ctx.lineTo(pts[j].x, pts[j].y);
          ctx.stroke();
        }
      }
      pts.forEach(function (p) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 2.2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(192,57,43,0.26)';
        ctx.fill();
        ctx.font = '9px ui-monospace, monospace';
        ctx.fillStyle = 'rgba(255,255,255,0.18)';
        ctx.fillText(p.label, p.x + 8, p.y + 2);
      });
      requestAnimationFrame(draw);
    }
    draw();
  }

  document.addEventListener('DOMContentLoaded', function () {
    initStatsOnView();
    initNeuralCanvas();
  });
})();
