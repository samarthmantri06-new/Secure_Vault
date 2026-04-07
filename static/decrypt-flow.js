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
    }, 560);
    return id;
  }

  function updateIntakeMeta() {
    var files = window.getVaultFileList ? window.getVaultFileList() : [];
    var meta = document.getElementById('vault-intake-meta');
    if (!meta) return;
    if (!files.length) {
      meta.innerHTML = '';
      return;
    }
    meta.innerHTML = '<div class="intake-line">ARTIFACT STAGED</div>';
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('decryptForm');
    if (!form) return;

    document.addEventListener('vaultfileschanged', updateIntakeMeta);
    updateIntakeMeta();

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var n = window.getVaultFileCount ? window.getVaultFileCount() : 0;
      if (n === 0) {
        alert('Please select at least one file!');
        return;
      }

      var btn = document.getElementById('submit');
      btn.innerText = 'Decrypting...';
      btn.disabled = true;
      btn.style.opacity = '0.7';

      document.body.classList.add('decrypt-state-scanning');
      resetStage();
      var pipeTimer = runStageTicker();

      var shards = document.getElementById('shard-assembly');
      if (shards) shards.classList.add('shard-assembly--animate');

      var formData = new FormData(form);

      try {
        var response = await fetch('/decrypt', {
          method: 'POST',
          body: formData
        });

        if (pipeTimer) clearInterval(pipeTimer);

        if (response.ok) {
          setStageText('STAGE: COMPLETE');
          document.body.classList.remove('decrypt-state-scanning');
          document.body.classList.add('decrypt-state-open');
          var blob = await response.blob();
          var success = document.getElementById('vault-opened-banner');
          if (success) {
            success.style.display = 'block';
            success.setAttribute('aria-live', 'polite');
          }
          var url = window.URL.createObjectURL(blob);
          var a = document.createElement('a');
          a.href = url;
          a.download = 'SecureVault_Restored.zip';
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
          setTimeout(function () {
            document.body.classList.add('vault-glitch-out');
            setTimeout(function () {
              window.location.href = '/';
            }, 200);
          }, 1600);
        } else {
          var err = await response.text();
          alert('Error: ' + err);
          btn.innerText = 'Retrieve';
          btn.disabled = false;
          btn.style.opacity = '1';
          document.body.classList.remove('decrypt-state-scanning');
          resetStage();
          if (shards) shards.classList.remove('shard-assembly--animate');
        }
      } catch (err) {
        if (pipeTimer) clearInterval(pipeTimer);
        console.error(err);
        alert('Something went wrong with the connection!');
        btn.innerText = 'Retrieve';
        btn.disabled = false;
        btn.style.opacity = '1';
        resetStage();
        document.body.classList.remove('decrypt-state-scanning', 'decrypt-state-open');
        if (shards) shards.classList.remove('shard-assembly--animate');
      }
    });
  });
})();
