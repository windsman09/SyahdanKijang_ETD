<<<<<<< HEAD

// app/static/js/etd8a12.js

const API_PREFIX = '/etd8a12';
const channelNames = {};

=======
const channelNames = {};
>>>>>>> 3b7d1d5b9b7584757ceebdec74023182ad093cab
const grid = document.getElementById('grid');
const btnLoad = document.getElementById('btnLoad');

function authHeaders() {
  const token = localStorage.getItem('access_token');
  return token ? { 'Authorization': 'Bearer ' + token } : {};
<<<<<<< HEAD
}

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (res.status === 401) {
    // token invalid/expired → kembali ke login
    window.location.href = '/login';
    return;
  }
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

async function loadChannelNames() {
  try {
    const arr = await fetchJSON(`${API_PREFIX}/channels`, {
      headers: { ...authHeaders() }
    });
    (arr || []).forEach(ch => {
      // ch = { index, name }
      channelNames[ch.index] = ch.name;
    });
  } catch (e) {
    console.warn('Gagal load channel names:', e.message || e);
    // tidak fatal; boleh lanjut tanpa nama
  }
=======
}

async function loadChannelNames() {
  const res = await fetch('/etd8a12/channels');

  if (!res.ok) throw await res.text();

  const arr = await res.json();
  arr.forEach(ch => {
    channelNames[ch.index] = ch.name;
  });
>>>>>>> 3b7d1d5b9b7584757ceebdec74023182ad093cab
}

async function loadStatus() {
  grid.innerHTML = '';

  try {
    const arr = await fetchJSON(`${API_PREFIX}/outputs`, {
      headers: { ...authHeaders() }
    });
<<<<<<< HEAD
    if (!Array.isArray(arr)) throw new Error('Format outputs tidak sesuai');
=======

    if (!res.ok) throw await res.text();

    const arr = await res.json();
>>>>>>> 3b7d1d5b9b7584757ceebdec74023182ad093cab

    arr.forEach((on, idx) => {
      const n = idx + 1;

      const card = document.createElement('div');
      card.className = 'ch-card';
      card.style.border = '1px solid #ccc';
      card.style.padding = '12px';
      card.style.margin = '6px';
      card.style.borderRadius = '8px';
      card.style.minWidth = '140px';
      card.style.display = 'inline-block';

      const lbl = document.createElement('div');
      lbl.textContent = channelNames[n] ?? ('CH ' + n);
<<<<<<< HEAD
      lbl.style.fontWeight = '600';
      lbl.style.marginBottom = '6px';

      const wrap = document.createElement('label');
      wrap.style.display = 'flex';
      wrap.style.alignItems = 'center';
      wrap.style.gap = '8px';
      wrap.style.cursor = 'pointer';
=======
>>>>>>> 3b7d1d5b9b7584757ceebdec74023182ad093cab

      const sw = document.createElement('input');
      sw.type = 'checkbox';
      sw.checked = !!on;

<<<<<<< HEAD
      const stateText = document.createElement('span');
      stateText.textContent = on ? 'ON' : 'OFF';
      stateText.style.color = on ? 'green' : 'red';

      sw.addEventListener('change', async () => {
        const original = !sw.checked; // nilai sebelumnya
        sw.disabled = true;
        stateText.textContent = sw.checked ? 'ON' : 'OFF';
        stateText.style.color = sw.checked ? 'green' : 'red';

        try {
          await fetchJSON(`${API_PREFIX}/outputs/set`, {
            method: 'POST',
            headers: { 
              ...authHeaders(),
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ channel: n, on: sw.checked })
          });
          // (opsional) muat ulang status untuk sinkronisasi penuh:
          // await loadStatus();
        } catch (e) {
          alert(`Gagal set CH ${n}: ${e.message || e}`);
          // revert UI
          sw.checked = original;
          stateText.textContent = original ? 'ON' : 'OFF';
          stateText.style.color = original ? 'green' : 'red';
        } finally {
          sw.disabled = false;
        }
      });

      wrap.appendChild(sw);
      wrap.appendChild(stateText);

=======
>>>>>>> 3b7d1d5b9b7584757ceebdec74023182ad093cab
      card.appendChild(lbl);
      card.appendChild(wrap);
      grid.appendChild(card);
    });

  } catch (e) {
    console.error(e);
    alert('Gagal load status: ' + (e.message || e));
  }
}

btnLoad.addEventListener('click', loadStatus);

window.addEventListener('load', async () => {
  // pastikan elemen ada
  if (!grid || !btnLoad) {
    console.error('Elemen grid atau btnLoad tidak ditemukan di DOM');
    return;
  }
  await loadChannelNames();
  await loadStatus();

  // (opsional) auto refresh berkala:
  // setInterval(loadStatus, 5000);
});
