// ===== AI ADVISOR =====
const QUICK_QUESTIONS = [
  'How should I invest my monthly savings?',
  'Am I spending too much on rent?',
  'How to build a 6-month emergency fund?',
  'Best SIP funds for beginners in India?',
  'How can I reduce my monthly expenses?',
  'Explain PPF vs ELSS for tax saving',
  'What is the 50-30-20 rule?',
  'How to plan for retirement at 60?',
];

function renderQuickQs() {
  const el = document.getElementById('quick-qs');
  el.innerHTML = QUICK_QUESTIONS.map(q =>
    `<button class="quick-q-btn" onclick="askQuestion('${q.replace(/'/g,"\\'")}')">
      ${q}
    </button>`
  ).join('');
}

function askQuestion(q) {
  document.getElementById('chat-input').value = q;
  sendChat();
}

function buildSystemPrompt() {
  const totalExp = getTotalExpenses();
  const savings  = getSavings();
  const rate     = getSavingsRate();
  const score    = getHealthScore();

  const catBreakdown = state.categories
    .filter(c => c.actual > 0)
    .map(c => `  - ${c.name}: ₹${c.actual}${c.budget ? ' (budget: ₹' + c.budget + ')' : ''}`)
    .join('\n');

  const goalsList = state.goals.length
    ? state.goals.map(g => `  - ${g.name}: ₹${g.saved} saved of ₹${g.target} target${g.date ? ' by ' + g.date : ''}`).join('\n')
    : '  None set';

  return `You are FinTech — a friendly, expert personal finance advisor for India.

USER'S FINANCIAL PROFILE:
- Name: ${state.userName || 'User'}
- City type: ${state.city}
- Monthly Income: ₹${state.income}
- Total Monthly Expenses: ₹${totalExp}
- Monthly Savings: ₹${savings}
- Savings Rate: ${rate}%
- Financial Health Score: ${score}/100

EXPENSE BREAKDOWN:
${catBreakdown || '  No expenses entered yet'}

FINANCIAL GOALS:
${goalsList}

INSTRUCTIONS:
- Give personalized advice based on the user's actual numbers above.
- Always reference Indian financial instruments: SIP, PPF, ELSS, NPS, FD, RD, NSC, Sukanya Samriddhi, etc.
- Mention tax benefits under 80C, 80D where relevant.
- Use Indian number formatting (lakhs, crores).
- Be warm, encouraging, and practical. Avoid jargon unless explaining it.
- Keep responses concise (under 200 words unless the user asks for detail).
- If the user hasn't entered data, gently encourage them to do so for personalized advice.
- Format key numbers in bold using markdown **like this**.
- Use bullet points for lists.`;
}

function appendMessage(role, html) {
  const chatEl = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'chat-msg ' + role;
  const avatarText = role === 'ai' ? '✦' : (state.userName ? state.userName[0].toUpperCase() : 'U');
  const avatarClass = role === 'ai' ? 'ai-avatar' : 'user-avatar';
  div.innerHTML = `
    <div class="chat-avatar ${avatarClass}">${avatarText}</div>
    <div class="chat-bubble">${html}</div>`;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

function simpleMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<h4 style="margin:8px 0 4px;font-size:14px;font-weight:600">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 style="margin:10px 0 6px;font-size:15px;font-weight:700">$1</h3>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)+/gs, '<ul style="margin:6px 0;padding-left:1.2rem">$&</ul>')
    .replace(/\n{2,}/g, '</p><p style="margin-top:8px">')
    .replace(/\n/g, '<br>');
}

let chatHistory = [];

async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg   = input.value.trim();
  if (!msg) return;
  input.value = '';

  // User bubble
  appendMessage('user', msg);
  chatHistory.push({ role: 'user', content: msg });

  // Typing indicator
  const typingDiv = appendMessage('ai', '<div class="typing-dots"><span></span><span></span><span></span></div>');

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system: buildSystemPrompt(),
        messages: chatHistory,
      }),
    });

    const data  = await response.json();
    const reply = data.content?.map(b => b.text || '').join('') || 'I could not get a response. Please try again.';

    // Replace typing with actual response
    typingDiv.querySelector('.chat-bubble').innerHTML = simpleMarkdown(reply);
    chatHistory.push({ role: 'assistant', content: reply });

    // Keep history manageable
    if (chatHistory.length > 20) {
      chatHistory = chatHistory.slice(-18);
    }

  } catch (err) {
    typingDiv.querySelector('.chat-bubble').textContent =
      'Connection error. Please check your internet and try again.';
  }

  document.getElementById('chat-messages').scrollTop = 99999;
}