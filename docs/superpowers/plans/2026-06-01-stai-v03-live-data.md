# STAI v0.3 — Live Data Simulation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add live data simulation to the STAI dashboard — cases appear in real-time, alerts flash, stats tick, the Orb reacts, and cards have subtle parallax tilt.

**Architecture:** All changes go into `frontend/index.html`. A `LiveDataEngine` class generates realistic AMR data on random intervals and emits custom DOM events. UI sections listen for these events and animate new data in. A parallax hover effect is added to stat and alert cards.

**Tech Stack:** Vanilla JavaScript (no new dependencies), CSS animations, custom DOM events

**Baseline:** v1.0 tagged commit

---

## File Structure

Single file: `frontend/index.html`

Changes by region:
- `<style>` block: New CSS for LIVE badge, alert banner, parallax, slide-in animations
- `<body>`: Add LIVE badge div, alert banner container
- `<script>` block: LiveDataEngine class, data pools, event listeners, parallax init

---

### Task 1: LIVE Badge + Alert Banner HTML/CSS

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: Add LIVE badge HTML**

Insert after `<body>` opening, before the aurora-mesh div:

```html
<!-- LIVE Badge -->
<div id="live-badge" aria-label="Live data feed active">
  <span class="live-dot"></span>
  <span>LIVE</span>
</div>

<!-- Alert Banner Container -->
<div id="alert-banner-container"></div>
```

- [ ] **Step 2: Add LIVE badge + banner CSS**

Append to `<style>` before the `</style>` closing:

```css
/* ═══════════════════════════════════════════════════════════
   LIVE DATA — Badge + Banner
   ═══════════════════════════════════════════════════════════ */

#live-badge {
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px 4px 8px;
  border-radius: 999px;
  background: rgba(6,9,15,0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(74,222,128,0.2);
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.15em;
  color: var(--aurora-1);
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

#live-badge.visible {
  opacity: 1;
  transform: translateY(0);
}

.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--aurora-1);
  animation: livePulse 2s ease-in-out infinite;
}

@keyframes livePulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(74,222,128,0.4); }
  50% { opacity: 0.6; box-shadow: 0 0 0 4px rgba(74,222,128,0); }
}

/* Alert Banner */
#alert-banner-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10001;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 8px;
  pointer-events: none;
}

.alert-banner {
  pointer-events: all;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  margin-bottom: 4px;
  border-radius: 8px;
  background: rgba(239,68,68,0.95);
  backdrop-filter: blur(12px);
  color: white;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(239,68,68,0.3);
  animation: bannerSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  max-width: 600px;
  width: calc(100% - 32px);
}

.alert-banner.dismissing {
  animation: bannerSlideOut 0.3s ease-in forwards;
}

@keyframes bannerSlideIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes bannerSlideOut {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-20px); }
}

.alert-banner-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
  flex-shrink: 0;
  animation: alertPulse 1.5s ease-in-out infinite;
}

.alert-banner-text {
  flex: 1;
  line-height: 1.3;
}

.alert-banner-dismiss {
  background: none;
  border: none;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  font-size: 16px;
  padding: 0 4px;
  line-height: 1;
}

.alert-banner-dismiss:hover { color: white; }

/* Case row slide-in */
.case-row-new {
  animation: caseSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes caseSlideIn {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}

.case-row-glow {
  box-shadow: inset 0 0 12px rgba(0,240,255,0.15);
  transition: box-shadow 2s ease-out;
}

/* Alert card slide-in */
.alert-card-new {
  animation: alertCardSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes alertCardSlideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

.alert-card-glow {
  transition: box-shadow 2s ease-out;
}

.critical.alert-card-glow { box-shadow: inset 0 0 16px rgba(239,68,68,0.15); }
.high.alert-card-glow { box-shadow: inset 0 0 16px rgba(245,158,11,0.12); }
.medium.alert-card-glow { box-shadow: inset 0 0 16px rgba(0,240,255,0.1); }

/* Parallax tilt */
.parallax-tilt {
  transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
  will-change: transform;
}

/* Stat flash */
.stat-flash {
  animation: statFlash 0.6s ease-out;
}

@keyframes statFlash {
  0% { color: var(--accent); text-shadow: 0 0 12px rgba(0,240,255,0.4); }
  100% { color: var(--text); text-shadow: none; }
}

.stat-flash-red {
  animation: statFlashRed 0.6s ease-out;
}

@keyframes statFlashRed {
  0% { color: var(--red); text-shadow: 0 0 12px rgba(239,68,68,0.4); }
  100% { color: var(--text); text-shadow: none; }
}

/* Orb live reactions */
#orb.orb-case-pulse {
  animation: orbCasePulse 0.4s ease-out;
}

@keyframes orbCasePulse {
  0% { transform: scale(1); box-shadow: 0 0 30px rgba(45,212,191,0.3); }
  50% { transform: scale(1.12); box-shadow: 0 0 50px rgba(45,212,191,0.5); }
  100% { transform: scale(1); box-shadow: 0 0 30px rgba(45,212,191,0.2); }
}

#orb.orb-alert-amber {
  background: radial-gradient(circle at 35% 35%, var(--amber), #D97706);
  box-shadow: 0 0 30px rgba(245,158,11,0.3);
}

#orb.orb-alert-red {
  animation: orbAlertRed 0.6s ease-out;
}

@keyframes orbAlertRed {
  0% { transform: scale(1); }
  30% { transform: scale(1.2); background: radial-gradient(circle at 35% 35%, var(--red), #DC2626); box-shadow: 0 0 50px rgba(239,68,68,0.4); }
  100% { transform: scale(1); }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .case-row-new, .alert-card-new, .alert-banner { animation: none; }
  .parallax-tilt { transition: none; }
  #live-badge { opacity: 1; transform: none; }
}
```

- [ ] **Step 3: Verify**

Open browser. LIVE badge should appear top-left after a moment. No alert banners yet. Page otherwise unchanged.

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html
git commit -m "feat: add LIVE badge and alert banner for v0.3"
```

---

### Task 2: LiveDataEngine — Data Pools + Engine Class

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: Add complaint pool and engine**

Append to `<script>` before the `// ── Init everything ──` block:

```javascript
/* ═══════════════════════════════════════════════════════════
   LIVE DATA ENGINE — v0.3
   ═══════════════════════════════════════════════════════════ */

const COMPLAINT_POOL = [
  'Fever with chills for 5 days, no response to amoxicillin',
  'Productive cough with yellow sputum, chest pain on deep breathing',
  'Burning urination, frequency, suprapubic pain for 3 days',
  'Infected surgical wound with purulent discharge, erythema spreading',
  'Persistent watery diarrhea with dehydration signs, 4 days',
  'Severe headache, neck stiffness, photophobia, fever 39.5C',
  'Joint pain with swelling, heat, limited range of motion',
  'Non-healing ulcer on foot, surrounding cellulitis, diabetic patient',
  'High fever with rash, myalgia, severe fatigue — 3 days',
  'Dysuria with cloudy urine, foul odor, previous UTI history',
  'Chest congestion, wheezing, green sputum, SOB on exertion',
  'Purulent conjunctivitis, eye discharge, crusting on eyelids',
  'Abdominal pain, bloody stool, fever, recent antibiotic course',
  'Ear discharge, otalgia, hearing loss — 2 weeks post-amoxicillin',
  'Pneumonia not responding to 3 days of azithromycin',
  'Post-operative wound infection with MRSA-positive culture',
  'Recurrent UTI with ESBL-producing E. coli, nitrofurantoin failure',
  'Meningitis symptoms with ceftriaxone-resistant S. pneumoniae',
  'Gonorrhea treatment failure after dual therapy',
  'Cellulitis spreading despite 48h of flucloxacillin',
  'Neonatal sepsis with multi-drug resistant Klebsiella',
  'Diabetic foot infection with osteomyelitis, Pseudomonas suspected',
  'TB treatment failure — sputum still positive after 4 months',
  'Surgical site infection with Acinetobacter baumannii',
  'Ventilator-associated pneumonia with carbapenem-resistant organisms',
  'Intra-abdominal abscess post-surgery, polymicrobial resistance',
  'Osteomyelitis with methicillin-resistant Staphylococcus aureus',
  'Pyelonephritis with extended-spectrum beta-lactamase producers',
  'Bacteremia with vancomycin-resistant Enterococcus',
  'Wound infection in conflict zone, no response to empiric therapy',
];

const DISTRICT_WEIGHTS = [
  { district: 'Lagos', weight: 15 },
  { district: 'Nairobi', weight: 12 },
  { district: 'Accra', weight: 10 },
  { district: 'Kinshasa', weight: 9 },
  { district: 'Kampala', weight: 8 },
  { district: 'Johannesburg', weight: 8 },
  { district: 'Dar es Salaam', weight: 7 },
  { district: 'Addis Ababa', weight: 7 },
  { district: 'Mombasa', weight: 6 },
  { district: 'Kumasi', weight: 5 },
  { district: 'Abuja', weight: 5 },
  { district: 'Lusaka', weight: 3 },
  { district: 'Harare', weight: 3 },
  { district: 'Lilongwe', weight: 2 },
  { district: 'Dakar', weight: 2 },
];

const SOURCE_WEIGHTS = [
  { source: 'telegram', weight: 40 },
  { source: 'whatsapp', weight: 30 },
  { source: 'ussd', weight: 15 },
  { source: 'sms', weight: 10 },
  { source: 'manual', weight: 5 },
];

const SEVERITY_WEIGHTS = [
  { severity: 'moderate', weight: 60 },
  { severity: 'mild', weight: 25 },
  { severity: 'severe', weight: 10 },
  { severity: 'critical', weight: 5 },
];

const ALERT_TEMPLATES = [
  { severity: 'critical', title: 'Ciprofloxacin-Resistant E. coli Surge', drug: 'Ciprofloxacin' },
  { severity: 'critical', title: 'Carbapenem Resistance Detected', drug: 'Meropenem' },
  { severity: 'critical', title: 'MRSA Cluster Identified', drug: 'Penicillin' },
  { severity: 'high', title: 'ESBL-Producing K. pneumoniae Alert', drug: 'Ceftriaxone' },
  { severity: 'high', title: 'Azithromycin Treatment Failure', drug: 'Azithromycin' },
  { severity: 'high', title: 'MDR Pseudomonas in ICU', drug: 'Gentamicin' },
  { severity: 'medium', title: 'Rising Amoxicillin Resistance', drug: 'Amoxicillin' },
  { severity: 'medium', title: 'Doxycycline Resistance Pattern', drug: 'Doxycycline' },
];

function weightedRandom(pool, key = 'weight') {
  const total = pool.reduce((sum, item) => sum + item[key], 0);
  let rand = Math.random() * total;
  for (const item of pool) {
    rand -= item[key];
    if (rand <= 0) return item;
  }
  return pool[pool.length - 1];
}

function randomId() {
  return Math.random().toString(36).slice(2, 8);
}

function randomAge() {
  return Math.floor(Math.random() * 75) + 1;
}

function randomSex() {
  return Math.random() > 0.5 ? 'male' : 'female';
}

class LiveDataEngine {
  constructor() {
    this.running = false;
    this.caseCount = 250; // matches initial demo data
    this.alertCount = 10;
    this.caseWeekCount = 47;
    this.intervalId = null;
  }

  start() {
    if (this.running) return;
    this.running = true;

    // Show LIVE badge
    const badge = document.getElementById('live-badge');
    if (badge) badge.classList.add('visible');

    // First case after 3s delay
    setTimeout(() => this.tick(), 3000);
  }

  stop() {
    this.running = false;
    if (this.intervalId) clearTimeout(this.intervalId);
    const badge = document.getElementById('live-badge');
    if (badge) badge.classList.remove('visible');
  }

  tick() {
    if (!this.running) return;

    // Generate new case
    this.emitCase();

    // ~30% chance of alert
    if (Math.random() < 0.3) {
      setTimeout(() => this.emitAlert(), 500 + Math.random() * 1000);
    }

    // Update stats
    this.emitStatsUpdate();

    // Schedule next tick (8-15s)
    const delay = 8000 + Math.random() * 7000;
    this.intervalId = setTimeout(() => this.tick(), delay);
  }

  emitCase() {
    this.caseCount++;
    this.caseWeekCount++;
    const district = weightedRandom(DISTRICT_WEIGHTS, 'weight').district;
    const source = weightedRandom(SOURCE_WEIGHTS, 'weight').source;
    const severity = weightedRandom(SEVERITY_WEIGHTS, 'weight').severity;

    const detail = {
      case_id: randomId(),
      source,
      complaint: COMPLAINT_POOL[Math.floor(Math.random() * COMPLAINT_POOL.length)],
      district,
      severity,
      age: randomAge(),
      sex: randomSex(),
      time: 'just now',
    };

    window.dispatchEvent(new CustomEvent('case:new', { detail }));
  }

  emitAlert() {
    this.alertCount++;
    const template = ALERT_TEMPLATES[Math.floor(Math.random() * ALERT_TEMPLATES.length)];
    const district = weightedRandom(DISTRICT_WEIGHTS, 'weight').district;

    const detail = {
      severity: template.severity,
      title: template.title,
      message: `${district}: New resistance pattern detected. ${template.drug} showing decreased efficacy.`,
      district,
      drug: template.drug,
      time: 'just now',
    };

    window.dispatchEvent(new CustomEvent('alert:new', { detail }));
  }

  emitStatsUpdate() {
    window.dispatchEvent(new CustomEvent('stats:update', {
      detail: {
        total_cases: this.caseCount,
        active_alerts: this.alertCount,
        cases_this_week: this.caseWeekCount,
      }
    }));
  }
}

const liveEngine = new LiveDataEngine();
```

- [ ] **Step 2: Verify**

Open browser console. Type `liveEngine.start()` — should see console events. LIVE badge appears. No crashes.

- [ ] **Step 3: Commit**

```bash
git add frontend/index.html
git commit -m "feat: add LiveDataEngine with data pools"
```

---

### Task 3: UI Reactions — Cases, Alerts, Stats, Orb

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: Add case:new listener**

Append to `<script>` after the LiveDataEngine:

```javascript
/* ═══════════════════════════════════════════════════════════
   UI REACTIONS — Event Listeners
   ═══════════════════════════════════════════════════════════ */

// ── Case: New ──
window.addEventListener('case:new', (e) => {
  const c = e.detail;
  const tbody = document.getElementById('cases-body');
  if (!tbody) return;

  const row = document.createElement('tr');
  row.className = 'case-row-new';
  row.innerHTML = `
    <td><span class="case-id">${c.case_id}</span></td>
    <td><span class="source-badge ${c.source}">${c.source}</span></td>
    <td><span class="complaint-text">${c.complaint}</span></td>
    <td class="hide-mobile"><span class="district-tag">${c.district}</span></td>
    <td class="hide-mobile">
      <span class="severity-badge">
        <span class="severity-dot ${c.severity}"></span>
        ${c.severity}
      </span>
    </td>
    <td class="hide-mobile" style="font-size:11px;color:var(--text-dim)">${c.age}y ${c.sex === 'male' ? 'M' : 'F'}</td>
    <td><span class="time-ago">${c.time}</span></td>
  `;

  // Insert at top
  tbody.insertBefore(row, tbody.firstChild);

  // Glow effect
  row.classList.add('case-row-glow');
  setTimeout(() => row.classList.remove('case-row-glow'), 2000);

  // Remove oldest if > 15
  while (tbody.children.length > 15) {
    tbody.removeChild(tbody.lastChild);
  }

  // Orb pulse
  const orb = document.getElementById('orb');
  if (orb) {
    orb.classList.add('orb-case-pulse');
    setTimeout(() => orb.classList.remove('orb-case-pulse'), 500);
  }
});

// ── Alert: New ──
window.addEventListener('alert:new', (e) => {
  const a = e.detail;
  const grid = document.getElementById('alerts-grid');
  if (!grid) return;

  const card = document.createElement('div');
  card.className = `alert-card glass ${a.severity} alert-card-new`;
  card.innerHTML = `
    <div class="alert-header">
      <div class="alert-dot"></div>
      <div class="alert-title">${a.title}</div>
    </div>
    <div class="alert-message">${a.message}</div>
    <div class="alert-meta">
      <span class="alert-tag">${a.district}</span>
      <span class="alert-tag">${a.drug}</span>
      <span class="alert-time">${a.time}</span>
    </div>
  `;

  // Insert at top
  grid.insertBefore(card, grid.firstChild);

  // Glow effect
  card.classList.add('alert-card-glow');
  setTimeout(() => card.classList.remove('alert-card-glow'), 2000);

  // Remove oldest if > 12
  while (grid.children.length > 12) {
    grid.removeChild(grid.lastChild);
  }

  // Orb reaction
  const orb = document.getElementById('orb');
  if (orb) {
    if (a.severity === 'critical') {
      orb.classList.add('orb-alert-red');
      setTimeout(() => orb.classList.remove('orb-alert-red'), 700);

      // Show banner
      showAlertBanner(a);
    } else {
      orb.classList.add('orb-alert-amber');
      setTimeout(() => orb.classList.remove('orb-alert-amber'), 3000);
    }
  }
});

// ── Stats: Update ──
window.addEventListener('stats:update', (e) => {
  const stats = e.detail;

  // Find stat cards by their labels
  const statCards = document.querySelectorAll('.stat-card');
  statCards.forEach(card => {
    const label = card.querySelector('.stat-label');
    const value = card.querySelector('.stat-value');
    if (!label || !value) return;

    if (label.textContent.includes('Cases Reported')) {
      animateCounter(value, stats.total_cases);
      value.classList.add('stat-flash');
      setTimeout(() => value.classList.remove('stat-flash'), 700);
    }
    if (label.textContent.includes('Active Alerts')) {
      animateCounter(value, stats.active_alerts);
      value.classList.add('stat-flash-red');
      setTimeout(() => value.classList.remove('stat-flash-red'), 700);
    }
  });
});

// ── Alert Banner ──
function showAlertBanner(alert) {
  const container = document.getElementById('alert-banner-container');
  if (!container) return;

  const banner = document.createElement('div');
  banner.className = 'alert-banner';
  banner.innerHTML = `
    <span class="alert-banner-dot"></span>
    <span class="alert-banner-text"><strong>${alert.title}</strong> — ${alert.district}: ${alert.drug}</span>
    <button class="alert-banner-dismiss" onclick="this.parentElement.classList.add('dismissing'); setTimeout(() => this.parentElement.remove(), 300)">&times;</button>
  `;

  container.appendChild(banner);

  // Auto-dismiss after 5s
  setTimeout(() => {
    if (banner.parentElement) {
      banner.classList.add('dismissing');
      setTimeout(() => banner.remove(), 300);
    }
  }, 5000);

  // Max 3 banners
  while (container.children.length > 3) {
    container.removeChild(container.firstChild);
  }
}

// ── Parallax Tilt ──
function initParallaxTilt() {
  const isTouchDevice = 'ontouchstart' in window;
  if (isTouchDevice) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reducedMotion) return;

  const tiltCards = document.querySelectorAll('.stat-card, .alert-card');
  tiltCards.forEach(card => {
    card.classList.add('parallax-tilt');

    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      card.style.transform = `perspective(800px) rotateY(${x * 5}deg) rotateX(${-y * 5}deg)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(800px) rotateY(0) rotateX(0)';
    });
  });
}
```

- [ ] **Step 2: Wire up init**

Modify the `// ── Init everything ──` block at the bottom of `<script>` to include:

```javascript
document.addEventListener('DOMContentLoaded', () => {
  renderAlerts();
  renderCases();
  renderResistanceBars();
  initMap();
  initTrendChart();
  initParallaxTilt();
  liveEngine.start();
});
```

- [ ] **Step 3: Verify**

Open in browser. After 3s:
- LIVE badge appears top-left
- Cases table gets new rows sliding in from left with teal glow
- Alert cards slide in from right
- Critical alerts show red banner at top (auto-dismisses in 5s)
- Stats tick up with flash animation
- Orb pulses teal on new case, turns amber/red on alerts
- Stat cards tilt on mouse hover

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html
git commit -m "feat: add live data UI reactions and parallax tilt"
```

---

### Task 4: Deploy v0.3

**Files:**
- No new files

- [ ] **Step 1: Tag v0.3**

```bash
git tag -a v0.3 -m "STAI v0.3 — live data simulation + parallax polish"
```

- [ ] **Step 2: Push**

```bash
git push origin master --tags
```

- [ ] **Step 3: Verify deploy**

```bash
gh workflow run deploy.yml --repo teaminnovatorx/week02-demo
```

Wait for success, then verify:
```bash
curl -sI https://teaminnovatorx.github.io/week02-demo/ | head -3
```

Expected: HTTP/2 200

- [ ] **Step 4: Final commit count**

```bash
git log --oneline | wc -l
```

Expected: 20+ commits
