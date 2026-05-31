# STAI v0.3 — Live Data Simulation Design Spec

## Overview

Upgrade the STAI cinematic dashboard with a live data simulation engine that makes the dashboard feel alive. Cases appear in real-time, alerts flash, stats tick, and the Orb reacts. This is a "visual treat" enhancement for demo/investor impact.

**Baseline:** v1.0 tagged commit (cinematic scrollytelling, 9 sections, Living Orb, D3 map, Chart.js)
**Target:** v0.3 — same file, enhanced with live simulation + subtle parallax polish

---

## Feature 1: Live Data Engine

### Architecture

A `LiveDataEngine` class that generates realistic AMR data on random intervals.

```
LiveDataEngine
  ├── start()        — begins simulation loop
  ├── stop()         — pauses simulation
  ├── onTick()       — generates new case or alert
  └── emit(event)    — dispatches custom DOM events
```

### Events

| Event | Payload | Trigger |
|-------|---------|---------|
| `case:new` | `{ case_id, source, complaint, district, severity, age, sex, time }` | Every 8-15s |
| `alert:new` | `{ severity, title, message, district, drug, time }` | ~30% chance per tick |
| `stats:update` | `{ total_cases, active_alerts, cases_this_week }` | After each case/alert |

### Data Pools

- **Complaints:** 30+ realistic AMR symptom descriptions
- **Districts:** Weighted by population (Lagos 15%, Nairobi 12%, Accra 10%, others distributed)
- **Sources:** telegram 40%, whatsapp 30%, ussd 15%, sms 10%, manual 5%
- **Severities:** moderate 60%, mild 25%, severe 10%, critical 5%
- **Age/Sex:** Random realistic ranges

### Timing

- Case interval: 8-15 seconds (random)
- Alert burst: ~30% chance per case tick
- First case appears after 3s delay (let page load)

---

## Feature 2: UI Reactions

### Cases Section

- New case row slides in from left (`translateX(-20px)` → `0`, 0.5s spring)
- Teal glow border (`box-shadow: 0 0 12px rgba(0,240,255,0.3)`) fades after 2s
- Source badge pulses once on arrival
- Max 15 visible rows; oldest fades out when new arrives

### Alerts Section

- New alert card slides in from right (`translateX(20px)` → `0`, 0.5s spring)
- Severity-colored left border glows on arrival
- Critical alerts trigger a full-width banner at page top:
  - Red background, white text, dismissable (X button)
  - Shows for 5s then auto-dismisses
  - Stacks if multiple criticals arrive

### Stats (Crisis Section)

- Total cases: smooth increment with spring animation (reuses `animateCounter`)
- Cases this week: increments + brief flash
- Active alerts: increments + red flash on new alert

### The Orb

| Event | Orb Reaction |
|-------|-------------|
| New case | Brief teal pulse (scale 1.0→1.12→1.0, 0.4s) |
| New alert (non-critical) | Turns amber for 3s |
| Critical alert | Turns red, scale 1.0→1.2→1.0, 0.6s |
| Idle | Normal breathing (existing) |

### LIVE Badge

- Fixed position: top-left (16px, 16px)
- Small pill: green pulsing dot + "LIVE" text
- `font-family: var(--font-mono)`, 10px, uppercase
- Z-index: 9999 (same as Orb)
- Subtle, never distracting

---

## Feature 3: Subtle Parallax Polish

### Stat Cards + Alert Cards

- On mouse hover: card tilts toward cursor (max 5deg)
- Uses `transform: perspective(800px) rotateX(Xdeg) rotateY(Ydeg)`
- Smooth transition (0.2s ease-out)
- Reset on mouse leave (spring back to flat)
- Glint effect: subtle highlight that follows cursor position

### Implementation

```javascript
card.addEventListener('mousemove', (e) => {
  const rect = card.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width - 0.5;
  const y = (e.clientY - rect.top) / rect.height - 0.5;
  card.style.transform = `perspective(800px) rotateY(${x * 5}deg) rotateX(${-y * 5}deg)`;
});
card.addEventListener('mouseleave', () => {
  card.style.transform = 'perspective(800px) rotateY(0) rotateX(0)';
});
```

---

## Technical Constraints

- Single file modification: `frontend/index.html`
- No new CDN dependencies
- All CSS additions append to existing `<style>` block
- All JS additions append to existing `<script>` block
- Maintains reduced-motion support (disable parallax + live animations)
- Maintains responsive design (disable parallax on touch devices)
- Performance: requestAnimationFrame for parallax, setInterval for data engine

---

## Success Criteria

1. New cases appear every 8-15s with smooth animation
2. Alerts flash with severity-colored borders
3. Critical alerts show banner at page top
4. Stats tick up reactively
5. Orb reacts to data events
6. LIVE badge visible but not distracting
7. Cards tilt on hover with smooth parallax
8. No performance degradation (60fps maintained)
9. Reduced-motion mode disables all live animations
10. Works on mobile (parallax disabled on touch)
