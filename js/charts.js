// ===== CHARTS =====
let donutChart = null;
let projChart  = null;
let sipChart   = null;

function renderDonutChart() {
  const cats = state.categories.filter(c => c.actual > 0);
  const canvas = document.getElementById('donutChart');
  if (!canvas) return;

  if (donutChart) { donutChart.destroy(); donutChart = null; }

  const totalExp = getTotalExpenses();
  document.getElementById('donut-total').textContent = fmt(totalExp);

  const labels = cats.map(c => c.name);
  const data   = cats.map(c => c.actual);
  const colors = CHART_COLORS.slice(0, cats.length);

  // Legend
  const legendEl = document.getElementById('donut-legend');
  legendEl.innerHTML = labels.map((l, i) =>
    `<span class="legend-item">
      <span class="legend-dot" style="background:${colors[i]}"></span>
      ${l.split('/')[0].trim()}
    </span>`
  ).join('');

  if (!cats.length) return;

  donutChart = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderWidth: 0,
        hoverOffset: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${fmt(ctx.raw)}  (${pct(ctx.raw, totalExp)}%)`
          },
          backgroundColor: '#1a1a28',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          titleColor: '#f0f0f5',
          bodyColor: '#888899',
          padding: 10,
        }
      }
    }
  });
}

function renderBudgetBars() {
  const el = document.getElementById('budget-bars');
  const cats = state.categories.filter(c => c.budget > 0 || c.actual > 0).slice(0, 8);
  if (!cats.length) {
    el.innerHTML = '<p class="empty-hint">Set budgets in the Budget tab.</p>';
    return;
  }
  el.innerHTML = cats.map(c => {
    const p = c.budget ? Math.min(pct(c.actual, c.budget), 100) : 0;
    const over = c.budget && c.actual > c.budget;
    const color = over ? '#f06375' : (p > 75 ? '#f5a623' : '#7c6ff7');
    return `
      <div class="budget-bar-item">
        <div class="budget-bar-labels">
          <span class="budget-bar-name">${c.name.split('/')[0].trim()}</span>
          <span class="budget-bar-amt">${fmt(c.actual)}${c.budget ? ' / ' + fmt(c.budget) : ''}</span>
        </div>
        <div class="budget-bar-track">
          <div class="budget-bar-fill" style="width:${p}%;background:${color}"></div>
        </div>
      </div>`;
  }).join('');
}

function renderProjectionChart() {
  const canvas = document.getElementById('projChart');
  if (!canvas) return;
  if (projChart) { projChart.destroy(); projChart = null; }

  const savings = getSavings();
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const base = state.goals.reduce((s, g) => s + (g.saved || 0), 0);
  const bullish  = months.map((_, i) => Math.round(base + savings * (i + 1) * 1.05));
  const moderate = months.map((_, i) => Math.round(base + savings * (i + 1)));
  const careful  = months.map((_, i) => Math.round(base + savings * (i + 1) * 0.9));

  projChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: months,
      datasets: [
        {
          label: 'Optimistic',
          data: bullish,
          borderColor: '#3ecf8e',
          backgroundColor: 'rgba(62,207,142,0.06)',
          borderWidth: 2, tension: 0.4, pointRadius: 2, fill: true,
        },
        {
          label: 'Moderate',
          data: moderate,
          borderColor: '#7c6ff7',
          backgroundColor: 'rgba(124,111,247,0.08)',
          borderWidth: 2, tension: 0.4, pointRadius: 2, fill: true,
        },
        {
          label: 'Conservative',
          data: careful,
          borderColor: '#f5a623',
          backgroundColor: 'rgba(245,166,35,0.05)',
          borderWidth: 2, tension: 0.4, pointRadius: 2, fill: true,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#888899', font: { size: 12 }, boxWidth: 12, padding: 16 }
        },
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.dataset.label}: ${fmt(ctx.raw)}` },
          backgroundColor: '#1a1a28',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          titleColor: '#f0f0f5',
          bodyColor: '#888899',
          padding: 10,
        }
      },
      scales: {
        y: {
          ticks: { color: '#555566', callback: v => '₹' + (v/1000).toFixed(0) + 'k' },
          grid: { color: 'rgba(255,255,255,0.04)' },
        },
        x: {
          ticks: { color: '#555566' },
          grid: { display: false },
        }
      }
    }
  });
}

function calcSIP() {
  const P = +document.getElementById('sip-amount').value || 0;
  const r = (+document.getElementById('sip-rate').value || 12) / 100 / 12;
  const n = (+document.getElementById('sip-years').value || 10) * 12;

  const fv = P * ((Math.pow(1 + r, n) - 1) / r) * (1 + r);
  const invested = P * n;
  const gains = fv - invested;

  document.getElementById('sip-results').innerHTML = `
    <div class="sip-result-item">
      <div class="sip-result-label">Amount Invested</div>
      <div class="sip-result-value">${fmt(invested)}</div>
    </div>
    <div class="sip-result-item">
      <div class="sip-result-label">Estimated Gains</div>
      <div class="sip-result-value" style="color:var(--green)">${fmt(gains)}</div>
    </div>
    <div class="sip-result-item">
      <div class="sip-result-label">Total Value</div>
      <div class="sip-result-value" style="color:var(--accent)">${fmt(fv)}</div>
    </div>`;

  renderSIPChart(invested, gains, n);
}

function renderSIPChart(invested, gains, months) {
  const canvas = document.getElementById('sipChart');
  if (!canvas) return;
  if (sipChart) { sipChart.destroy(); sipChart = null; }

  const P = +document.getElementById('sip-amount').value || 0;
  const r = (+document.getElementById('sip-rate').value || 12) / 100 / 12;
  const step = Math.ceil(months / 12);
  const labels = [], invData = [], fvData = [];

  for (let i = step; i <= months; i += step) {
    labels.push(Math.round(i / 12) + 'y');
    const inv = P * i;
    const fv  = P * ((Math.pow(1 + r, i) - 1) / r) * (1 + r);
    invData.push(Math.round(inv));
    fvData.push(Math.round(fv));
  }

  sipChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Invested', data: invData, backgroundColor: 'rgba(77,168,255,0.5)', borderRadius: 4 },
        { label: 'Portfolio Value', data: fvData, backgroundColor: 'rgba(124,111,247,0.7)', borderRadius: 4 },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#888899', font: { size: 12 }, boxWidth: 12 } },
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.dataset.label}: ${fmt(ctx.raw)}` },
          backgroundColor: '#1a1a28',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          titleColor: '#f0f0f5',
          bodyColor: '#888899',
          padding: 10,
        }
      },
      scales: {
        y: {
          ticks: { color: '#555566', callback: v => '₹' + (v >= 1e6 ? (v/1e5).toFixed(1) + 'L' : (v/1000).toFixed(0) + 'k') },
          grid: { color: 'rgba(255,255,255,0.04)' },
        },
        x: { ticks: { color: '#555566' }, grid: { display: false } }
      }
    }
  });
}
