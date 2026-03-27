let svcChart = null;
let ipChart  = null;
let allEvents = [];
let currentFilter = 'ALL';

async function refresh() {
  try {
    const [stats, events] = await Promise.all([
      fetch('/api/stats').then(r => r.json()),
      fetch('/api/events?limit=100').then(r => r.json())
    ]);

    allEvents = events;

    document.getElementById('total').textContent =
      stats.total.toLocaleString();
    document.getElementById('unique').textContent =
      stats.unique_ips.toLocaleString();
    document.getElementById('last-update').textContent =
      new Date().toLocaleTimeString();

    // Donut chart
    const svcLabels = stats.by_service.map(s => s.service);
    const svcData   = stats.by_service.map(s => s.count);
    if (!svcChart) {
      svcChart = new Chart(
        document.getElementById('svcChart').getContext('2d'), {
        type: 'doughnut',
        data: { labels: svcLabels, datasets: [{
          data: svcData,
          backgroundColor: ['#7c3aed','#1d4ed8','#047857'],
          borderWidth: 0
        }]},
        options: { plugins: { legend: {
          position: 'right',
          labels: { color: '#94a3b8', font: { size: 12 } }
        }}}
      });
    } else {
      svcChart.data.labels = svcLabels;
      svcChart.data.datasets[0].data = svcData;
      svcChart.update();
    }

    // Bar chart
    const ipLabels = stats.top_ips.map(i => i.ip);
    const ipData   = stats.top_ips.map(i => i.count);
    if (!ipChart) {
      ipChart = new Chart(
        document.getElementById('ipChart').getContext('2d'), {
        type: 'bar',
        data: { labels: ipLabels, datasets: [{
          label: 'Hits', data: ipData,
          backgroundColor: '#3b82f6', borderRadius: 4
        }]},
        options: {
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#94a3b8', font: { size: 11 } },
                 grid: { color: '#1e293b' } },
            y: { ticks: { color: '#94a3b8' },
                 grid: { color: '#334155' } }
          }
        }
      });
    } else {
      ipChart.data.labels = ipLabels;
      ipChart.data.datasets[0].data = ipData;
      ipChart.update();
    }

    renderTable();
  } catch(err) {
    console.error('Refresh error:', err);
  }
}

function renderTable() {
  const filtered = currentFilter === 'ALL'
    ? allEvents
    : allEvents.filter(e => e.service === currentFilter);

  const tbody = document.getElementById('feed-body');
  tbody.innerHTML = filtered.map(e => {
    const time = new Date(e.timestamp).toLocaleTimeString();
    let detail = '—';
    if (e.extra?.body && e.extra.body.includes('password')) {
      detail = e.extra.body;
    } else if (e.extra?.username) {
      detail = `user: ${e.extra.username}`;
    } else if (e.extra?.path) {
      detail = e.extra.path;
    }
    return `<tr>
      <td><code>${time}</code></td>
      <td><span class="badge ${e.service}">${e.service}</span></td>
      <td><code>${e.src_ip}</code></td>
      <td>${e.country}</td>
      <td><code>${detail}</code></td>
      <td><button class="detail-btn" onclick="showDetail(${e.id})">Detail</button></td>
    </tr>`;
  }).join('');
}

function setFilter(f) {
  currentFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => {
    b.classList.remove('active');
  });
  const map = { ALL: 'all', SSH: 'SSH', HTTP: 'HTTP', FTP: 'FTP' };
  document.querySelector(`.filter-btn.${map[f]}`).classList.add('active');
  renderTable();
}

async function showDetail(id) {
  const e = await fetch(`/api/events/${id}`).then(r => r.json());
  const body = document.getElementById('modal-body');
  body.innerHTML = `
    <div class="detail-row">
      <span class="detail-label">ID</span>
      <span class="detail-val">${e.id}</span>
    </div>
    <div class="detail-row">
      <span class="detail-label">Timestamp</span>
      <span class="detail-val">${new Date(e.timestamp).toLocaleString()}</span>
    </div>
    <div class="detail-row">
      <span class="detail-label">Service</span>
      <span class="detail-val"><span class="badge ${e.service}">${e.service}</span></span>
    </div>
    <div class="detail-row">
      <span class="detail-label">Source IP</span>
      <span class="detail-val">${e.src_ip}:${e.src_port}</span>
    </div>
    <div class="detail-row">
      <span class="detail-label">Location</span>
      <span class="detail-val">${e.city}, ${e.country}</span>
    </div>
    <div class="detail-row">
      <span class="detail-label">Extra data</span>
      <span class="detail-val">${JSON.stringify(e.extra, null, 2)}</span>
    </div>
    <div style="margin-top:14px;font-size:12px;color:#64748b">Raw payload</div>
    <div class="raw-box">${e.raw_data || '(no raw data)'}</div>
  `;
  document.getElementById('modal').classList.add('open');
}

function closeModal(event) {
  if (event.target.id === 'modal') closeModalDirect();
}
function closeModalDirect() {
  document.getElementById('modal').classList.remove('open');
}

function exportCSV() {
  const filtered = currentFilter === 'ALL'
    ? allEvents
    : allEvents.filter(e => e.service === currentFilter);

  const header = ['id','timestamp','service','src_ip','country','city','detail'];
  const rows = filtered.map(e => {
    let detail = '';
    if (e.extra?.body) detail = e.extra.body;
    else if (e.extra?.username) detail = `user:${e.extra.username}`;
    else if (e.extra?.path) detail = e.extra.path;
    return [
      e.id,
      e.timestamp,
      e.service,
      e.src_ip,
      e.country,
      e.city,
      `"${detail.replace(/"/g, '""')}"`
    ].join(',');
  });

  const csv = [header.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `honeypot_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

refresh();
setInterval(refresh, 5000);