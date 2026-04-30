// Fetch and render JSON content for the Copper Kettle demo
// No build step — pages read from content/ JSON files directly

async function fetchJSON(filename) {
  try {
    const res = await fetch('./content/' + filename);
    if (!res.ok) throw new Error('Not found');
    return await res.json();
  } catch (e) {
    console.error('Failed to load', filename, e);
    return null;
  }
}

function formatPrice(price) {
  return '$' + parseFloat(price).toFixed(2);
}

function renderMenu(data) {
  const el = document.getElementById('menu-content');
  if (!el) return;
  if (!data || !data.categories) {
    el.innerHTML = '<p>Menu unavailable.</p>';
    return;
  }
  let html = '';
  for (const cat of data.categories) {
    html += `<div class="menu-category"><h2>${cat.name}</h2>`;
    for (const item of cat.items) {
      html += `<div class="menu-item">
        <div>
          <div class="menu-item-name">${item.name}</div>
          ${item.description ? `<div class="menu-item-desc">${item.description}</div>` : ''}
        </div>
        <div class="menu-item-price">${formatPrice(item.price)}</div>
      </div>`;
    }
    html += '</div>';
  }
  el.innerHTML = html;
}

function renderSpecials(data) {
  const el = document.getElementById('specials-content');
  if (!el) return;
  if (!data || !data.specials) {
    el.innerHTML = '<p>No specials available.</p>';
    return;
  }
  let html = '';
  for (const s of data.specials) {
    html += `<div class="special-card">
      <h2>${s.name}</h2>
      <div class="price">${formatPrice(s.price)}</div>
      <div class="description">${s.description}</div>
    </div>`;
  }
  el.innerHTML = html;
}

function renderHours(data) {
  const el = document.getElementById('hours-content');
  if (!el) return;
  if (!data || !data.regular) {
    el.innerHTML = '<p>Hours unavailable.</p>';
    return;
  }

  // Format a time range like "11:00 AM – 9:00 PM"
  function fmt(hm) {
    if (!hm) return '';
    const [h, m] = hm.split(':').map(Number);
    const ampm = h >= 12 ? 'PM' : 'AM';
    const hr = h > 12 ? h - 12 : h === 0 ? 12 : h;
    return `${hr}:${m.toString().padStart(2,'0')} ${ampm}`;
  }

  const days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday'];
  let html = '<h2>Regular Hours</h2>';
  for (const day of days) {
    const hours = data.regular[day];
    if (!hours || hours.closed) {
      html += `<div class="day-row"><span class="day-name">${day.charAt(0).toUpperCase() + day.slice(1)}</span><span class="closed">Closed</span></div>`;
    } else {
      html += `<div class="day-row"><span class="day-name">${day.charAt(0).toUpperCase() + day.slice(1)}</span><span>${fmt(hours.open)} – ${fmt(hours.close)}</span></div>`;
    }
  }

  if (data.holidays && data.holidays.length > 0) {
    html += '<h2 style="margin-top:2rem;">Holiday Hours</h2>';
    for (const h of data.holidays) {
      html += `<div class="day-row"><span class="day-name">${h.date}</span><span>${h.notes}</span></div>`;
    }
  }

  el.innerHTML = html;
}

function renderHoursShort(data, targetId) {
  // Just show today's or a quick summary on homepage
  const el = document.getElementById(targetId);
  if (!el) return;
  if (!data || !data.regular) return;
  // Show Mon-Fri open hours as a quick line
  const hours = data.regular;
  const summary = `Mon–Fri: ${fmt(hours.monday.open)}–${fmt(hours.monday.close)}`;
  el.textContent = summary;
}

function fmt(hm) {
  if (!hm) return '';
  const [h, m] = hm.split(':').map(Number);
  const ampm = h >= 12 ? 'PM' : 'AM';
  const hr = h > 12 ? h - 12 : h === 0 ? 12 : h;
  return `${hr}:${m.toString().padStart(2,'0')} ${ampm}`;
}

async function loadMenu() {
  const data = await fetchJSON('menu.json');
  renderMenu(data);
}

async function loadSpecials() {
  const data = await fetchJSON('specials.json');
  renderSpecials(data);
}

async function loadHoursFull() {
  const data = await fetchJSON('hours.json');
  renderHours(data);
}

async function loadHours(targetId) {
  const data = await fetchJSON('hours.json');
  renderHoursShort(data, targetId);
}
