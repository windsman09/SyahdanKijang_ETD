const channelNames = {};
const grid = document.getElementById('grid');
const btnLoad = document.getElementById('btnLoad');

function authHeader() {
  const token = localStorage.getItem('access_token');
  return token ? { 'Authorization': 'Bearer ' + token } : {};
}

async function loadChannelNames() {
  const res = await fetch('/etd8a12/channels');

  if (!res.ok) throw await res.text();

  const arr = await res.json();
  arr.forEach(ch => {
    channelNames[ch.index] = ch.name;
  });
}

async function loadStatus() {
  grid.innerHTML = '';

  try {
    const res = await fetch('/etd8a12/outputs', {
      headers: authHeader()
    });

    if (!res.ok) throw await res.text();

    const arr = await res.json();

    arr.forEach((on, idx) => {
      const n = idx + 1;

      const card = document.createElement('div');
      card.className = 'ch-card';

      const lbl = document.createElement('div');
      lbl.textContent = channelNames[n] ?? ('CH ' + n);

      const sw = document.createElement('input');
      sw.type = 'checkbox';
      sw.checked = !!on;

      card.appendChild(lbl);
      card.appendChild(sw);
      grid.appendChild(card);
    });

  } catch (e) {
    alert('Gagal load status: ' + e);
  }
}

btnLoad.addEventListener('click', loadStatus);

window.addEventListener('load', async () => {
  await loadChannelNames();
  await loadStatus();
});
