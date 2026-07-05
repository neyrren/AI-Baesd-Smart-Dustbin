const $ = id => document.getElementById(id);

function updateStats(data) {
  const total = data.total;
  const oPct  = total > 0 ? Math.round(data.organic   / total * 100) : 0;
  const iPct  = total > 0 ? Math.round(data.inorganic / total * 100) : 0;

  $('total').textContent           = total;
  $('organic-count').textContent   = data.organic;
  $('inorganic-count').textContent = data.inorganic;
  $('organic-bar').style.width     = oPct + '%';
  $('inorganic-bar').style.width   = iPct + '%';
  $('organic-pct').textContent     = oPct + '% of total';
  $('inorganic-pct').textContent   = iPct + '% of total';
}

function updateLatest(latest) {
  if (!latest) return;

  const val  = $('latest-result');
  const pill = $('latest-pill');

  val.textContent = latest.result.charAt(0).toUpperCase() + latest.result.slice(1);
  val.className   = 'latest-value ' + latest.result;
  pill.textContent = latest.result.charAt(0).toUpperCase() + latest.result.slice(1);
  pill.className   = 'latest-pill ' + latest.result;

  $('latest-time').textContent       = latest.time;
  $('latest-confidence').textContent = latest.confidence;
}

function updateHistory(history) {
  const tbody = $('history-body');
  $('history-count').textContent = history.length + ' record' + (history.length !== 1 ? 's' : '');

  if (!history.length) {
    tbody.innerHTML = '<tr class="empty-row"><td colspan="4">No records yet — system is ready and waiting</td></tr>';
    return;
  }

  tbody.innerHTML = [...history].reverse().map(h => `
    <tr>
      <td class="time-text">${h.time}</td>
      <td><span class="result-pill ${h.result}">${h.result}</span></td>
      <td class="conf-text">${h.confidence}</td>
      <td>
        <button class="delete-btn" onclick="deleteRecord(${h.id})" title="Delete record" aria-label="Delete record">
          <i class="ti ti-trash" aria-hidden="true"></i>
        </button>
      </td>
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

async function deleteRecord(id) {
  if (!confirm('Delete this record?')) return;
  try {
    const res = await fetch(`/delete-record/${id}`, { method: 'POST' });
    const data = await res.json();
    if (data.success) refresh();
  } catch (e) {
    alert('Error deleting record');
  }
}

refresh();
setInterval(refresh, 3000);