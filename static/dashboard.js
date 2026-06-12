const $ = id => document.getElementById(id);

function updateStats(data) {
  const total = data.total;
  const oPct  = total > 0 ? Math.round(data.organic   / total * 100) : 0;
  const iPct  = total > 0 ? Math.round(data.inorganic / total * 100) : 0;

  $('total').textContent          = total;
  $('organic-count').textContent  = data.organic;
  $('inorganic-count').textContent = data.inorganic;
  $('organic-bar').style.width    = oPct + '%';
  $('inorganic-bar').style.width  = iPct + '%';
  $('organic-pct').textContent    = oPct + '% of total';
  $('inorganic-pct').textContent  = iPct + '% of total';
}

function updateLatest(latest) {
  if (!latest) return;

  const resultEl = $('latest-result');
  const badgeEl  = $('latest-badge');

  resultEl.textContent = latest.result.charAt(0).toUpperCase() + latest.result.slice(1);
  resultEl.className   = 'latest-result-text ' + latest.result;

  badgeEl.textContent  = latest.result.toUpperCase();
  badgeEl.className    = 'latest-badge ' + latest.result;

  $('latest-time').textContent       = latest.time;
  $('latest-confidence').textContent = latest.confidence;
  $('last-conf').textContent         = latest.confidence;
}

function updateHistory(history) {
  const tbody = $('history-body');
  $('history-count').textContent = history.length + ' record' + (history.length !== 1 ? 's' : '');

  if (!history.length) {
    tbody.innerHTML = '<tr class="empty-row"><td colspan="3">No classifications yet — system is ready</td></tr>';
    return;
  }

  tbody.innerHTML = [...history].reverse().map(h => `
    <tr>
      <td class="time-text">${h.time}</td>
      <td><span class="result-pill ${h.result}">${h.result}</span></td>
      <td class="confidence-text">${h.confidence}</td>
    </tr>
  `).join('');
}

async function refresh() {
  try {
    const res  = await fetch('/stats');
    const data = await res.json();
    updateStats(data);
    updateLatest(data.latest);
    updateHistory(data.history);
  } catch (_) {}
}

refresh();
setInterval(refresh, 3000);
