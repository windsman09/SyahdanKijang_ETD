// app/static/js/etd8a12.js
// ==========================================
// Prasyarat:
// - Di HTML (device.html / etd8a12.html) HARUS ada:
//   <script>const deviceId = {{ device.id }};</script>
// ==========================================

const API_PREFIX = '/api/etd';
const channelNames = {};

// Elemen DOM
const grid = document.getElementById('grid');
const btnLoad = document.getElementById('btnLoad');


// =========================
// Helper Auth Header
// =========================
function authHeaders() {
  const token = localStorage.getItem('access_token');
  return token ? { 'Authorization': 'Bearer ' + token } : {};
}


// =========================
// Helper Fetch JSON
// =========================
async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);

  if (res.status === 401) {
    // Token invalid / expired
    window.location.href = '/login';
    return;
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json();
}


// =========================
// Load Channel Names (Global)
// =========================
async function loadChannelNames() {
  try {
    const url = `${API_PREFIX}/channels`;
    console.log('[etd8a12] GET', url);

    const arr = await fetchJSON(url, {
      headers: { ...authHeaders() }
    });

    (arr || []).forEach(ch => {
      channelNames[ch.index] = ch.name;
    });

  } catch (e) {
    console.warn('Gagal load channel names:', e.message || e);
    // Tidak fatal, UI tetap jalan
  }
}


// =========================
// Load Channel Status (PER DEVICE)
// =========================
async function loadStatus() {
  grid.innerHTML = '';

  try {
    const url = `${API_PREFIX}/devices/${deviceId}/outputs`;
    console.log('[etd8a12] GET', url);

    const states = await fetchJSON(url, {
      headers: { ...authHeaders() }
    });

    if (!Array.isArray(states)) {
      throw new Error('Format outputs tidak sesuai');
    }

    states.forEach((on, idx) => {
      const channelNo = idx + 1;

      // --- Card container ---
      const card = document.createElement('div');
      card.className = 'ch-card';
      card.style.border = '1px solid #ccc';
      card.style.padding = '12px';
      card.style.margin = '6px';
      card.style.borderRadius = '8px';
      card.style.minWidth = '140px';
      card.style.display = 'inline-block';

      // --- Channel label ---
      const lbl = document.createElement('div');
      lbl.textContent = channelNames[channelNo] ?? ('CH ' + channelNo);
      lbl.style.fontWeight = '600';
      lbl.style.marginBottom = '6px';

      // --- Switch wrapper ---
      const wrap = document.createElement('label');
      wrap.style.display = 'flex';
      wrap.style.alignItems = 'center';
      wrap.style.gap = '8px';
      wrap.style.cursor = 'pointer';

      const sw = document.createElement('input');
      sw.type = 'checkbox';
      sw.checked = !!on;

      const stateText = document.createElement('span');
      stateText.textContent = on ? 'ON' : 'OFF';
      stateText.style.color = on ? 'green' : 'red';

      // =========================
      // Toggle Handler
      // =========================
      sw.addEventListener('change', async () => {
        const previous = !sw.checked;
        sw.disabled = true;

        try {
          await fetchJSON(
            `${API_PREFIX}/devices/${deviceId}/outputs/set`,
            {
              method: 'POST',
              headers: {
                ...authHeaders(),
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                channel: channelNo,
                on: sw.checked
              })
            }
          );

        } catch (e) {
          alert(`Gagal set CH ${channelNo}: ${e.message || e}`);
          sw.checked = previous;
        } finally {
          stateText.textContent = sw.checked ? 'ON' : 'OFF';
          stateText.style.color = sw.checked ? 'green' : 'red';
          sw.disabled = false;
        }
      });

      wrap.appendChild(sw);
      wrap.appendChild(stateText);

      card.appendChild(lbl);
      card.appendChild(wrap);
      grid.appendChild(card);
    });

  } catch (e) {
    console.error(e);
    alert('Gagal load status: ' + (e.message || e));
  }
}


// =========================
// Init
// =========================
if (btnLoad) {
  btnLoad.addEventListener('click', loadStatus);
}

window.addEventListener('load', async () => {
  if (!grid) {
    console.error('Elemen grid tidak ditemukan');
    return;
  }

  await loadChannelNames();
  await loadStatus();

  // Optional realtime polling
  // setInterval(loadStatus, 5000);
});
