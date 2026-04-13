// ===== API SERVICE =====
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:5000/api'
  : 'https://YOUR-APP-NAME.up.railway.app/api';

function getToken()   { return localStorage.getItem('fintech_token'); }
function setToken(t)  { localStorage.setItem('fintech_token', t); }
function clearToken() { localStorage.removeItem('fintech_token'); localStorage.removeItem('fintech_user'); }
function setUser(u)   { localStorage.setItem('fintech_user', JSON.stringify(u)); }
function getUser()    { try { return JSON.parse(localStorage.getItem('fintech_user')); } catch { return null; } }
function isLoggedIn() { return !!getToken(); }

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  const res  = await fetch(API_BASE + path, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'API error ' + res.status);
  return data;
}

const AuthAPI = {
  async register(name, email, password, cityType) {
    const data = await apiFetch('/auth/register', { method: 'POST', body: JSON.stringify({ name, email, password, city_type: cityType }) });
    setToken(data.access_token); setUser(data.user); return data;
  },
  async login(email, password) {
    const data = await apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
    setToken(data.access_token); setUser(data.user); return data;
  },
  logout() { clearToken(); },
  async getProfile() { return apiFetch('/auth/profile'); },
  async updateProfile(payload) { return apiFetch('/auth/profile', { method: 'PUT', body: JSON.stringify(payload) }); },
};

const BudgetAPI = {
  async get(month, year)                    { return apiFetch('/budget/?month=' + month + '&year=' + year); },
  async updateIncome(income, month, year)   { return apiFetch('/budget/income', { method: 'PUT', body: JSON.stringify({ income, month, year }) }); },
  async addExpense(category, actual, budgetAmt, month, year) { return apiFetch('/budget/expense', { method: 'POST', body: JSON.stringify({ category, actual, budget_amt: budgetAmt, month, year }) }); },
  async deleteExpense(id)                   { return apiFetch('/budget/expense/' + id, { method: 'DELETE' }); },
  async saveBulk(income, expenses, month, year) { return apiFetch('/budget/save', { method: 'POST', body: JSON.stringify({ income, expenses, month, year }) }); },
  async getHistory()                        { return apiFetch('/budget/history'); },
};

const GoalsAPI = {
  async getAll()            { return apiFetch('/goals/'); },
  async add(payload)        { return apiFetch('/goals/', { method: 'POST', body: JSON.stringify(payload) }); },
  async update(id, payload) { return apiFetch('/goals/' + id, { method: 'PUT', body: JSON.stringify(payload) }); },
  async delete(id)          { return apiFetch('/goals/' + id, { method: 'DELETE' }); },
};

const DashboardAPI = {
  async getSummary(month, year) { return apiFetch('/dashboard/summary?month=' + month + '&year=' + year); },
};

const AdvisorAPI = {
  async chat(message)  { return apiFetch('/advisor/chat', { method: 'POST', body: JSON.stringify({ message }) }); },
  async getHistory()   { return apiFetch('/advisor/history'); },
  async clearHistory() { return apiFetch('/advisor/history', { method: 'DELETE' }); },
};

const NetWorthAPI = {
  async getAll()            { return apiFetch('/networth/'); },
  async add(payload)        { return apiFetch('/networth/', { method: 'POST', body: JSON.stringify(payload) }); },
  async delete(id)          { return apiFetch('/networth/' + id, { method: 'DELETE' }); },
};

const TaxAPI = {
  async calculate(payload) { return apiFetch('/tax/calculate', { method: 'POST', body: JSON.stringify(payload) }); },
};

const StocksAPI = {
  async getPopular()   { return apiFetch('/stocks/popular'); },
  async search(symbol) { return apiFetch('/stocks/search?symbol=' + symbol); },
  async getSIPFunds()  { return apiFetch('/stocks/sip-funds'); },
};

const EmailAPI = {
  async sendReport(month, year) { return apiFetch('/email/send-report', { method: 'POST', body: JSON.stringify({ month, year }) }); },
  async sendTest()              { return apiFetch('/email/test', { method: 'POST', body: '{}' }); },
};
