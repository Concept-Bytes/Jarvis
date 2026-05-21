'use strict';

// ── Element refs ────────────────────────────────────────
const $ = id => document.getElementById(id);
const messagesEl     = $('messages');
const welcomeEl      = $('welcome');
const inputEl        = $('message-input');
const sendBtn        = $('send-btn');
const micBtn         = $('mic-btn');
const micIcon        = $('mic-icon');
const stopIcon       = $('stop-icon');
const clearBtn       = $('clear-btn');
const statusDot      = $('status-dot');
const voiceToggleBtn = $('voice-toggle-btn');
const voiceOnIcon    = $('voice-on-icon');
const voiceOffIcon   = $('voice-off-icon');
const voiceOverlay   = $('voice-overlay');
const interimText    = $('interim-text');
const cancelVoiceBtn = $('cancel-voice-btn');
const container      = $('messages-container');

// ── State ───────────────────────────────────────────────
let isStreaming  = false;
let isRecording  = false;
let voiceEnabled = true;
let recognition  = null;

// ── Status indicator ─────────────────────────────────────
const setStatus = cls => {
  statusDot.className = 'status-dot' + (cls ? ' ' + cls : '');
};

// ── Voice output toggle ──────────────────────────────────
voiceToggleBtn.addEventListener('click', () => {
  voiceEnabled = !voiceEnabled;
  voiceOnIcon.style.display  = voiceEnabled ? '' : 'none';
  voiceOffIcon.style.display = voiceEnabled ? 'none' : '';
  voiceToggleBtn.classList.toggle('active', voiceEnabled);
  if (!voiceEnabled) window.speechSynthesis?.cancel();
});
voiceToggleBtn.classList.add('active');

// ── Auto-resize textarea ─────────────────────────────────
inputEl.addEventListener('input', () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
  sendBtn.disabled = !inputEl.value.trim() || isStreaming;
});

inputEl.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
    e.preventDefault();
    send(inputEl.value.trim());
  }
});

sendBtn.addEventListener('click', () => send(inputEl.value.trim()));

// ── Clear conversation ───────────────────────────────────
clearBtn.addEventListener('click', async () => {
  if (isStreaming) return;
  try { await fetch('/clear', { method: 'POST' }); } catch {}
  messagesEl.innerHTML = '';
  welcomeEl.classList.remove('hidden');
  setStatus('');
  window.speechSynthesis?.cancel();
});

// ── Scroll to bottom ──────────────────────────────────────
const scrollBottom = () => {
  requestAnimationFrame(() => { container.scrollTop = container.scrollHeight; });
};

// ── Welcome screen ────────────────────────────────────────
const hideWelcome = () => welcomeEl.classList.add('hidden');

// ── Add a message bubble ──────────────────────────────────
function addMessage(role, text = '') {
  hideWelcome();
  const msg    = document.createElement('div');
  msg.className = `message ${role}`;

  const label = document.createElement('div');
  label.className = 'msg-label';
  label.textContent = role === 'ai' ? 'JARVIS' : 'YOU';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  if (text) bubble.textContent = text;

  msg.appendChild(label);
  msg.appendChild(bubble);
  messagesEl.appendChild(msg);
  scrollBottom();
  return bubble;
}

// ── Typing indicator ──────────────────────────────────────
function showTyping() {
  hideWelcome();
  const el = document.createElement('div');
  el.className = 'typing-indicator';
  el.id = 'typing-indicator';
  for (let i = 0; i < 3; i++) {
    const d = document.createElement('div');
    d.className = 'typing-dot';
    el.appendChild(d);
  }
  messagesEl.appendChild(el);
  scrollBottom();
}

function hideTyping() {
  $('typing-indicator')?.remove();
}

// ── Streaming cursor ──────────────────────────────────────
function addCursor(bubble) {
  removeCursor();
  const cur = document.createElement('span');
  cur.className = 'cursor';
  cur.id = 'stream-cursor';
  bubble.appendChild(cur);
}

function removeCursor() {
  $('stream-cursor')?.remove();
}

// ── Send a message ────────────────────────────────────────
async function send(text) {
  if (!text || isStreaming) return;

  inputEl.value = '';
  inputEl.style.height = 'auto';
  sendBtn.disabled = true;
  isStreaming = true;
  setStatus('thinking');

  addMessage('user', text);
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) throw new Error(`Server error ${res.status}`);

    hideTyping();
    const bubble = addMessage('ai');
    addCursor(bubble);

    const reader  = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        try {
          handleEvent(JSON.parse(line.slice(6)), bubble);
        } catch {}
      }
    }

  } catch (err) {
    hideTyping();
    removeCursor();
    const b = addMessage('ai', `Error: ${err.message}`);
    b.classList.add('error-bubble');
    setStatus('error');
  } finally {
    removeCursor();
    isStreaming = false;
    sendBtn.disabled = !inputEl.value.trim();
    setStatus('ready');
    scrollBottom();
  }
}

// ── Handle SSE events ─────────────────────────────────────
function handleEvent(data, bubble) {
  if (data.type === 'token') {
    removeCursor();
    bubble.appendChild(document.createTextNode(data.text));
    addCursor(bubble);
    scrollBottom();
  } else if (data.type === 'error') {
    removeCursor();
    bubble.textContent = data.text || 'Something went wrong.';
    bubble.classList.add('error-bubble');
  } else if (data.type === 'done') {
    removeCursor();
    if (voiceEnabled && data.speech) speak(data.speech);
  }
}

// ── Text-to-speech ────────────────────────────────────────
function speak(text) {
  if (!voiceEnabled || !window.speechSynthesis || !text.trim()) return;
  window.speechSynthesis.cancel();

  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'en-US';
  utter.rate = 1.0;
  utter.pitch = 1.0;

  const pickVoice = () => {
    const voices = speechSynthesis.getVoices();
    const best = voices.find(v => v.lang.startsWith('en') && /Google|Natural|Neural|Premium/i.test(v.name))
              || voices.find(v => v.lang.startsWith('en'));
    if (best) utter.voice = best;
  };

  speechSynthesis.getVoices().length ? pickVoice() : (speechSynthesis.onvoiceschanged = pickVoice);
  speechSynthesis.speak(utter);
}

// ── Web Speech API voice input ────────────────────────────
function setupVoice() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    micBtn.title   = 'Voice input not supported in this browser. Use Chrome.';
    micBtn.style.opacity = '0.4';
    micBtn.disabled = true;
    return;
  }

  recognition = new SR();
  recognition.continuous      = false;
  recognition.interimResults  = true;
  recognition.lang            = 'en-US';

  recognition.onstart = () => {
    isRecording = true;
    micBtn.classList.add('recording');
    micIcon.style.display = 'none';
    stopIcon.style.display = '';
    voiceOverlay.classList.remove('hidden');
    interimText.textContent = 'Listening…';
    window.speechSynthesis?.cancel();
  };

  recognition.onresult = e => {
    const transcript = Array.from(e.results).map(r => r[0].transcript).join('');
    interimText.textContent = transcript || 'Listening…';
    if (e.results[e.results.length - 1].isFinal) {
      stopRecording();
      if (transcript.trim()) send(transcript.trim());
    }
  };

  recognition.onerror = e => {
    if (e.error !== 'aborted') interimText.textContent = 'Could not hear you — try again.';
    stopRecording();
  };

  recognition.onend = stopRecording;
}

function startRecording() {
  if (!recognition || isRecording || isStreaming) return;
  try { recognition.start(); } catch {}
}

function stopRecording() {
  if (!isRecording) return;
  isRecording = false;
  micBtn.classList.remove('recording');
  micIcon.style.display = '';
  stopIcon.style.display = 'none';
  voiceOverlay.classList.add('hidden');
  try { recognition?.stop(); } catch {}
}

micBtn.addEventListener('click', () => isRecording ? stopRecording() : startRecording());
cancelVoiceBtn.addEventListener('click', stopRecording);

// Keyboard shortcut: Space bar when input not focused = start voice
document.addEventListener('keydown', e => {
  if (e.code === 'Space' && document.activeElement !== inputEl && !isStreaming) {
    e.preventDefault();
    isRecording ? stopRecording() : startRecording();
  }
});

// ── Init ──────────────────────────────────────────────────
setupVoice();
setStatus('ready');
inputEl.focus();
