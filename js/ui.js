// ===== UI RENDERING =====

function updateAll() {
  readBudgetInputs();
  updateMetrics();
  renderDonutChart();
  renderBudgetBars();
  renderInsights();
  renderProjectionChart();
  updateAISummary();
  saveState();
}

function readBudgetInputs() {
  state.income = +document.getElementById('income').value || 0;
  state.city   = document.getElementById('city').value;
  state.month  = document.getElementById('month').value;
}

function updateMetrics() {
  const totalExp = getTotalExpenses();
  const savings  = getSavings();
  const rate     = getSavingsRate();
  const score    = getHealthScore();

  document.getElementById('m-income').textContent   = fmt(state.income);
  document.getElementById('m-expenses').textContent = fmt(totalExp);
  document.getElementById('m-savings').textContent  = fmt(savings);
  document.getElementById('m-rate').textContent     = rate + '%';

  document.getElementById('m-exp-pct').textContent =
    state.income ? pct(totalExp, state.income) + '% of income' : 'Enter income';

  const saveStatus = document.getElementById('m-save-status');
  saveStatus.textContent = savings > 0 ? 'Surplus ✓' : savings < 0 ? 'Deficit ✗' : 'Enter data';
  saveStatus.style.color = savings > 0 ? 'var(--green)' : savings < 0 ? 'var(--red)' : '';

  const rateStatus = document.getElementById('m-rate-status');
  if (rate >= 30) { rateStatus.textContent = 'Excellent! 🎉'; rateStatus.style.color = 'var(--green)'; }
  else if (rate >= 20) { rateStatus.textContent = 'Great job! ✓'; rateStatus.style.color = 'var(--green)'; }
  else if (rate >= 10) { rateStatus.textContent = 'Can improve'; rateStatus.style.color = 'var(--amber)'; }
  else { rateStatus.textContent = 'Needs attention'; rateStatus.style.color = 'var(--red)'; }

  const badge = document.getElementById('health-badge');
  badge.textContent = score + ' / 100 Health Score';
  badge.style.background = score >= 70 ? 'rgba(62,207,142,0.15)' : score >= 40 ? 'rgba(245,166,35,0.15)' : 'rgba(240,99,117,0.15)';
  badge.style.borderColor = score >= 70 ? 'rgba(62,207,142,0.3)' : score >= 40 ? 'rgba(245,166,35,0.3)' : 'rgba(240,99,117,0.3)';
  badge.style.color = score >= 70 ? 'var(--green)' : score >= 40 ? 'var(--amber)' : 'var(--red)';

  // Greeting
  const hour = new Date().getHours();
  const greet = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const name = state.userName ? `, ${state.userName}` : '';
  document.getElementById('dash-greeting').textContent = `${greet}${name}! Here's your financial overview for ${state.month}.`;
}

function renderInsights() {
  const totalExp = getTotalExpenses();
  const savings  = getSavings();
  const rate     = getSavingsRate();
  const ins      = [];

  if (!state.income) {
    ins.push({ icon: 'i', cls: 'icon-blue', title: 'Get started', desc: 'Enter your monthly income and expenses in the Budget tab to unlock personalized insights.' });
  } else {
    if (rate >= 30)
      ins.push({ icon: '★', cls: 'icon-green', title: 'Outstanding savings rate!', desc: `You're saving ${rate}% of your income. That's excellent! Consider investing the surplus in SIPs or PPF for wealth creation.` });
    else if (rate >= 20)
      ins.push({ icon: '✓', cls: 'icon-green', title: 'Good savings rate', desc: `You save ${rate}% of your income — above the recommended 20%. Keep going and explore mutual funds for better returns.` });
    else if (rate < 10 && savings >= 0)
      ins.push({ icon: '!', cls: 'icon-amber', title: 'Low savings rate', desc: `Only ${rate}% saved this month. Target 20%+ by reducing discretionary spending like entertainment or dining out.` });
    else if (savings < 0)
      ins.push({ icon: '✗', cls: 'icon-red', title: 'Spending exceeds income!', desc: `You're in a deficit of ${fmt(Math.abs(savings))}. Immediate action needed — identify and cut non-essential expenses.` });

    const rent = state.categories.find(c => c.name === 'Rent / Housing');
    if (rent && rent.actual > state.income * 0.35)
      ins.push({ icon: '↑', cls: 'icon-amber', title: 'High housing cost', desc: `Rent is ${pct(rent.actual, state.income)}% of income. Financial experts recommend under 30%. Consider alternatives or look for cost-sharing.` });

    const food = state.categories.find(c => c.name === 'Food & Groceries');
    if (food && food.actual > state.income * 0.2)
      ins.push({ icon: '↑', cls: 'icon-amber', title: 'Food spending is high', desc: `Food is ${pct(food.actual, state.income)}% of income. Cook at home more often and reduce restaurant/delivery expenses.` });

    const overBudget = state.categories.filter(c => c.budget > 0 && c.actual > c.budget);
    if (overBudget.length)
      ins.push({ icon: '!', cls: 'icon-red', title: `Over budget in ${overBudget.length} categories`, desc: `You exceeded your budget in: ${overBudget.map(c => c.name.split('/')[0].trim()).join(', ')}. Review and adjust your spending.` });

    if (savings > 0 && totalExp > 0) {
      const efTarget = totalExp * 6;
      ins.push({ icon: '🛡', cls: 'icon-blue', title: 'Emergency fund tip', desc: `Build 6 months of expenses as emergency fund: ${fmt(efTarget)}. Start a recurring deposit or liquid fund today.` });
    }

    if (state.income > 30000 && rate >= 15)
      ins.push({ icon: '📈', cls: 'icon-green', title: 'Time to invest!', desc: `With ${fmt(savings)} in monthly surplus, start a SIP of at least ₹${Math.round(savings * 0.5 / 500) * 500}/month in a diversified equity fund for long-term wealth.` });
  }

  document.getElementById('insights-list').innerHTML = ins.map(i =>
    `<div class="insight-item">
      <div class="insight-icon ${i.cls}">${i.icon}</div>
      <div>
        <div class="insight-title">${i.title}</div>
        <div class="insight-desc">${i.desc}</div>
      </div>
    </div>`
  ).join('') || '<p class="empty-hint">Enter your financial data to see insights.</p>';
}

// ---- Budget Table ----
function renderExpenseTable() {
  const tbody = document.getElementById('expense-tbody');
  tbody.innerHTML = state.categories.map((c, i) => {
    const over = c.budget && c.actual > c.budget;
    const near = c.budget && !over && c.actual > c.budget * 0.8;
    const status = !c.budget ? `<span class="status-badge badge-none">No limit</span>`
      : over ? `<span class="status-badge badge-over">Over budget</span>`
      : near ? `<span class="status-badge badge-warn">Near limit</span>`
      : `<span class="status-badge badge-ok">On track</span>`;
    const isDefault = i < 10;
    return `<tr>
      <td style="font-weight:500">${c.name}</td>
      <td>
        <input type="number" placeholder="₹0" value="${c.actual || ''}"
          style="width:130px"
          oninput="state.categories[${i}].actual=+this.value||0;updateAll()"/>
      </td>
      <td>
        <input type="number" placeholder="₹0" value="${c.budget || ''}"
          style="width:130px"
          oninput="state.categories[${i}].budget=+this.value||0;updateAll()"/>
      </td>
      <td>${status}</td>
      <td>${!isDefault
        ? `<button class="btn btn-danger" style="padding:5px 10px;font-size:12px" onclick="removeCategory(${i})">✕ Remove</button>`
        : ''}</td>
    </tr>`;
  }).join('');
}

function addCategory() {
  const name   = document.getElementById('new-cat').value.trim();
  const actual = +document.getElementById('new-amt').value || 0;
  const budget = +document.getElementById('new-budget').value || 0;
  if (!name) { alert('Please enter a category name.'); return; }
  state.categories.push({ name, actual, budget });
  document.getElementById('new-cat').value    = '';
  document.getElementById('new-amt').value    = '';
  document.getElementById('new-budget').value = '';
  renderExpenseTable();
  updateAll();
}

function removeCategory(i) {
  state.categories.splice(i, 1);
  renderExpenseTable();
  updateAll();
}

function updateName() {
  state.userName = document.getElementById('user-name').value.trim();
  document.getElementById('sidebar-name').textContent = state.userName || 'User';
  const av = state.userName ? state.userName[0].toUpperCase() : 'U';
  document.querySelector('.avatar').textContent = av;
  updateAll();
}

// ---- Goals ----
function addGoal() {
  const name   = document.getElementById('goal-name').value.trim();
  const target = +document.getElementById('goal-target').value;
  const saved  = +document.getElementById('goal-saved').value || 0;
  const date   = document.getElementById('goal-date').value.trim();
  const type   = document.getElementById('goal-type').value;
  if (!name || !target) { alert('Please enter goal name and target amount.'); return; }
  state.goals.push({ name, target, saved, date, type });
  document.getElementById('goal-name').value   = '';
  document.getElementById('goal-target').value = '';
  document.getElementById('goal-saved').value  = '';
  document.getElementById('goal-date').value   = '';
  renderGoals();
  renderProjectionChart();
  saveState();
}

function renderGoals() {
  const el = document.getElementById('goals-list');
  if (!state.goals.length) {
    el.innerHTML = '<p class="empty-hint">No goals added yet. Add your first goal above!</p>';
    return;
  }
  el.innerHTML = state.goals.map((g, i) => {
    const p = Math.min(pct(g.saved, g.target), 100);
    const remaining = g.target - g.saved;
    const emoji = GOAL_EMOJIS[g.type] || '⭐';
    const monthlyNeeded = getSavings() > 0 ? Math.ceil(remaining / getSavings()) : '∞';
    return `<div class="goal-card">
      <div class="goal-header">
        <div class="goal-emoji">${emoji}</div>
        <div class="goal-info">
          <div class="goal-name">${g.name}</div>
          <div class="goal-meta">${g.date ? 'Target: ' + g.date + ' · ' : ''}~${monthlyNeeded} months at current savings</div>
        </div>
        <div class="goal-pct">${p}%</div>
        <button class="btn btn-danger" style="padding:6px 12px;font-size:12px" onclick="removeGoal(${i})">✕</button>
      </div>
      <div class="goal-progress-track">
        <div class="goal-progress-fill" style="width:${p}%"></div>
      </div>
      <div class="goal-amounts">
        <span>${fmt(g.saved)} saved</span>
        <span>${fmt(remaining)} remaining</span>
        <span>Target: ${fmt(g.target)}</span>
      </div>
    </div>`;
  }).join('');
}

function removeGoal(i) {
  state.goals.splice(i, 1);
  renderGoals();
  renderProjectionChart();
  saveState();
}

function updateAISummary() {
  const el = document.getElementById('ai-summary');
  const rows = [
    { label: 'Income',     val: fmt(state.income),      color: 'var(--blue)' },
    { label: 'Expenses',   val: fmt(getTotalExpenses()), color: 'var(--red)' },
    { label: 'Savings',    val: fmt(getSavings()),       color: getSavings() >= 0 ? 'var(--green)' : 'var(--red)' },
    { label: 'Save Rate',  val: getSavingsRate() + '%',  color: getSavingsRate() >= 20 ? 'var(--green)' : 'var(--amber)' },
    { label: 'Goals',      val: state.goals.length + ' active', color: 'var(--accent)' },
    { label: 'Health',     val: getHealthScore() + '/100', color: 'var(--accent)' },
  ];
  el.innerHTML = rows.map(r =>
    `<div class="ai-summary-row">
      <span class="ai-summary-label">${r.label}</span>
      <span class="ai-summary-val" style="color:${r.color}">${r.val}</span>
    </div>`
  ).join('');
}

// ---- Tab switching ----
function switchTab(id) {
  document.querySelectorAll('.nav-item').forEach(n => {
    n.classList.toggle('active', n.dataset.tab === id);
  });
  document.querySelectorAll('.tab-section').forEach(s => {
    s.classList.toggle('active', s.id === 'tab-' + id);
  });
  if (id === 'investments') calcSIP();
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// Load into form fields from state
function populateFormFromState() {
  if (state.income)   document.getElementById('income').value    = state.income;
  if (state.userName) document.getElementById('user-name').value = state.userName;
  document.getElementById('city').value  = state.city;
  document.getElementById('month').value = state.month;
  if (state.userName) {
    document.getElementById('sidebar-name').textContent = state.userName;
    document.querySelector('.avatar').textContent = state.userName[0].toUpperCase();
  }
}
