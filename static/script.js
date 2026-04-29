// ===== NETRA — Main Script =====

let isMonitoring = false;
let packetCount = 0;
let updateInterval = null;

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
        const res = await fetch('/api/start-monitoring', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            isMonitoring = true;
            packetCount = 0;
            updateDashboardUI();
            startAutoUpdate();
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
        const res = await fetch('/api/stop-monitoring', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            isMonitoring = false;
            if (updateInterval) clearInterval(updateInterval);
            updateDashboardUI();
            showNotification(
                `Monitoring stopped — ${data.packets_captured || 0} packets captured`,
                'success'
            );
            // Fetch final data from CSV
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
            protocol, src_ip: srcIp, dest_ip: destIp, limit: 50
        });
        const res = await fetch(`/api/live-packets?${params}`);
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
        const params = new URLSearchParams({ protocol, src_ip: srcIp, dest_ip: destIp, limit: 50 });
        const res = await fetch(`/api/traffic-data?${params}`);
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
        const res = await fetch('/api/logs?limit=30');
        const data = await res.json();
        if (data.success) {
            displayLogs(data.logs);
        }
    } catch (e) { console.error(e); }
}

async function fetchDetailedStats() {
    try {
        const res = await fetch('/api/stats');
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
    // Re-fetch data with cleared filters
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
        window.location.href = '/api/export-csv';
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
    // Auto-scroll to bottom for live data
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
    // Show newest first
    const reversed = [...logs].reverse();
    reversed.forEach(log => {
        // Parse log type for styling
        let logClass = 'log-info';
        if (log.includes('[START]')) logClass = 'log-start';
        else if (log.includes('[STOP]')) logClass = 'log-stop';
        else if (log.includes('[INIT]')) logClass = 'log-init';
        else if (log.includes('[SNIFFER]')) logClass = 'log-sniffer';
        else if (log.includes('[ERROR]')) logClass = 'log-error';

        html += `<div class="log-entry ${logClass}">${log}</div>`;
    });
    logList.innerHTML = html;
}

function displayDetailedStats(data) {
    // Summary
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val ?? '—'; };
    set('totalPackets', data.total_packets);
    set('uniqueSources', data.unique_sources);
    set('uniqueDestinations', data.unique_destinations);
    set('avgPacketSize', data.avg_packet_size ? `${data.avg_packet_size} B` : '—');
    set('totalDataKb', data.total_data_kb ? `${data.total_data_kb} KB` : '—');

    // Protocols
    const protocolList = document.getElementById('protocolList');
    if (protocolList && data.protocols) {
        const total = Object.values(data.protocols).reduce((a, b) => a + b, 0) || 1;
        protocolList.innerHTML = Object.entries(data.protocols).map(([name, count]) => {
            const pct = Math.round((count / total) * 100);
            return `<div class="stat-row"><span class="stat-name">${name}</span><span class="stat-count">${count} (${pct}%)</span></div><div class="stat-bar-wrap"><div class="stat-bar-fill" style="width:${pct}%"></div></div>`;
        }).join('');
    }

    // Sources
    const sourcesList = document.getElementById('sourcesList');
    if (sourcesList && data.top_sources) {
        sourcesList.innerHTML = Object.entries(data.top_sources).map(([ip, count]) =>
            `<div class="ip-item"><span class="ip-addr">${ip}</span><span class="ip-count">${count} packets</span></div>`
        ).join('') || '<div class="empty-state"><p>No data</p></div>';
    }

    // Ports
    const portsList = document.getElementById('portsList');
    if (portsList && data.top_ports) {
        const maxPort = Math.max(...Object.values(data.top_ports)) || 1;
        portsList.innerHTML = Object.entries(data.top_ports).map(([name, count]) => {
            const pct = Math.round((count / maxPort) * 100);
            return `<div class="port-item"><div class="port-info"><span class="port-name">${name}</span><span class="port-count">${count}</span></div><div class="stat-bar-wrap"><div class="stat-bar-fill" style="width:${pct}%"></div></div></div>`;
        }).join('');
    }
}

// ===== AUTO UPDATE =====
function startAutoUpdate() {
    if (updateInterval) clearInterval(updateInterval);
    // Fetch live packets every 1.5 seconds during monitoring
    updateInterval = setInterval(() => {
        if (isMonitoring) {
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

    // Theme toggle
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);

    // Dashboard buttons
    document.getElementById('startBtn')?.addEventListener('click', startMonitoring);
    document.getElementById('stopBtn')?.addEventListener('click', stopMonitoring);
    document.getElementById('applyFiltersBtn')?.addEventListener('click', () => {
        if (isMonitoring) fetchLivePackets();
        else fetchTrafficData();
    });
    document.getElementById('resetFiltersBtn')?.addEventListener('click', resetFilters);
    document.getElementById('exportCsvBtn')?.addEventListener('click', exportCsv);
    document.getElementById('refreshLogsBtn')?.addEventListener('click', fetchLogs);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            toggleTheme();
        }
    });

    // Page-specific init
    if (document.body.classList.contains('page-dashboard')) {
        updateDashboardUI();
        fetchTrafficData();
        fetchLogs();

        // Check if monitoring is already active (page reload)
        fetch('/api/status')
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
    }
    if (document.body.classList.contains('page-stats')) {
        fetchDetailedStats();
    }
});
