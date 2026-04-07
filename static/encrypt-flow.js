(function () {
  function setStageText(txt) {
    var el = document.getElementById('stage-line');
    if (!el) return;
    el.textContent = txt;
  }

  function resetStage() {
    setStageText('STAGE: IDLE');
  }

  function runStageTicker() {
    var seq = ['STAGE: A', 'STAGE: B', 'STAGE: C', 'STAGE: D'];
    var i = 0;
    setStageText(seq[0]);
    var id = setInterval(function () {
      i++;
      if (i >= seq.length) {
        clearInterval(id);
        return;
      }
      setStageText(seq[i]);
    }, 520);
    return id;
  }

  function showMatrix(cb) {
    var ov = document.getElementById('matrix-overlay');
    if (!ov) {
      cb();
      return;
    }
    ov.style.display = 'block';
    ov.classList.add('matrix-overlay--on');
    var c = document.getElementById('matrix-canvas');
    if (c && c.getContext) {
      var ctx = c.getContext('2d');
      var w = (c.width = window.innerWidth);
      var h = (c.height = window.innerHeight);
      var cols = Math.floor(w / 14);
      var y = [];
      for (var i = 0; i < cols; i++) y[i] = Math.random() * h;
      var chars = '01ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ';
      var frames = 0;
      var maxFrames = 90;
      function tick() {
        frames++;
        ctx.fillStyle = 'rgba(8,8,12,0.12)';
        ctx.fillRect(0, 0, w, h);
        ctx.font = '12px ui-monospace, monospace';
        for (var j = 0; j < cols; j++) {
          var ch = chars[Math.floor(Math.random() * chars.length)];
          ctx.fillStyle = 'rgba(192,57,43,' + (0.15 + Math.random() * 0.35) + ')';
          ctx.fillText(ch, j * 14, y[j]);
          y[j] += 14;
          if (y[j] > h) y[j] = 0;
        }
        if (frames < maxFrames) requestAnimationFrame(tick);
        else {
          ov.classList.remove('matrix-overlay--on');
          ov.style.display = 'none';
          cb();
        }
      }
      tick();
    } else {
      setTimeout(cb, 1800);
    }
  }

  function showSealedThen(fn) {
    var modal = document.getElementById('vault-sealed-modal');
    if (modal) {
      modal.style.display = 'flex';
      modal.setAttribute('aria-hidden', 'false');
    }
    setTimeout(fn, 2200);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('encryptForm');
    if (!form) return;

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var n = window.getVaultFileCount ? window.getVaultFileCount() : 0;
      if (n === 0) {
        alert('Please select at least one file!');
        return;
      }

      var btn = document.getElementById('submit');
      btn.innerText = 'Processing...';
      btn.disabled = true;
      btn.style.opacity = '0.7';

      resetStage();
      var pipeTimer = runStageTicker();

      var formData = new FormData(form);

      try {
        var response = await fetch('/encrypt', {
          method: 'POST',
          body: formData
        });

        if (pipeTimer) clearInterval(pipeTimer);

        if (response.ok) {
          setStageText('STAGE: COMPLETE');
          var blob = await response.blob();
          showMatrix(function () {
            showSealedThen(function () {
              var url = window.URL.createObjectURL(blob);
              var a = document.createElement('a');
              a.href = url;
              a.download = 'SecureVault_Encrypted.zip';
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
              var modal = document.getElementById('vault-sealed-modal');
              if (modal) {
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
              }
              document.body.classList.add('vault-glitch-out');
              setTimeout(function () {
                window.location.href = '/';
              }, 200);
            });
          });
        } else {
          var err = await response.text();
          alert('Error: ' + err);
          btn.innerText = 'Encrypt & Generate Vault';
          btn.disabled = false;
          btn.style.opacity = '1';
          resetStage();
        }
      } catch (err) {
        if (pipeTimer) clearInterval(pipeTimer);
        console.error(err);
        alert('Something went wrong with the connection!');
        btn.innerText = 'Encrypt & Generate Vault';
        btn.disabled = false;
        btn.style.opacity = '1';
        resetStage();
      }
    });
  });
})();
