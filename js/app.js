// ===== APP INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {

  if (!isLoggedIn()) { window.location.href = 'login.html'; return; }

  // Logout button
  const footer = document.querySelector('.sidebar-footer');
  const logoutBtn = document.createElement('button');
  logoutBtn.textContent = '⎋ Sign Out';
  logoutBtn.className = 'btn';
  logoutBtn.style.cssText = 'width:100%;margin-top:10px;font-size:13px;color:var(--text-muted)';
  logoutBtn.onclick = () => { AuthAPI.logout(); window.location.href = 'login.html'; };
  footer.appendChild(logoutBtn);

  // Load user
  try {
    const { user } = await AuthAPI.getProfile();
    setUser(user);
    state.userName = user.name;
    state.city     = user.city_type;
    document.getElementById('sidebar-name').textContent     = user.name;
    document.querySelector('.avatar').textContent           = user.name[0].toUpperCase();
    document.getElementById('user-name').value              = user.name;
    document.getElementById('city').value                   = user.city_type;
  } catch { AuthAPI.logout(); window.location.href = 'login.html'; return; }

  // Load data
  await loadDashboard();
  await loadGoals();
  await loadChatHistory();

  // Render
  renderExpenseTable();
  renderGoals();
  renderQuickQs();
  updateAISummary();
  updateAll();
  calcSIP();

  // Nav buttons
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      const tab = this.dataset.tab;
      switchTab(tab);
      if (tab === 'networth') loadNetWorth();
      if (tab === 'trends')   loadTrends();
      if (tab === 'stocks')   { loadStocks(); loadSIPFunds(); }
      if (window.innerWidth <= 900) document.getElementById('sidebar').classList.remove('open');
    });
  });

  // Close sidebar on mobile
  document.querySelector('.main-content').addEventListener('click', () => {
    if (window.innerWidth <= 900) document.getElementById('sidebar').classList.remove('open');
  });

  // Fix chat input Enter key
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        sendChat();
      }
    });
  }

  console.log('%c FinTech ✦ Backend Connected ', 'background:#7c6ff7;color:#fff;font-size:14px;padding:4px 10px;border-radius:4px');
});

// Load dashboard
async function loadDashboard() {
  try {
    const month = document.getElementById('month').value;
    const year  = new Date().getFullYear();
    const data  = await DashboardAPI.getSummary(month, year);
    state.income = data.income;
    document.getElementById('income').value = data.income || '';
    if (data.expenses && data.expenses.length > 0) {
      state.categories = data.expenses.map(e => ({ id: e.id, name: e.category, actual: e.actual, budget: e.budget_amt }));
    }
  } catch (err) { console.warn('Dashboard load:', err.message); }
}

// Load goals
async function loadGoals() {
  try {
    const data  = await GoalsAPI.getAll();
    state.goals = data.goals.map(g => ({ id: g.id, name: g.name, target: g.target, saved: g.saved, date: g.target_date, type: g.goal_type }));
  } catch (err) { console.warn('Goals load:', err.message); }
}

// Load chat history
async function loadChatHistory() {
  try {
    const data   = await AdvisorAPI.getHistory();
    const chatEl = document.getElementById('chat-messages');
    if (data.history && data.history.length > 0) {
      chatEl.innerHTML = '';
      data.history.forEach(log => appendMessage(log.role === 'assistant' ? 'ai' : 'user', log.message));
    }
  } catch (err) { console.warn('Chat load:', err.message); }
}

// Auto-save debounced
let saveTimeout = null;
function updateAll() {
  readBudgetInputs();
  updateMetrics();
  renderDonutChart();
  renderBudgetBars();
  renderInsights();
  renderProjectionChart();
  updateAISummary();
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(saveToBackend, 1500);
}

async function saveToBackend() {
  if (!isLoggedIn() || !state.income) return;
  try {
    const month = document.getElementById('month').value;
    const year  = new Date().getFullYear();
    await BudgetAPI.saveBulk(
      state.income,
      state.categories.map(c => ({ category: c.name, actual: c.actual || 0, budget_amt: c.budget || 0 })),
      month, year
    );
    const data = await DashboardAPI.getSummary(month, year);
    if (data.expenses) {
      data.expenses.forEach(e => {
        const cat = state.categories.find(c => c.name === e.category);
        if (cat) cat.id = e.id;
      });
    }
  } catch (err) { console.warn('Auto-save:', err.message); }
}

// Goals
async function addGoal() {
  const name   = document.getElementById('goal-name').value.trim();
  const target = +document.getElementById('goal-target').value;
  const saved  = +document.getElementById('goal-saved').value  || 0;
  const date   = document.getElementById('goal-date').value.trim();
  const type   = document.getElementById('goal-type').value;
  if (!name || !target) { alert('Please enter goal name and target amount.'); return; }
  try {
    const data = await GoalsAPI.add({ name, target, saved, target_date: date, goal_type: type });
    state.goals.push({ id: data.goal.id, name, target, saved, date, type });
    document.getElementById('goal-name').value   = '';
    document.getElementById('goal-target').value = '';
    document.getElementById('goal-saved').value  = '';
    document.getElementById('goal-date').value   = '';
    renderGoals();
    renderProjectionChart();
  } catch (err) { alert('Error: ' + err.message); }
}

async function removeGoal(i) {
  const goal = state.goals[i];
  try {
    if (goal.id) await GoalsAPI.delete(goal.id);
    state.goals.splice(i, 1);
    renderGoals();
    renderProjectionChart();
  } catch (err) { alert('Error: ' + err.message); }
}

// Chat
async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg   = input.value.trim();
  if (!msg) return;
  input.value = '';
  appendMessage('user', msg);
  const typingDiv = appendMessage('ai', '<div class="typing-dots"><span></span><span></span><span></span></div>');
  try {
    const data = await AdvisorAPI.chat(msg);
    typingDiv.querySelector('.chat-bubble').innerHTML = simpleMarkdown(data.reply);
  } catch (err) {
    typingDiv.querySelector('.chat-bubble').textContent = 'Error: ' + err.message;
  }
  document.getElementById('chat-messages').scrollTop = 99999;
}
