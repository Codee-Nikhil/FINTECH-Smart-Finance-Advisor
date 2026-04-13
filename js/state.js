// ===== STATE MANAGEMENT =====
const DEFAULT_CATEGORIES = [
  { name: 'Rent / Housing',     actual: 0, budget: 0 },
  { name: 'Food & Groceries',   actual: 0, budget: 0 },
  { name: 'Transport',          actual: 0, budget: 0 },
  { name: 'Utilities',          actual: 0, budget: 0 },
  { name: 'Entertainment',      actual: 0, budget: 0 },
  { name: 'Healthcare',         actual: 0, budget: 0 },
  { name: 'Education / EMI',    actual: 0, budget: 0 },
  { name: 'Clothing',           actual: 0, budget: 0 },
  { name: 'Personal Care',      actual: 0, budget: 0 },
  { name: 'Miscellaneous',      actual: 0, budget: 0 },
];

const GOAL_EMOJIS = {
  emergency: '🛡️', investment: '📈', travel: '✈️',
  education: '🎓', vehicle: '🚗', home: '🏠', other: '⭐'
};

const CHART_COLORS = [
  '#7c6ff7','#4da8ff','#3ecf8e','#f5a623','#f06375',
  '#a78bfa','#34d399','#fb923c','#60a5fa','#f472b6'
];

let state = {
  income: 0,
  city: 'metro',
  month: 'December',
  userName: '',
  categories: JSON.parse(JSON.stringify(DEFAULT_CATEGORIES)),
  goals: [],
};

// ---- Computed values ----
function getTotalExpenses() {
  return state.categories.reduce((s, c) => s + (c.actual || 0), 0);
}

function getSavings() {
  return state.income - getTotalExpenses();
}

function getSavingsRate() {
  if (!state.income) return 0;
  return Math.round((getSavings() / state.income) * 100);
}

function getHealthScore() {
  let score = 0;
  const rate = getSavingsRate();
  if (rate >= 30) score += 40;
  else if (rate >= 20) score += 30;
  else if (rate >= 10) score += 15;
  else if (rate > 0) score += 5;

  const rentCat = state.categories.find(c => c.name === 'Rent / Housing');
  if (rentCat && state.income) {
    const rentPct = rentCat.actual / state.income;
    if (rentPct <= 0.25) score += 20;
    else if (rentPct <= 0.35) score += 10;
  } else {
    score += 20;
  }

  const budgeted = state.categories.filter(c => c.budget > 0);
  const overBudget = budgeted.filter(c => c.actual > c.budget).length;
  if (budgeted.length > 0) {
    const compliance = 1 - overBudget / budgeted.length;
    score += Math.round(compliance * 25);
  } else {
    score += 15;
  }

  if (state.goals.length > 0) score += 15;
  return Math.min(score, 100);
}

function fmt(n) {
  return '₹' + Math.round(n).toLocaleString('en-IN');
}

function pct(a, b) {
  if (!b) return 0;
  return Math.round((a / b) * 100);
}

// ---- Persist to localStorage ----
function saveState() {
  try { localStorage.setItem('fintech_state', JSON.stringify(state)); } catch(e) {}
}

function loadState() {
  try {
    const saved = localStorage.getItem('fintech_state');
    if (saved) {
      const parsed = JSON.parse(saved);
      state = { ...state, ...parsed };
    }
  } catch(e) {}
}
