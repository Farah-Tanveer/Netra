/* =============================================
   NETRA - Frontend JavaScript
   Pure vanilla JS with no dependencies
   ============================================= */

// ================== STATE MANAGEMENT ==================

const appState = {
    currentSection: 'home',
    isCapturing: false,
    isDarkTheme: localStorage.getItem('theme') !== 'light',
    capturedPackets: [],
    packetCount: 0,
    dataSize: 0,
    startTime: null,
    captureInterval: null,
    mockProtocols: ['TCP', 'UDP', 'ICMP', 'DNS', 'HTTP', 'HTTPS'],
    mockIPs: [
        '192.168.1.105',
        '10.0.0.42',
        '172.16.0.89',
        '192.168.1.15',
        '8.8.8.8'
    ],
    mockPorts: [80, 443, 22, 53, 3306, 5432, 8080, 9090]
};

// ================== INITIALIZATION ==================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Set initial theme
    applyTheme();
    
    // Set up navigation
    setupNavigation();
    
    // Set up theme toggle
    setupThemeToggle();
    
    // Set up dashboard controls
    setupDashboard();
    
    // Set up contact form
    setupContactForm();
    
    // Set up keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Show home section
    navigateToSection('home');
    
    console.log('Netra Frontend Initialized');
}

// ================== NAVIGATION ==================

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = link.getAttribute('data-section');
            navigateToSection(sectionId);
            
            // Close mobile menu
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        });
    });

    // Hamburger menu toggle
    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        hamburger.classList.toggle('active');
    });
}

function navigateToSection(sectionId) {
    // Update state
    appState.currentSection = sectionId;

    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-section') === sectionId) {
            link.classList.add('active');
        }
    });

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Stop capture if navigating away from dashboard
    if (sectionId !== 'dashboard' && appState.isCapturing) {
        stopCapture();
    }
}

// ================== THEME TOGGLE ==================

function setupThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    themeToggle.addEventListener('click', toggleTheme);
}

function toggleTheme() {
    appState.isDarkTheme = !appState.isDarkTheme;
    localStorage.setItem('theme', appState.isDarkTheme ? 'dark' : 'light');
    applyTheme();
}

function applyTheme() {
    const html = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');
    
    if (appState.isDarkTheme) {
        html.classList.remove('light-theme');
        document.body.classList.remove('light-theme');
        themeToggle.textContent = '🌙';
    } else {
        html.classList.add('light-theme');
        document.body.classList.add('light-theme');
        themeToggle.textContent = '☀️';
    }
}

// ================== DASHBOARD CONTROLS ==================

function setupDashboard() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const checkStatsBtn = document.getElementById('checkStatsBtn');
    const backToDashboard = document.getElementById('backToDashboard');
    const startCaptureBtn = document.getElementById('startCaptureBtn');

    startBtn.addEventListener('click', startCapture);
    stopBtn.addEventListener('click', stopCapture);
    checkStatsBtn.addEventListener('click', () => navigateToSection('stats'));
    backToDashboard.addEventListener('click', () => navigateToSection('dashboard'));
    startCaptureBtn.addEventListener('click', () => {
        navigateToSection('dashboard');
        setTimeout(() => startCapture(), 300);
    });
}

function startCapture() {
    appState.isCapturing = true;
    appState.packetCount = 0;
    appState.dataSize = 0;
    appState.capturedPackets = [];
    appState.startTime = Date.now();

    // Update UI
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    document.getElementById('statusDot').classList.add('active');
    document.getElementById('statusText').textContent = 'Capturing...';

    // Clear packet list
    document.getElementById('packetList').innerHTML = '';

    // Start duration counter
    updateDuration();
    appState.captureInterval = setInterval(updateDuration, 1000);

    // Simulate packet capture
    simulatePacketCapture();

    console.log('Capture started');
}

function stopCapture() {
    appState.isCapturing = false;

    // Update UI
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('statusDot').classList.remove('active');
    document.getElementById('statusText').textContent = 'Stopped';

    // Clear interval
    if (appState.captureInterval) {
        clearInterval(appState.captureInterval);
    }

    console.log('Capture stopped');
}

function updateDuration() {
    if (!appState.startTime) return;

    const elapsed = Math.floor((Date.now() - appState.startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;

    document.getElementById('duration').textContent = 
        `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function simulatePacketCapture() {
    if (!appState.isCapturing) return;

    // Generate random packet
    const protocol = appState.mockProtocols[Math.floor(Math.random() * appState.mockProtocols.length)];
    const srcIP = appState.mockIPs[Math.floor(Math.random() * appState.mockIPs.length)];
    const dstIP = appState.mockIPs[Math.floor(Math.random() * appState.mockIPs.length)];
    const port = appState.mockPorts[Math.floor(Math.random() * appState.mockPorts.length)];
    const size = Math.floor(Math.random() * 1500) + 64; // 64-1564 bytes
    const timestamp = new Date().toLocaleTimeString();

    // Update counters
    appState.packetCount++;
    appState.dataSize += size;

    // Update UI counters
    document.getElementById('packetCount').textContent = appState.packetCount;
    document.getElementById('dataSize').textContent = (appState.dataSize / (1024 * 1024)).toFixed(2) + ' MB';

    // Add to packet list
    const packetList = document.getElementById('packetList');
    const packetItem = document.createElement('div');
    packetItem.className = 'packet-item';
    packetItem.innerHTML = `
        <strong>${protocol}</strong> | 
        ${srcIP}:${port} → ${dstIP} | 
        <span style="color: var(--color-primary);">${size}B</span> | 
        ${timestamp}
    `;

    // If this is the first packet, remove empty state
    if (packetList.querySelector('.empty-state')) {
        packetList.innerHTML = '';
    }

    packetList.insertBefore(packetItem, packetList.firstChild);

    // Keep only last 50 packets
    while (packetList.children.length > 50) {
        packetList.removeChild(packetList.lastChild);
    }

    // Schedule next packet (random interval: 100-500ms)
    const nextInterval = Math.random() * 400 + 100;
    setTimeout(simulatePacketCapture, nextInterval);
}

// ================== CONTACT FORM ==================

function setupContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (!contactForm) return;

    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();

        // Get form data
        const formData = new FormData(contactForm);
        const data = Object.fromEntries(formData);

        // Validate
        if (!data.name || !data.email || !data.subject || !data.message) {
            showAlert('Please fill in all fields', 'error');
            return;
        }

        // Simulate sending
        console.log('Form submitted:', data);
        
        // Store in localStorage
        localStorage.setItem('lastContact', JSON.stringify({
            ...data,
            timestamp: new Date().toISOString()
        }));

        // Show success message
        contactForm.classList.remove('active');
        document.getElementById('formSuccess').style.display = 'block';

        // Reset form
        contactForm.reset();

        // Hide success after 5 seconds
        setTimeout(() => {
            document.getElementById('formSuccess').style.display = 'none';
            contactForm.classList.add('active');
        }, 5000);
    });

    // Make form active by default
    contactForm.classList.add('active');
}

// ================== KEYBOARD SHORTCUTS ==================

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+K or Cmd+K - Toggle theme
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            toggleTheme();
        }

        // Ctrl+1 - Home
        if ((e.ctrlKey || e.metaKey) && e.key === '1') {
            e.preventDefault();
            navigateToSection('home');
        }

        // Ctrl+2 - Dashboard
        if ((e.ctrlKey || e.metaKey) && e.key === '2') {
            e.preventDefault();
            navigateToSection('dashboard');
        }

        // Ctrl+3 - Stats
        if ((e.ctrlKey || e.metaKey) && e.key === '3') {
            e.preventDefault();
            navigateToSection('stats');
        }

        // Space - Start/Stop (in dashboard)
        if (e.code === 'Space' && appState.currentSection === 'dashboard') {
            e.preventDefault();
            if (appState.isCapturing) {
                stopCapture();
            } else {
                startCapture();
            }
        }
    });
}

// ================== UTILITY FUNCTIONS ==================

function showAlert(message, type = 'info') {
    // Simple alert (can be enhanced with a toast notification system)
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ================== SCROLL ANIMATIONS ==================

function setupScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });

    document.querySelectorAll('.stats-card').forEach(card => {
        observer.observe(card);
    });
}

// ================== EXPORT STATE FOR DEBUGGING ==================

window.getAppState = () => appState;
window.toggleDebugMode = () => {
    console.log('=== NETRA APP STATE ===');
    console.log('Current Section:', appState.currentSection);
    console.log('Is Capturing:', appState.isCapturing);
    console.log('Packets Captured:', appState.packetCount);
    console.log('Data Size:', appState.dataSize);
    console.log('Theme:', appState.isDarkTheme ? 'Dark' : 'Light');
    console.log('=====================');
};

// ================== PERFORMANCE OPTIMIZATION ==================

// Debounce resize events
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        console.log('Window resized');
    }, 250);
});

// Monitor performance
if (window.performance && window.performance.timing) {
    window.addEventListener('load', () => {
        setTimeout(() => {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`Page Load Time: ${pageLoadTime}ms`);
        }, 0);
    });
}

console.log('Netra Frontend Script Loaded');
