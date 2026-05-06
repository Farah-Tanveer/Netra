// ===== NETRA — Main Script (Security Enhanced) =====

let isMonitoring = false;
let packetCount = 0;
let updateInterval = null;
let dosBlockActive = false;

// ===== THEME =====
function initTheme() {
    const saved = localStorage.getItem('netra-theme') || 'dark';
    applyTheme(saved);
}
function applyTheme(theme) {
    if (theme === 'light') {
        document.body.classList.add('light-theme');
    } else {
        document.body.classList.remove('light-theme');
    }
    localStorage.setItem('netra-theme', theme);
}
function toggleTheme() {
    const isLight = document.body.classList.contains('light-theme');
    applyTheme(isLight ? 'dark' : 'light');
}

// ===== SECURITY UTILS =====
async function authFetch(url, options = {}) {
    const token = localStorage.getItem('netra-token');
    const headers = {
        ...options.headers,
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
    };

    try {
        const response = await fetch(url, { ...options, headers });
        
        // Handle DoS Detection (429)
        if (response.status === 429) {
            const data = await response.json();
            handleDoS(data.blocked_until);
            return { success: false, error: 'DoS Blocked' };
        }

        // Handle Unauthorized (401)
        if (response.status === 401 && !url.includes('/login')) {
            showLoginModal();
            return { success: false, error: 'Unauthorized' };
        }

        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        return { success: false, error: error.message };
    }
}

function handleDoS(seconds) {
    if (dosBlockActive) return;
    dosBlockActive = true;
    
    const screen = document.getElementById('dosBlockScreen');
    const countdown = document.getElementById('dosCountdown');
    const alert = document.getElementById('securityAlert');
    
    if (screen) screen.classList.add('active');
    if (alert) alert.classList.add('active');
    
    let remaining = seconds || 300;
    const timer = setInterval(() => {
        remaining--;
        const mins = Math.floor(remaining / 60);
        const secs = remaining % 60;
        if (countdown) countdown.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        
        if (remaining <= 0) {
            clearInterval(timer);
            dosBlockActive = false;
            if (screen) screen.classList.remove('active');
            if (alert) alert.classList.remove('active');
            window.location.reload();
        }
    }, 1000);
}

function showLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) modal.classList.add('active');
}

function hideLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) modal.classList.remove('active');
}

function updateAuthUI() {
    const authLink = document.getElementById('navAuthLink');
    if (!authLink) return;
    
    if (localStorage.getItem('netra-token')) {
        authLink.textContent = 'Logout';
        authLink.classList.add('auth-logged-in');
    } else {
        authLink.textContent = 'Login';
        authLink.classList.remove('auth-logged-in');
    }
}

function handleLogout() {
    localStorage.removeItem('netra-token');
    showNotification('Logged out successfully', 'info');
    updateAuthUI();
    // Redirect to home if on a protected-ish page or just refresh
    if (document.body.classList.contains('page-dashboard') || document.body.classList.contains('page-stats')) {
        window.location.reload();
    }
}

let authMode = 'login'; // 'login' or 'register'

function toggleAuth() {
    const title = document.getElementById('modalTitle');
    const desc = document.getElementById('modalDesc');
    const submitBtn = document.getElementById('authSubmitBtn');
    const toggleLink = document.getElementById('toggleAuthMode');
    const toggleText = document.getElementById('toggleText');
    
    if (authMode === 'login') {
        authMode = 'register';
        title.innerHTML = 'Create <span class="gradient-text">Account</span>';
        desc.textContent = 'Sign up to access and manage network monitoring.';
        submitBtn.textContent = 'Register Account';
        toggleLink.textContent = 'Login here';
        toggleText.textContent = 'Already have an account?';
    } else {
        authMode = 'login';
        title.innerHTML = 'Admin <span class="gradient-text">Login</span>';
        desc.textContent = 'Enter your credentials to manage network monitoring.';
        submitBtn.textContent = 'Login to Netra';
        toggleLink.textContent = 'Register Now';
        toggleText.textContent = "Don't have an account?";
    }
}

function initSecurity() {
    const authForm = document.getElementById('authForm');
    const closeBtn = document.getElementById('closeLogin');
    const navAuthLink = document.getElementById('navAuthLink');
    const toggleLink = document.getElementById('toggleAuthMode');
    
    updateAuthUI();

    if (toggleLink) {
        toggleLink.addEventListener('click', (e) => {
            e.preventDefault();
            toggleAuth();
        });
    }

    if (navAuthLink) {
        navAuthLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (localStorage.getItem('netra-token')) {
                handleLogout();
            } else {
                showLoginModal();
            }
        });
    }

    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('authUsername').value;
            const password = document.getElementById('authPassword').value;
            
            const endpoint = authMode === 'login' ? '/login' : '/register';
            
            try {
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                
                if (data.success) {
                    if (authMode === 'register') {
                        showNotification('Registration successful! Please login.', 'success');
                        toggleAuth(); // Switch to login mode
                    } else {
                        localStorage.setItem('netra-token', data.token);
                        showNotification('Authentication successful!', 'success');
                        hideLoginModal();
                        updateAuthUI();
                        if (document.body.classList.contains('page-dashboard') || document.body.classList.contains('page-stats')) {
                            window.location.reload();
                        }
                    }
                } else {
                    showNotification(data.message || 'Error occurred', 'error');
                }
            } catch (err) {
                showNotification('Authentication failed', 'error');
            }
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', hideLoginModal);
    }

    // Intercept "Start Capture" if not logged in
    const startCaptureBtn = document.getElementById('startCaptureBtn');
    if (startCaptureBtn) {
        startCaptureBtn.addEventListener('click', (e) => {
            if (!localStorage.getItem('netra-token')) {
                e.preventDefault();
                showLoginModal();
            }
        });
    }
}


// ===== NAVBAR SCROLL EFFECT =====
function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 30);
    });
    // Hamburger
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            const spans = hamburger.querySelectorAll('span');
            hamburger.classList.toggle('open');
            if (hamburger.classList.contains('open')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
            } else {
                spans[0].style.transform = '';
                spans[1].style.opacity = '';
                spans[2].style.transform = '';
            }
        });
        // Close menu on link click (mobile)
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                hamburger.classList.remove('open');
                const spans = hamburger.querySelectorAll('span');
                spans[0].style.transform = '';
                spans[1].style.opacity = '';
                spans[2].style.transform = '';
            });
        });
    }
}

// ===== PARTICLES (Hero) =====
function initParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    for (let i = 0; i < 30; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        p.style.left = Math.random() * 100 + '%';
        p.style.animationDuration = (4 + Math.random() * 8) + 's';
        p.style.animationDelay = Math.random() * 6 + 's';
        p.style.width = p.style.height = (2 + Math.random() * 3) + 'px';
        container.appendChild(p);
    }
}

// ===== SCROLL ANIMATIONS =====
function initScrollAnimations() {
    const els = document.querySelectorAll('.feature-card, .info-card, .tech-pill, .glass-card');
    if (!els.length) return;
    els.forEach(el => el.classList.add('fade-in'));
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    els.forEach(el => observer.observe(el));
}

// ===== API CALLS =====
async function startMonitoring() {
    try {
        const res = await authFetch('/api/start-monitoring', { method: 'POST' });
        if (!res.ok) return;
        const data = await res.json();
        if (data.success) {
            isMonitoring = true;
            packetCount = 0;
            displayTraffic([], true);
            updateMiniStats({total: 0, tcp: 0, udp: 0, icmp: 0, avg_size: 0, total_data: 0});
            updateDashboardUI();
            startAutoUpdate();
            fetchLivePackets();
            showNotification('Real-time packet capture started!', 'success');
        } else {
            showNotification(data.message || 'Failed to start', 'error');
        }
    } catch (e) {
        console.error(e);
        showNotification('Error starting monitoring', 'error');
    }
}

async function stopMonitoring() {
    try {
        const res = await authFetch('/api/stop-monitoring', { method: 'POST' });
        if (!res.ok) return;
        const data = await res.json();
        if (data.success) {
            isMonitoring = false;
            if (updateInterval) clearInterval(updateInterval);
            updateDashboardUI();
            showNotification(
                `Monitoring stopped — ${data.packets_captured || 0} packets captured`,
                'success'
            );
            fetchTrafficData();
            fetchLogs();
        }
    } catch (e) {
        console.error(e);
        showNotification('Error stopping monitoring', 'error');
    }
}

async function fetchLivePackets() {
    try {
        const protocol = document.getElementById('protocolFilter')?.value || 'ALL';
        const srcIp = document.getElementById('srcIpFilter')?.value || '';
        const destIp = document.getElementById('destIpFilter')?.value || '';
        const params = new URLSearchParams({
            protocol, src_ip: srcIp, dest_ip: destIp, limit: 50, _t: Date.now()
        });
        const res = await authFetch(`/api/live-packets?${params}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.success) {
            displayTraffic(data.data, true);
            updateMiniStats(data.stats);
            packetCount = data.stats.total;
            updateDashboardUI();
        }
    } catch (e) { console.error(e); }
}

async function fetchTrafficData() {
    try {
        const protocol = document.getElementById('protocolFilter')?.value || 'ALL';
        const srcIp = document.getElementById('srcIpFilter')?.value || '';
        const destIp = document.getElementById('destIpFilter')?.value || '';
        const params = new URLSearchParams({ protocol, src_ip: srcIp, dest_ip: destIp, limit: 50, _t: Date.now() });
        const res = await authFetch(`/api/traffic-data?${params}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.success) {
            displayTraffic(data.data, false);
            updateMiniStats(data.stats);
            packetCount = data.stats.total;
            updateDashboardUI();
        }
    } catch (e) { console.error(e); }
}

async function fetchLogs() {
    try {
        const res = await authFetch(`/api/logs?limit=30&_t=${Date.now()}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.success) {
            displayLogs(data.logs);
        }
    } catch (e) { console.error(e); }
}

async function fetchDetailedStats() {
    try {
        const res = await authFetch(`/api/stats?_t=${Date.now()}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.success) displayDetailedStats(data);
    } catch (e) { console.error(e); }
}

// ===== RESET FILTERS =====
function resetFilters() {
    const protocolFilter = document.getElementById('protocolFilter');
    const srcIpFilter = document.getElementById('srcIpFilter');
    const destIpFilter = document.getElementById('destIpFilter');
    if (protocolFilter) protocolFilter.value = 'ALL';
    if (srcIpFilter) srcIpFilter.value = '';
    if (destIpFilter) destIpFilter.value = '';
    if (isMonitoring) {
        fetchLivePackets();
    } else {
        fetchTrafficData();
    }
    showNotification('Filters cleared', 'success');
}

// ===== EXPORT CSV =====
async function exportCsv() {
    try {
        const token = localStorage.getItem('netra-token');
        if (!token) {
            showLoginModal();
            return;
        }
        window.location.href = `/api/export-csv?token=${token}`;
        showNotification('Exporting CSV...', 'success');
    } catch (e) {
        showNotification('Error exporting CSV', 'error');
    }
}

// ===== UI UPDATES =====
function updateDashboardUI() {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    const countEl = document.getElementById('packetCount');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const liveBadge = document.getElementById('liveBadge');

    if (dot) dot.className = isMonitoring ? 'status-dot active' : 'status-dot';
    if (text) text.textContent = isMonitoring ? 'Capturing Live Packets' : 'Ready';
    if (countEl) countEl.textContent = packetCount;
    if (startBtn) startBtn.disabled = isMonitoring;
    if (stopBtn) stopBtn.disabled = !isMonitoring;
    if (liveBadge) liveBadge.style.display = isMonitoring ? 'inline-flex' : 'none';
}

function updateMiniStats(stats) {
    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val || 0;
    };
    set('packetCount', stats.total);
    set('tcpCount', stats.tcp);
    set('udpCount', stats.udp);
    set('icmpCount', stats.icmp);
    set('avgSize', stats.avg_size || 0);
    set('totalData', stats.total_data || 0);
}

function displayTraffic(packets, isLive) {
    const list = document.getElementById('packetList');
    if (!list) return;
    if (!packets || !packets.length) {
        list.innerHTML = '<div class="empty-state"><p>No packets captured yet</p><p class="empty-hint">Click Start to begin real-time monitoring</p></div>';
        return;
    }
    let html = '<div class="traffic-table-wrapper"><table class="traffic-table"><thead><tr><th>Time</th><th>Source IP</th><th>Destination IP</th><th>Protocol</th><th>Src Port</th><th>Dst Port</th><th>Service</th><th>Size</th></tr></thead><tbody>';
    packets.forEach(p => {
        const service = p.Service || 'Unknown';
        html += `<tr>
            <td>${p.Time || '—'}</td>
            <td><span class="ip-badge">${p.Source_IP}</span></td>
            <td><span class="ip-badge">${p.Destination_IP}</span></td>
            <td><span class="protocol-badge ${(p.Protocol||'').toLowerCase()}">${p.Protocol}</span></td>
            <td>${p.Source_Port}</td>
            <td>${p.Destination_Port}</td>
            <td><span class="service-badge">${service}</span></td>
            <td>${p.Packet_Size} B</td>
        </tr>`;
    });
    html += '</tbody></table></div>';
    list.innerHTML = html;
    if (isLive) {
        list.scrollTop = list.scrollHeight;
    }
}

function displayLogs(logs) {
    const logList = document.getElementById('logList');
    if (!logList) return;
    if (!logs || !logs.length) {
        logList.innerHTML = '<div class="empty-state"><p>No logs yet</p></div>';
        return;
    }
    let html = '';
    const reversed = [...logs].reverse();
    reversed.forEach(log => {
        let logClass = 'log-info';
        if (log.includes('[START]')) logClass = 'log-start';
        else if (log.includes('[STOP]')) logClass = 'log-stop';
        else if (log.includes('[INIT]')) logClass = 'log-init';
        else if (log.includes('[SNIFFER]')) logClass = 'log-sniffer';
        else if (log.includes('[ERROR]')) logClass = 'log-error';
        else if (log.includes('[SECURITY]')) logClass = 'log-error';

        html += `<div class="log-entry ${logClass}">${log}</div>`;
    });
    logList.innerHTML = html;
}

function displayDetailedStats(data) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val ?? '—'; };
    set('totalPackets', data.total_packets);
    set('uniqueSources', data.unique_sources);
    set('uniqueDestinations', data.unique_destinations);
    set('avgPacketSize', data.avg_packet_size ? `${data.avg_packet_size} B` : '—');
    set('totalDataKb', data.total_data_kb ? `${data.total_data_kb} KB` : '—');

    const total = data.total_packets || 1;
    
    const getPctText = (count, total) => {
        if (count === 0) return '0';
        const pct = (count / total) * 100;
        if (pct > 0 && Math.round(pct) === 0) return '<1';
        return Math.round(pct);
    };

    const protocolList = document.getElementById('protocolList');
    if (protocolList && data.protocols) {
        protocolList.innerHTML = Object.entries(data.protocols).map(([name, count]) => {
            const pctVal = (count / total) * 100;
            const pctText = getPctText(count, total);
            return `<div class="stat-row"><span class="stat-name">${name}</span><span class="stat-count">${count} (${pctText}%)</span></div><div class="stat-bar-wrap"><div class="stat-bar-fill" style="width:${pctVal}%"></div></div>`;
        }).join('');
    }

    // Packet Size Distribution
    const sizeDistList = document.getElementById('sizeDistList');
    if (sizeDistList && data.size_dist) {
        sizeDistList.innerHTML = Object.entries(data.size_dist).map(([name, count]) => {
            const pctVal = (count / total) * 100;
            const pctText = getPctText(count, total);
            return `<div class="stat-row"><span class="stat-name">${name}</span><span class="stat-count">${count} (${pctText}%)</span></div><div class="stat-bar-wrap"><div class="stat-bar-fill" style="width:${pctVal}%"></div></div>`;
        }).join('');
    }

    const sourcesList = document.getElementById('sourcesList');
    if (sourcesList && data.top_sources) {
        sourcesList.innerHTML = Object.entries(data.top_sources).map(([ip, count]) => {
            const pctVal = (count / total) * 100;
            const pctText = getPctText(count, total);
            return `<div class="ip-item">
                        <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 5px;">
                            <span class="ip-addr">${ip}</span>
                            <span class="ip-count">${count} (${pctText}%)</span>
                        </div>
                        <div class="stat-bar-wrap"><div class="stat-bar-fill" style="width:${pctVal}%"></div></div>
                    </div>`;
        }).join('') || '<div class="empty-state"><p>No data</p></div>';
    }

    const portsList = document.getElementById('portsList');
    if (portsList && data.top_ports) {
        portsList.innerHTML = Object.entries(data.top_ports).map(([name, count]) => {
            const pctVal = (count / total) * 100;
            const pctText = getPctText(count, total);
            return `<div class="port-item">
                        <div class="port-info" style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 5px;">
                            <span class="port-name">${name}</span>
                            <span class="port-count">${count} (${pctText}%)</span>
                        </div>
                        <div class="stat-bar-wrap"><div class="stat-bar-fill" style="width:${pctVal}%"></div></div>
                    </div>`;
        }).join('');
    }
}

// ===== AUTO UPDATE =====
function startAutoUpdate() {
    if (updateInterval) clearInterval(updateInterval);
    updateInterval = setInterval(() => {
        if (isMonitoring && !dosBlockActive) {
            fetchLivePackets();
        }
    }, 1500);
}

// ===== NOTIFICATIONS =====
function showNotification(msg, type = 'info') {
    const n = document.createElement('div');
    n.className = `notification notification-${type}`;
    n.textContent = msg;
    document.body.appendChild(n);
    setTimeout(() => n.remove(), 3200);
}

// ===== CONTACT FORM =====
function initContactForm() {
    const form = document.getElementById('contactForm');
    const success = document.getElementById('formSuccess');
    if (!form || !success) return;
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        form.style.display = 'none';
        success.classList.add('show');
        setTimeout(() => {
            form.style.display = '';
            success.classList.remove('show');
            form.reset();
        }, 3500);
    });
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initNavbar();
    initParticles();
    initScrollAnimations();
    initContactForm();
    initSecurity();

    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);

    document.getElementById('startBtn')?.addEventListener('click', startMonitoring);
    document.getElementById('stopBtn')?.addEventListener('click', stopMonitoring);
    document.getElementById('applyFiltersBtn')?.addEventListener('click', () => {
        if (isMonitoring) fetchLivePackets();
        else fetchTrafficData();
    });
    document.getElementById('resetFiltersBtn')?.addEventListener('click', resetFilters);
    document.getElementById('exportCsvBtn')?.addEventListener('click', exportCsv);
    document.getElementById('refreshLogsBtn')?.addEventListener('click', fetchLogs);

    document.getElementById('resetSessionBtn')?.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to clear all monitoring data and logs? This cannot be undone.')) return;
        
        try {
            const res = await authFetch('/api/reset-session', { method: 'POST' });
            if (!res.ok) return;
            const data = await res.json();
            if (data.success) {
                showNotification('Session data cleared!', 'success');
                window.location.reload();
            }
        } catch (e) {
            showNotification('Error resetting session', 'error');
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            toggleTheme();
        }
    });

    if (document.body.classList.contains('page-dashboard')) {
        // Init UI for either Guest or Admin
        updateDashboardUI();
        fetchTrafficData();
        fetchLogs();
        
        // Update status and potentially start auto-update if sniffer is running
        authFetch(`/api/status?_t=${Date.now()}`)
            .then(r => r.json())
            .then(data => {
                if (data.monitoring) {
                    isMonitoring = true;
                    packetCount = data.packet_count || 0;
                    updateDashboardUI();
                    startAutoUpdate();
                }
            })
            .catch(() => {});

        // If not logged in, show a subtle hint
        if (!localStorage.getItem('netra-token')) {
            showNotification('Entering Guest Mode (Read-Only). Login as Admin to start capture.', 'info');
        }
    }
    if (document.body.classList.contains('page-stats')) {
        fetchDetailedStats();
    }
});
