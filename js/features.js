// ===== FEATURES: Net Worth, Tax, Trends, Stocks, Email =====

// ══════════════════════════════════════════════════════════════════
//  NET WORTH
// ══════════════════════════════════════════════════════════════════
let networthData  = { assets: [], liabilities: [] };
let networthChart = null;

async function loadNetWorth() {
  try {
    const data = await NetWorthAPI.getAll();
    networthData.assets      = data.assets      || [];
    networthData.liabilities = data.liabilities || [];
    renderNetWorth(data);
  } catch (err) { console.warn('NetWorth load:', err.message); }
}

function renderNetWorth(data) {
  const totalA = data.total_assets      || 0;
  const totalL = data.total_liabilities || 0;
  const nw     = data.net_worth         || 0;

  document.getElementById('nw-assets').textContent      = fmt(totalA);
  document.getElementById('nw-liabilities').textContent = fmt(totalL);
  document.getElementById('nw-total').textContent       = fmt(nw);
  const status = document.getElementById('nw-status');
  status.textContent = nw >= 0 ? 'Positive Net Worth ✓' : 'Negative Net Worth ✗';
  status.style.color = nw >= 0 ? 'var(--green)' : 'var(--red)';

  document.getElementById('assets-list').innerHTML = networthData.assets.length
    ? networthData.assets.map(e =>
        '<div class="nw-entry-row">' +
          '<span class="nw-entry-name">' + e.category + '</span>' +
          '<span class="nw-entry-amt asset">' + fmt(e.amount) + '</span>' +
          '<button class="btn btn-danger" style="padding:4px 10px;font-size:12px" onclick="deleteNWEntry(' + e.id + ')">✕</button>' +
        '</div>').join('')
    : '<p class="empty-hint">No assets added yet.</p>';

  document.getElementById('liabilities-list').innerHTML = networthData.liabilities.length
    ? networthData.liabilities.map(e =>
        '<div class="nw-entry-row">' +
          '<span class="nw-entry-name">' + e.category + '</span>' +
          '<span class="nw-entry-amt liability">' + fmt(e.amount) + '</span>' +
          '<button class="btn btn-danger" style="padding:4px 10px;font-size:12px" onclick="deleteNWEntry(' + e.id + ')">✕</button>' +
        '</div>').join('')
    : '<p class="empty-hint">No liabilities added yet.</p>';

  renderNetWorthChart(totalA, totalL);
}

function renderNetWorthChart(assets, liabilities) {
  const canvas = document.getElementById('networthChart');
  if (!canvas) return;
  if (networthChart) { networthChart.destroy(); networthChart = null; }
  networthChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: ['Assets', 'Liabilities', 'Net Worth'],
      datasets: [{ data: [assets, liabilities, Math.max(assets - liabilities, 0)], backgroundColor: ['rgba(62,207,142,0.7)', 'rgba(240,99,117,0.7)', 'rgba(124,111,247,0.7)'], borderRadius: 8 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ' ' + fmt(ctx.raw) }, backgroundColor: '#1a1a28', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, titleColor: '#f0f0f5', bodyColor: '#888899', padding: 10 } },
      scales: { y: { ticks: { color: '#555566', callback: v => '₹' + (v/1000).toFixed(0) + 'k' }, grid: { color: 'rgba(255,255,255,0.04)' } }, x: { ticks: { color: '#888899' }, grid: { display: false } } }
    }
  });
}

async function addNetWorthEntry(type) {
  const nameId   = type === 'asset' ? 'asset-name'   : 'liability-name';
  const amountId = type === 'asset' ? 'asset-amount' : 'liability-amount';
  const name   = document.getElementById(nameId).value.trim();
  const amount = +document.getElementById(amountId).value || 0;
  if (!name) { alert('Please enter a name.'); return; }
  try {
    await NetWorthAPI.add({ category: name, entry_type: type, amount });
    document.getElementById(nameId).value   = '';
    document.getElementById(amountId).value = '';
    await loadNetWorth();
  } catch (err) { alert('Error: ' + err.message); }
}

async function deleteNWEntry(id) {
  try { await NetWorthAPI.delete(id); await loadNetWorth(); }
  catch (err) { alert('Error: ' + err.message); }
}

// ══════════════════════════════════════════════════════════════════
//  TAX CALCULATOR
// ══════════════════════════════════════════════════════════════════
let taxChart = null;

async function calculateTax() {
  const salary   = +document.getElementById('tax-salary').value      || 0;
  const other    = +document.getElementById('tax-other').value       || 0;
  const sec80c   = +document.getElementById('tax-80c').value         || 0;
  const sec80d   = +document.getElementById('tax-80d').value         || 0;
  const sec80dP  = +document.getElementById('tax-80d-parents').value || 0;
  const hra      = +document.getElementById('tax-hra').value         || 0;
  const homeLoan = +document.getElementById('tax-homeloan').value    || 0;
  const nps      = +document.getElementById('tax-nps').value         || 0;
  if (!salary) return;
  try {
    const data   = await TaxAPI.calculate({ gross_salary: salary, other_income: other, sec_80c: sec80c, sec_80d: sec80d, sec_80d_parents: sec80dP, hra_exemption: hra, home_loan_int: homeLoan, nps_80ccd: nps });
    const oldTax = data.old_regime.tax;
    const newTax = data.new_regime.tax;
    const winner = data.better_regime;

    document.getElementById('tax-results').innerHTML =
      '<div class="tax-comparison">' +
        '<div class="tax-regime-card ' + (winner === 'old' ? 'winner' : '') + '">' +
          '<div class="tax-regime-label">Old Regime</div>' +
          '<div class="tax-regime-amount" style="color:var(--red)">' + fmt(oldTax) + '</div>' +
          '<div class="tax-regime-sub">Effective: ' + data.old_regime.effective_rate + '%</div>' +
          (winner === 'old' ? '<div class="winner-badge">✓ Better for you</div>' : '') +
        '</div>' +
        '<div class="tax-regime-card ' + (winner === 'new' ? 'winner' : '') + '">' +
          '<div class="tax-regime-label">New Regime</div>' +
          '<div class="tax-regime-amount" style="color:var(--accent)">' + fmt(newTax) + '</div>' +
          '<div class="tax-regime-sub">Effective: ' + data.new_regime.effective_rate + '%</div>' +
          (winner === 'new' ? '<div class="winner-badge">✓ Better for you</div>' : '') +
        '</div>' +
      '</div>' +
      '<div style="text-align:center;padding:10px;background:var(--surface);border-radius:var(--radius-sm)">' +
        '<span style="font-size:13px;color:var(--text-muted)">You save </span>' +
        '<span style="font-size:18px;font-weight:700;color:var(--green)">' + fmt(data.tax_saved) + '</span>' +
        '<span style="font-size:13px;color:var(--text-muted)"> by choosing the ' + winner + ' regime</span>' +
      '</div>';

    document.getElementById('tax-tips').innerHTML = data.suggestions.length
      ? data.suggestions.map(s => '<div class="tax-saving-row"><span class="tax-saving-icon">✦</span><span>' + s + '</span></div>').join('')
      : '<p style="color:var(--green);font-size:14px">✓ You are maximizing all available deductions!</p>';

    renderTaxChart(oldTax, newTax);
  } catch (err) { console.warn('Tax calc error:', err.message); }
}

function renderTaxChart(oldTax, newTax) {
  const canvas = document.getElementById('taxChart');
  if (!canvas) return;
  if (taxChart) { taxChart.destroy(); taxChart = null; }
  taxChart = new Chart(canvas, {
    type: 'bar',
    data: { labels: ['Old Regime', 'New Regime'], datasets: [{ data: [oldTax, newTax], backgroundColor: ['rgba(240,99,117,0.7)', 'rgba(124,111,247,0.7)'], borderRadius: 8 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ' Tax: ' + fmt(ctx.raw) }, backgroundColor: '#1a1a28', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, titleColor: '#f0f0f5', bodyColor: '#888899', padding: 10 } }, scales: { y: { ticks: { color: '#555566', callback: v => '₹' + (v/1000).toFixed(0) + 'k' }, grid: { color: 'rgba(255,255,255,0.04)' } }, x: { ticks: { color: '#888899' }, grid: { display: false } } } }
  });
}

// ══════════════════════════════════════════════════════════════════
//  MONTHLY TRENDS
// ══════════════════════════════════════════════════════════════════
let trendsChart      = null;
let savingsRateChart = null;

async function loadTrends() {
  try {
    const data    = await BudgetAPI.getHistory();
    const history = (data.history || []).slice(0, 6).reverse();
    if (!history.length) return;
    const labels   = history.map(b => b.month.slice(0, 3) + ' ' + b.year);
    const incomes  = history.map(b => b.income);
    const expenses = history.map(b => b.expenses.reduce((s, e) => s + e.actual, 0));
    const savings  = incomes.map((inc, i) => inc - expenses[i]);
    const rates    = incomes.map((inc, i) => inc ? Math.round((savings[i] / inc) * 100) : 0);

    const avgIncome = Math.round(incomes.reduce((a, b) => a + b, 0) / incomes.length);
    const avgExp    = Math.round(expenses.reduce((a, b) => a + b, 0) / expenses.length);
    const avgSave   = Math.round(savings.reduce((a, b) => a + b, 0) / savings.length);
    const bestIdx   = savings.indexOf(Math.max(...savings));

    document.getElementById('trend-avg-income').textContent = fmt(avgIncome);
    document.getElementById('trend-avg-exp').textContent    = fmt(avgExp);
    document.getElementById('trend-avg-save').textContent   = fmt(avgSave);
    document.getElementById('trend-best').textContent       = labels[bestIdx] || '—';
    document.getElementById('trend-best-amt').textContent   = fmt(savings[bestIdx] || 0) + ' saved';

    renderTrendsChart(labels, incomes, expenses, savings);
    renderSavingsRateChart(labels, rates);
  } catch (err) { console.warn('Trends load:', err.message); }
}

function renderTrendsChart(labels, incomes, expenses, savings) {
  const canvas = document.getElementById('trendsChart');
  if (!canvas) return;
  if (trendsChart) { trendsChart.destroy(); trendsChart = null; }
  trendsChart = new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets: [
      { label: 'Income',   data: incomes,  backgroundColor: 'rgba(77,168,255,0.7)',  borderRadius: 4 },
      { label: 'Expenses', data: expenses, backgroundColor: 'rgba(240,99,117,0.7)', borderRadius: 4 },
      { label: 'Savings',  data: savings,  backgroundColor: 'rgba(62,207,142,0.7)', borderRadius: 4 },
    ]},
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#888899', font: { size: 12 }, boxWidth: 12 } }, tooltip: { callbacks: { label: ctx => ' ' + ctx.dataset.label + ': ' + fmt(ctx.raw) }, backgroundColor: '#1a1a28', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, titleColor: '#f0f0f5', bodyColor: '#888899', padding: 10 } }, scales: { y: { ticks: { color: '#555566', callback: v => '₹' + (v/1000).toFixed(0) + 'k' }, grid: { color: 'rgba(255,255,255,0.04)' } }, x: { ticks: { color: '#888899' }, grid: { display: false } } } }
  });
}

function renderSavingsRateChart(labels, rates) {
  const canvas = document.getElementById('savingsRateChart');
  if (!canvas) return;
  if (savingsRateChart) { savingsRateChart.destroy(); savingsRateChart = null; }
  savingsRateChart = new Chart(canvas, {
    type: 'line',
    data: { labels, datasets: [{ label: 'Savings Rate %', data: rates, borderColor: '#7c6ff7', backgroundColor: 'rgba(124,111,247,0.1)', borderWidth: 2, tension: 0.4, pointRadius: 4, fill: true }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ' Savings Rate: ' + ctx.raw + '%' }, backgroundColor: '#1a1a28', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, titleColor: '#f0f0f5', bodyColor: '#888899', padding: 10 } }, scales: { y: { ticks: { color: '#555566', callback: v => v + '%' }, grid: { color: 'rgba(255,255,255,0.04)' } }, x: { ticks: { color: '#888899' }, grid: { display: false } } } }
  });
}

// ══════════════════════════════════════════════════════════════════
//  STOCKS / MARKETS
// ══════════════════════════════════════════════════════════════════
async function loadStocks() {
  const el = document.getElementById('stocks-list');
  el.innerHTML = '<p class="empty-hint">Loading prices...</p>';
  try {
    const data = await StocksAPI.getPopular();
    window._stocksData = data.stocks;
    el.innerHTML = data.stocks.map(s => {
      const up   = s.change_pct >= 0;
      const abbr = s.symbol.slice(0, 4);
      return '<div class="stock-row">' +
        '<div class="stock-icon">' + abbr + '</div>' +
        '<div class="stock-info">' +
          '<div class="stock-name">' + s.name + '</div>' +
          '<div class="stock-symbol">' + s.symbol + ' · ' + s.type + ' · ' + (s.sector || '') + '</div>' +
        '</div>' +
        '<div style="text-align:right">' +
          '<div class="stock-price">₹' + s.price.toLocaleString('en-IN') + '</div>' +
          '<span class="stock-change ' + (up ? 'up' : 'down') + '">' + (up ? '▲' : '▼') + ' ' + Math.abs(s.change_pct) + '%</span>' +
        '</div>' +
      '</div>';
    }).join('');
  } catch (err) {
    el.innerHTML = '<p class="empty-hint">Error loading stocks: ' + err.message + '</p>';
  }

  // Also load indices
  loadIndices();
}

async function loadIndices() {
  const el = document.getElementById('indices-list');
  if (!el) return;
  try {
    const data = await apiFetch('/stocks/indices');
    el.innerHTML = data.indices.map(idx => {
      const up = idx.change_pct >= 0;
      return '<div style="background:var(--surface);border-radius:var(--radius-sm);padding:14px;text-align:center">' +
        '<div style="font-size:12px;color:var(--text-muted);margin-bottom:4px">' + idx.name + '</div>' +
        '<div style="font-size:20px;font-weight:700;font-family:var(--font2)">' + idx.price.toLocaleString('en-IN') + '</div>' +
        '<div class="stock-change ' + (up ? 'up' : 'down') + '" style="margin-top:4px;display:inline-block">' + (up ? '▲' : '▼') + ' ' + Math.abs(idx.change_pct) + '%</div>' +
      '</div>';
    }).join('');
  } catch (err) {
    if (el) el.innerHTML = '<p class="empty-hint">Could not load indices</p>';
  }
}

async function searchStock() {
  const input  = document.getElementById('stock-search');
  const symbol = input.value.trim();
  if (!symbol) { alert('Please enter a stock name or symbol'); return; }
  const el = document.getElementById('search-result');
  el.innerHTML = '<p style="color:var(--text-muted);font-size:14px">Searching for ' + symbol + '...</p>';
  try {
    const s  = await StocksAPI.search(symbol);
    const up = s.change_pct >= 0;
    el.innerHTML =
      '<div style="background:var(--surface);border-radius:var(--radius);padding:1.25rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap">' +
        '<div>' +
          '<div style="font-size:18px;font-weight:600">' + s.name + '</div>' +
          '<div style="font-size:13px;color:var(--text-muted);margin-top:2px">' + s.symbol + ' · ' + s.type + (s.note ? ' · ' + s.note : '') + '</div>' +
        '</div>' +
        '<div style="text-align:right">' +
          '<div style="font-size:28px;font-weight:700;font-family:var(--font2)">₹' + s.price.toLocaleString('en-IN') + '</div>' +
          '<span class="stock-change ' + (up ? 'up' : 'down') + '">' + (up ? '▲' : '▼') + ' ' + Math.abs(s.change_pct) + '% today</span>' +
        '</div>' +
      '</div>';
  } catch (err) {
    el.innerHTML = '<p style="color:var(--red);font-size:14px">Error: ' + err.message + '</p>';
  }
}

async function loadSIPFunds() {
  const el = document.getElementById('sip-funds-list');
  if (!el) return;
  el.innerHTML = '<p class="empty-hint">Loading funds...</p>';
  try {
    const data = await StocksAPI.getSIPFunds();
    el.innerHTML = data.funds.map(f =>
      '<div class="sip-fund-card">' +
        '<div style="flex:1">' +
          '<div class="sip-fund-name">' + f.name + ' <span style="color:var(--amber)">' + f.rating + '</span></div>' +
          '<div class="sip-fund-meta">' + f.category + ' · AUM: ' + (f.aum || '—') + ' · Min SIP: ' + f.min_sip + '</div>' +
          '<div class="sip-fund-meta" style="margin-top:4px">Risk: <span style="color:' + (f.risk === 'High' ? 'var(--red)' : f.risk === 'Low' ? 'var(--green)' : 'var(--amber)') + '">' + f.risk + '</span></div>' +
        '</div>' +
        '<div style="text-align:right;flex-shrink:0">' +
          '<div class="sip-fund-return">' + f.returns_3y + '</div>' +
          '<div style="font-size:11px;color:var(--text-muted)">3Y returns</div>' +
          '<div style="font-size:11px;color:var(--text-muted);margin-top:2px">1Y: ' + (f.returns_1y || '—') + ' · 5Y: ' + (f.returns_5y || '—') + '</div>' +
        '</div>' +
      '</div>'
    ).join('');
  } catch (err) {
    el.innerHTML = '<p class="empty-hint">Error: ' + err.message + '</p>';
  }
}

// ══════════════════════════════════════════════════════════════════
//  EMAIL
// ══════════════════════════════════════════════════════════════════
async function sendEmailReport() {
  const month  = document.getElementById('month') ? document.getElementById('month').value : new Date().toLocaleString('en', { month: 'long' });
  const year   = new Date().getFullYear();
  const status = document.getElementById('email-status');
  status.innerHTML = '<span style="color:var(--text-muted)">Sending report...</span>';
  try {
    const data = await EmailAPI.sendReport(month, year);
    status.innerHTML = '<span style="color:var(--green)">✓ ' + data.message + '</span>';
  } catch (err) { status.innerHTML = '<span style="color:var(--red)">✗ ' + err.message + '</span>'; }
}

async function sendTestEmail() {
  const status = document.getElementById('email-status');
  status.innerHTML = '<span style="color:var(--text-muted)">Sending test email...</span>';
  try {
    const data = await EmailAPI.sendTest();
    status.innerHTML = '<span style="color:var(--green)">✓ ' + data.message + '</span>';
  } catch (err) { status.innerHTML = '<span style="color:var(--red)">✗ ' + err.message + '</span>'; }
}

// ══════════════════════════════════════════════════════════════════
//  PDF DOWNLOAD
// ══════════════════════════════════════════════════════════════════
async function downloadPDF() {
  const month = document.getElementById('month') ? document.getElementById('month').value : new Date().toLocaleString('en', { month: 'long' });
  const year  = new Date().getFullYear();
  const token = getToken();
  const url   = 'http://127.0.0.1:5000/api/pdf/report?month=' + month + '&year=' + year;
  try {
    const response = await fetch(url, { headers: { 'Authorization': 'Bearer ' + token } });
    if (!response.ok) throw new Error('Failed to generate PDF');
    const blob = await response.blob();
    const link = document.createElement('a');
    link.href  = URL.createObjectURL(blob);
    link.download = 'FinTech_Report_' + month + '_' + year + '.pdf';
    link.click();
    URL.revokeObjectURL(link.href);
  } catch (err) { alert('PDF download failed: ' + err.message); }
}


// ══════════════════════════════════════════════════════════════════
//  PORTFOLIO TRACKER (localStorage based)
// ══════════════════════════════════════════════════════════════════
function getPortfolio() {
  try { return JSON.parse(localStorage.getItem('fintech_portfolio') || '[]'); } catch { return []; }
}

function savePortfolio(p) {
  localStorage.setItem('fintech_portfolio', JSON.stringify(p));
}

function addToPortfolio() {
  const symbol = document.getElementById('port-symbol').value.trim();
  const qty    = +document.getElementById('port-qty').value    || 0;
  const buy    = +document.getElementById('port-buy').value    || 0;
  const type   = document.getElementById('port-type').value;

  if (!symbol) { alert('Please enter a stock name or symbol'); return; }
  if (!qty)    { alert('Please enter quantity'); return; }
  if (!buy)    { alert('Please enter buy price'); return; }

  const portfolio = getPortfolio();

  // Check if already exists — update quantity
  const existing = portfolio.find(p => p.symbol.toUpperCase() === symbol.toUpperCase());
  if (existing) {
    const totalInvested = existing.qty * existing.buy + qty * buy;
    const totalQty      = existing.qty + qty;
    existing.buy = Math.round(totalInvested / totalQty);
    existing.qty = totalQty;
  } else {
    portfolio.push({ symbol: symbol.toUpperCase(), qty, buy, type, added: new Date().toLocaleDateString('en-IN') });
  }

  savePortfolio(portfolio);
  document.getElementById('port-symbol').value = '';
  document.getElementById('port-qty').value    = '';
  document.getElementById('port-buy').value    = '';
  renderPortfolio();
}

function removeFromPortfolio(index) {
  const portfolio = getPortfolio();
  portfolio.splice(index, 1);
  savePortfolio(portfolio);
  renderPortfolio();
}

function renderPortfolio() {
  const portfolio = getPortfolio();
  const listEl    = document.getElementById('portfolio-list');
  const summaryEl = document.getElementById('portfolio-summary');
  if (!listEl) return;

  if (!portfolio.length) {
    listEl.innerHTML    = '<p class="empty-hint">No holdings yet. Add your first stock above!</p>';
    summaryEl.innerHTML = '';
    return;
  }

  // Get current prices from popular stocks data
  let totalInvested = 0;
  let totalCurrent  = 0;

  listEl.innerHTML = portfolio.map((p, i) => {
    // Find matching stock for current price
    const match = window._stocksData ? window._stocksData.find(s =>
      s.symbol.toUpperCase() === p.symbol.toUpperCase() ||
      s.name.toUpperCase().includes(p.symbol.toUpperCase())
    ) : null;

    const currentPrice = match ? match.price : p.buy;
    const invested     = p.qty * p.buy;
    const current      = p.qty * currentPrice;
    const gain         = current - invested;
    const gainPct      = ((gain / invested) * 100).toFixed(2);
    const isGain       = gain >= 0;

    totalInvested += invested;
    totalCurrent  += current;

    return '<div class="stock-row">' +
      '<div class="stock-icon" style="font-size:10px">' + p.symbol.slice(0,4) + '</div>' +
      '<div class="stock-info">' +
        '<div class="stock-name">' + p.symbol + ' <span style="font-size:11px;color:var(--text-muted)">(' + p.type + ')</span></div>' +
        '<div class="stock-symbol">Qty: ' + p.qty + ' · Avg Buy: ₹' + p.buy.toLocaleString('en-IN') + ' · Added: ' + p.added + '</div>' +
      '</div>' +
      '<div style="text-align:right;margin-right:10px">' +
        '<div style="font-size:14px;font-weight:600">₹' + current.toLocaleString('en-IN', {maximumFractionDigits:0}) + '</div>' +
        '<span class="stock-change ' + (isGain ? 'up' : 'down') + '">' + (isGain ? '+' : '') + gain.toLocaleFixed(0) + ' (' + gainPct + '%)</span>' +
      '</div>' +
      '<button class="btn btn-danger" style="padding:5px 10px;font-size:12px;flex-shrink:0" onclick="removeFromPortfolio(' + i + ')">✕</button>' +
    '</div>';
  }).join('');

  // Summary
  const totalGain    = totalCurrent - totalInvested;
  const totalGainPct = totalInvested ? ((totalGain / totalInvested) * 100).toFixed(2) : 0;
  const isGain       = totalGain >= 0;

  summaryEl.innerHTML =
    '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:1rem">' +
      '<div class="metric-card accent-blue" style="margin:0">' +
        '<div class="metric-label">Total Invested</div>' +
        '<div class="metric-value" style="font-size:20px">₹' + totalInvested.toLocaleString('en-IN', {maximumFractionDigits:0}) + '</div>' +
      '</div>' +
      '<div class="metric-card accent-green" style="margin:0">' +
        '<div class="metric-label">Current Value</div>' +
        '<div class="metric-value" style="font-size:20px">₹' + totalCurrent.toLocaleString('en-IN', {maximumFractionDigits:0}) + '</div>' +
      '</div>' +
      '<div class="metric-card ' + (isGain ? 'accent-green' : 'accent-red') + '" style="margin:0">' +
        '<div class="metric-label">Total Gain/Loss</div>' +
        '<div class="metric-value" style="font-size:20px;color:' + (isGain ? 'var(--green)' : 'var(--red)') + '">' +
          (isGain ? '+' : '') + '₹' + Math.abs(totalGain).toLocaleString('en-IN', {maximumFractionDigits:0}) + '</div>' +
        '<div class="metric-foot">' + totalGainPct + '%</div>' +
      '</div>' +
    '</div>';
}

// Fix toLocaleFixed for numbers
Number.prototype.toLocaleFixed = function(digits) {
  return this.toLocaleString('en-IN', {maximumFractionDigits: digits || 0, minimumFractionDigits: digits || 0});
};

// Load portfolio when stocks tab opens
const _origLoadStocks = loadStocks;
loadStocks = async function() {
  await _origLoadStocks();
  renderPortfolio();
};