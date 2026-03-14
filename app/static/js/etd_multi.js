// app/static/js/etd_multi.js
console.log('[multi] script loaded');

const channelNames = {};
const deviceSelect = document.getElementById('deviceSelect');
const grid = document.getElementById('grid');
const btnLoad = document.getElementById('btnLoad');

function authHeaders() {
  const t = localStorage.getItem('access_token');
  return t ? { 'Authorization': 'Bearer ' + t } : {};
}

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (res.status === 401) { window.location.href = '/login'; return; }
  if (!res.ok) { throw new Error(await res.text() || `HTTP ${res.status}`); }
  return res.json();
}

async function loadDevices() {
  const arr = await fetchJSON(`/devices/`, { headers: { ...authHeaders() } });
  deviceSelect.innerHTML = '';
  arr.filter(d => d.enabled).forEach(d => {
    const opt = document.createElement('option');
    opt.value = d.id; opt.textContent = `${d.name} (${d.ip}:${d.port})`;
    deviceSelect.appendChild(opt);
  });
}

async function loadChannelNames(deviceId) {
  const arr = await fetchJSON(`/devices/${deviceId}/channels`, { headers: { ...authHeaders() } });
  Object.keys(channelNames).forEach(k => delete channelNames[k]);
  (arr || []).forEach(ch => channelNames[ch.index] = ch.name);
}

function renderCard(n, on, deviceId) {
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
  lbl.style.fontWeight = '600';
  lbl.style.marginBottom = '6px';

  const wrap = document.createElement('label');
  wrap.style.display = 'flex';
  wrap.style.alignItems = 'center';
  wrap.style.gap = '8px';
  wrap.style.cursor = 'pointer';

  const sw = document.createElement('input');
  sw.type = 'checkbox';
  sw.checked = !!on;

  const stateText = document.createElement('span');
  stateText.textContent = sw.checked ? 'ON' : 'OFF';
  stateText.style.color = sw.checked ? 'green' : 'red';

  sw.addEventListener('change', async () => {
    const original = !sw.checked;
    sw.disabled = true;
    stateText.textContent = sw.checked ? 'ON' : 'OFF';
    stateText.style.color = sw.checked ? 'green' : 'red';
    try {
      await fetchJSON(`/devices/${deviceId}/outputs/set`, {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel: n, on: sw.checked })
      });
    } catch (e) {
      alert(`Gagal set CH ${n}: ${e.message || e}`);
      sw.checked = original;
      stateText.textContent = original ? 'ON' : 'OFF';
      stateText.style.color = original ? 'green' : 'red';
    } finally {
      sw.disabled = false;
    }
  });

  wrap.appendChild(sw);
  wrap.appendChild(stateText);
  card.appendChild(lbl);
  card.appendChild(wrap);
  return card;
}

async function loadStatus(deviceId) {
  grid.innerHTML = '';
  try {
    const arr = await fetchJSON(`/devices/${deviceId}/outputs`, { headers: { ...authHeaders() } });
    if (!Array.isArray(arr)) throw new Error('Format outputs tidak sesuai');
    arr.forEach((on, idx) => {
      const n = idx + 1;
      grid.appendChild(renderCard(n, on, deviceId));
    });
  } catch (e) {
    console.error(e);
    alert('Gagal load status: ' + (e.message || e));
    // Render placeholder supaya UI tetap terlihat
    for (let i = 1; i <= 12; i++) grid.appendChild(renderCard(i, false, deviceId));
  }
}

btnLoad.addEventListener('click', async () => {
  const deviceId = deviceSelect.value;
  await loadChannelNames(deviceId);
  await loadStatus(deviceId);
});

deviceSelect.addEventListener('change', async () => {
  const deviceId = deviceSelect.value;
  await loadChannelNames(deviceId);
  await loadStatus(deviceId);
});

window.addEventListener('load', async () => {
  if (!grid || !btnLoad || !deviceSelect) {
    console.error('Elemen grid/btnLoad/deviceSelect tidak ditemukan');
    return;
  }
  await loadDevices();
  if (deviceSelect.options.length > 0) {
    const id = deviceSelect.value;
    await loadChannelNames(id);
    await loadStatus(id);
  }
});
``
