let selectedFile = null;
let sessionHistory = [];

const dropzone    = document.getElementById('dropzone');
const fileInput   = document.getElementById('fileInput');
const preview     = document.getElementById('preview');
const classifyBtn = document.getElementById('classifyBtn');
const spinner     = document.getElementById('spinner');

function showPreview(file) {
  selectedFile = file;
  preview.src = URL.createObjectURL(file);
  preview.style.display = 'block';
  document.getElementById('drop-icon').style.display = 'none';
  document.getElementById('drop-text').style.display = 'none';
  document.getElementById('drop-sub').style.display  = 'none';
  classifyBtn.disabled = false;
  document.getElementById('result-empty').style.display   = 'flex';
  document.getElementById('result-content').style.display = 'none';
}

fileInput.addEventListener('change', e => { if (e.target.files[0]) showPreview(e.target.files[0]); });
dropzone.addEventListener('dragover',  e => { e.preventDefault(); dropzone.classList.add('drag'); });
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag'));
dropzone.addEventListener('drop', e => {
  e.preventDefault(); dropzone.classList.remove('drag');
  if (e.dataTransfer.files[0]) showPreview(e.dataTransfer.files[0]);
});

async function classify() {
  if (!selectedFile) return;
  classifyBtn.disabled = true;
  spinner.style.display = 'block';
  classifyBtn.style.display = 'none';

  try {
    const fd = new FormData();
    fd.append('image', selectedFile);
    const res  = await fetch('/classify', { method: 'POST', body: fd });
    const data = await res.json();

    const pred = data.result;
    const conf = parseFloat(data.confidence);

    document.getElementById('result-empty').style.display   = 'none';
    document.getElementById('result-content').style.display = 'flex';

    const rv = document.getElementById('result-value');
    rv.textContent = pred.charAt(0).toUpperCase() + pred.slice(1);
    rv.className   = 'result-value ' + pred;

    const icon = pred === 'organic' ? 'ti-leaf' : 'ti-recycle';
    document.getElementById('result-badge').innerHTML =
      `<span class="badge ${pred}"><i class="ti ${icon}"></i> ${pred}</span>`;

    document.getElementById('conf-bar').style.width = conf + '%';
    document.getElementById('conf-bar').className   = 'bar-fill ' + pred;
    document.getElementById('conf-val').textContent = data.confidence;

    const now   = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
    const thumb = URL.createObjectURL(selectedFile);
    sessionHistory.unshift({ pred, conf: data.confidence, name: selectedFile.name, time: now, thumb });
    if (sessionHistory.length > 8) sessionHistory.pop();
    renderHistory();

  } catch (_) {
    document.getElementById('result-empty').style.display = 'flex';
    document.getElementById('result-empty').innerHTML =
      '<i class="ti ti-alert-circle" style="color:#dc2626;"></i><span style="color:#dc2626;">Could not classify — check server is running</span>';
  } finally {
    spinner.style.display    = 'none';
    classifyBtn.style.display = 'block';
    classifyBtn.disabled      = false;
  }
}

function renderHistory() {
  const el = document.getElementById('history-list');
  if (!sessionHistory.length) { el.innerHTML = '<p class="history-empty">No classifications yet</p>'; return; }
  el.innerHTML = sessionHistory.map(h => `
    <div class="history-item">
      <img src="${h.thumb}" class="thumb" alt="${h.name}"/>
      <div>
        <div class="history-name">${h.name}</div>
        <div class="history-time">${h.time}</div>
      </div>
      <span class="badge ${h.pred}"><i class="ti ${h.pred === 'organic' ? 'ti-leaf' : 'ti-recycle'}"></i> ${h.pred}</span>
      <span class="history-conf">${h.conf}</span>
    </div>
  `).join('');
}