const stream = document.querySelector('#conversation');
const commandForm = document.querySelector('#command-form');
const commandInput = document.querySelector('#command');
const processStatus = document.querySelector('#process-health');
const stateStatus = document.querySelector('#state-status');
const aiStatus = document.querySelector('#ai-status');
const statusDot = document.querySelector('#status-dot');
const assistantState = document.querySelector('#assistant-state');
const stateLabel = document.querySelector('#state-label');
const stateDetail = document.querySelector('#state-detail');
const timeValue = document.querySelector('#time');
const dateValue = document.querySelector('#date');
const locationValue = document.querySelector('#location');
const weatherValue = document.querySelector('#weather');
let eventSource = null;

function updateClock() {
    const now = new Date();
    timeValue.textContent = now.toLocaleTimeString();
    dateValue.textContent = now.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
}

async function refreshEnvironment(position) {
    const params = position ? `?lat=${position.coords.latitude}&lon=${position.coords.longitude}` : '';
    try {
        const response = await fetch(`/environment${params}`);
        const data = await response.json();
        timeValue.textContent = data.time;
        dateValue.textContent = data.date;
        locationValue.textContent = data.location;
        weatherValue.textContent = data.weather;
    } catch (error) {
        locationValue.textContent = 'Unavailable';
        weatherValue.textContent = 'Unavailable';
    }
}

function addMessage(label, text, type = 'assistant') {
    const item = document.createElement('article');
    item.className = `message ${type}`;
    const title = document.createElement('span');
    title.className = 'label';
    title.textContent = label;
    item.append(title, document.createTextNode(text));
    stream.appendChild(item);
    stream.scrollTop = stream.scrollHeight;
}

function setStatus(data) {
    const running = Boolean(data.running);
    processStatus.textContent = running ? `RUNNING${data.pid ? ` · PID ${data.pid}` : ''}` : 'STOPPED';
    stateStatus.textContent = (data.state || 'unknown').toUpperCase();
    aiStatus.textContent = data.ai_configured ? 'CONFIGURED' : 'NOT CONFIGURED';
    statusDot.className = `status-dot ${running ? 'online' : ''}`;
    if (data.runtime_state) setAssistantState(data.runtime_state.state, data.runtime_state.detail);
}

function setAssistantState(state, detail) {
    const normalized = (state || 'idle').toLowerCase();
    assistantState.className = `assistant-state ${normalized}`;
    stateLabel.textContent = normalized.toUpperCase();
    stateDetail.textContent = detail || 'Waiting for your next command.';
}

async function refreshStatus() {
    try {
        const response = await fetch('/status');
        setStatus(await response.json());
    } catch (error) {
        processStatus.textContent = 'UNAVAILABLE';
        statusDot.className = 'status-dot error';
    }
}

function startLogStream() {
    if (eventSource) eventSource.close();
    eventSource = new EventSource('/logs');
    eventSource.onmessage = event => {
        const separator = event.data.indexOf(':');
        if (separator === -1) return;
        const label = event.data.slice(0, separator);
        const text = event.data.slice(separator + 1).trim();
        addMessage(label, text, label === 'Sameer Boss' ? 'user' : 'assistant');
    };
    eventSource.addEventListener('state', event => {
        const state = JSON.parse(event.data);
        setAssistantState(state.state, state.detail);
    });
    eventSource.onerror = () => eventSource.close();
}

async function processAction(path, button) {
    button.disabled = true;
    try {
        const response = await fetch(path, { method: 'POST' });
        const data = await response.json();
        if (data.status) addMessage('SYSTEM', data.status);
        if (path === '/start' || path === '/restart') startLogStream();
        if (path === '/stop' && eventSource) eventSource.close();
        await refreshStatus();
    } finally {
        button.disabled = false;
    }
}

document.querySelector('#start').addEventListener('click', event => processAction('/start', event.currentTarget));
document.querySelector('#restart').addEventListener('click', event => processAction('/restart', event.currentTarget));
document.querySelector('#stop').addEventListener('click', event => processAction('/stop', event.currentTarget));

commandForm.addEventListener('submit', async event => {
    event.preventDefault();
    const command = commandInput.value.trim();
    if (!command) return;
    addMessage('YOU', command, 'user');
    setAssistantState('thinking', 'Waiting for Gemini to respond...');
    commandInput.value = '';
    try {
        const response = await fetch('/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command })
        });
        const data = await response.json();
        addMessage('JARVIS', data.response || data.error || 'No response received.');
        setAssistantState('idle', 'Ready. Waiting for your next command.');
    } catch (error) {
        addMessage('SYSTEM', 'The dashboard could not reach the application.');
        setAssistantState('error', 'The command could not be completed.');
    }
});

setAssistantState('idle', 'Ready. Waiting for your next command.');
refreshStatus();
updateClock();
setInterval(updateClock, 1000);
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(refreshEnvironment, () => refreshEnvironment(null), { timeout: 8000 });
} else {
    refreshEnvironment(null);
}
setInterval(() => refreshEnvironment(null), 60000);
setInterval(refreshStatus, 5000);
