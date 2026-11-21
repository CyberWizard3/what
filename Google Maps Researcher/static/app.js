const map = L.map('map').setView([51.83, 107.62], 13);

const GOOGLE_SUBS = ['mt0', 'mt1', 'mt2', 'mt3'];

function googleLayer(lyrs) {
  return L.tileLayer(
    `https://{s}.google.com/vt/lyrs=${lyrs}&x={x}&y={y}&z={z}`,
    { subdomains: GOOGLE_SUBS, maxZoom: 20, attribution: '© Google' }
  );
}

googleLayer('s').addTo(map);

const baseLayers = {
  'Google Satellite': googleLayer('s'),
  'Google Terrain':   googleLayer('p'),
  'Google Hybrid':    googleLayer('y'),
};
L.control.layers(baseLayers).addTo(map);

let bboxRect = null;
const overlays = {};

function readForm() {
  const g = id => document.getElementById(id).value;
  return {
    lon_min: +g('lon_min'), lat_min: +g('lat_min'),
    lon_max: +g('lon_max'), lat_max: +g('lat_max'),
    zoom:    +g('zoom'),
    include_roads: document.getElementById('include_roads')?.checked || false,
  };
}

function clearLayers() {
  for (const k in overlays) { map.removeLayer(overlays[k]); delete overlays[k]; }
  document.getElementById('layers').innerHTML = '';
}

function addTileLayer(name, url, bounds) {
  const busted = url + (url.includes('?') ? '&' : '?') + 't=' + Date.now();
  const layer = L.imageOverlay(busted, bounds, { opacity: 0.75 });
  overlays[name] = layer;
  const lbl = document.createElement('label');
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.addEventListener('change', () => {
    if (cb.checked) layer.addTo(map); else map.removeLayer(layer);
  });
  lbl.appendChild(cb);
  lbl.appendChild(document.createTextNode(name));
  document.getElementById('layers').appendChild(lbl);
}

document.getElementById('go').addEventListener('click', async () => {
  const q = readForm();
  const btn = document.getElementById('go');
  const status = document.getElementById('status');
  btn.disabled = true;
  status.textContent = 'Загрузка тайлов Google и анализ...';

  try {
    const r = await fetch('/api/analyze?' + new URLSearchParams(q));
    if (!r.ok) throw new Error('HTTP ' + r.status + ': ' + (await r.text()));
    const data = await r.json();

    if (bboxRect) map.removeLayer(bboxRect);
    bboxRect = L.rectangle(
      [[q.lat_min, q.lon_min], [q.lat_max, q.lon_max]],
      { color: '#f55', weight: 2, fill: false }
    ).addTo(map);
    map.fitBounds(bboxRect.getBounds());

    clearLayers();
    const bounds = [[q.lat_min, q.lon_min], [q.lat_max, q.lon_max]];
    for (const [name, url] of Object.entries(data.tiles)) {
      addTileLayer(name, url, bounds);
    }

    document.getElementById('report').textContent = JSON.stringify(data, null, 2);
    status.textContent = `Готово за ${data.elapsed_s} c.`;
  } catch (e) {
    status.textContent = 'Ошибка: ' + e.message;
  } finally {
    btn.disabled = false;
  }
});