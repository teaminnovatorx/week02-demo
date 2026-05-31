# STAI Frontend — Cinematic Scrollytelling Design Spec

## Overview

STAI (Sentri Intelligence) is an AMR (Antimicrobial Resistance) surveillance platform that reports cases via Telegram, WhatsApp, and SMS, and visualizes resistance patterns across Africa in real-time.

This spec defines a complete frontend redesign: a cinematic scrollytelling experience that serves as both a launch showcase and a live interactive dashboard. The design is a single `index.html` file with embedded CSS/JS, using D3.js, Chart.js, and vanilla JavaScript. No frameworks.

**Name**: STAI (Sentri Intelligence)  
**Domain**: stai.is-a.software  
**Hosting**: GitHub Pages (static)  
**Data**: Embedded demo data with API fallback

---

## Visual Language

### Color System — Luxury Biotech

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-deep` | `#06090F` | Page background (warm deep navy) |
| `--bg-glass` | `rgba(255,255,255,0.04)` | Card backgrounds |
| `--aurora-1` | `#4ADE80` | Aurora gradient start (sage) |
| `--aurora-2` | `#2DD4BF` | Aurora gradient mid (teal) |
| `--aurora-3` | `#A78BFA` | Aurora gradient end (lavender) |
| `--accent` | `#00F0FF` | Data highlights, active states |
| `--amber` | `#F59E0B` | Warnings, medium severity |
| `--red` | `#EF4444` | Danger, critical alerts |
| `--text` | `#EEF0F4` | Primary text |
| `--text-dim` | `#949BA8` | Secondary text |
| `--text-muted` | `#5A6170` | Tertiary text |

Aurora gradients shift with CSS animations (8s cycle). Glow effects are subtle — candlelight, not laser. No harsh neon.

### Typography

| Role | Font | Weight | Size |
|------|------|--------|------|
| Display / Logo | **Syne** | 700-800 | 48-96px |
| Headings | **Syne** | 600-700 | 24-36px |
| Body | **Satoshi** | 400-500 | 14-16px |
| Data / Stats | **JetBrains Mono** | 500-600 | 12-14px |

Load from Google Fonts / CDN. Fallback: system fonts.

### Effects

- **Glassmorphism**: `backdrop-filter: blur(24px)` with `rgba(255,255,255,0.04)` background and 1px `rgba(255,255,255,0.06)` border
- **Grain overlay**: CSS noise texture at 3% opacity for depth
- **Aurora mesh**: Animated radial gradients behind key sections
- **Spring physics**: All animations use spring easing (no linear/ease). Custom `spring(t)` function with damping.
- **Scroll-triggered reveals**: `IntersectionObserver` triggers staggered entrances

---

## Page Structure — The Scroll Journey

Single continuous page. 9 sections. Total scroll: ~9 viewport heights.

### Section 0: Hero — "The Arrival" (0% scroll)

- Full viewport height
- STAI logo assembles from floating particles (canvas or CSS)
- Living Orb materializes center-screen with breath animation
- "Sentri Intelligence" fades in below logo (Syne 72px)
- Tagline: "Real-time antimicrobial resistance surveillance"
- Subtle aurora mesh background shifts with mouse movement
- Scroll indicator arrow pulses at bottom

### Section 1: The Crisis — "Silent Pandemic" (15% scroll)

- "1.27M" counter rolls up from 0 (JetBrains Mono, 96px)
- "deaths per year from drug-resistant infections" (Satoshi, 18px)
- 4 stat cards spring in staggered:
  - Cases reported: 250+
  - Districts covered: 15
  - Drugs tracked: 12
  - Alerts active: 10
- Orb dims, pulses amber in response
- Background shifts to warmer tone

### Section 2: The Vision — "See What Others Miss" (30% scroll)

- Large text reveals word by word with spring animation
- "STAI sees resistance before it spreads."
- Orb brightens, sends data tendrils (CSS animated lines)
- Background returns to cool aurora

### Section 3: How It Works — "3 Channels" (45% scroll)

- 3-column layout: Telegram / WhatsApp / SMS
- Each column has an icon + message bubble animation
- Messages flow INTO the Orb (animated path)
- Below: "Structured data OUT" — the Orb outputs case cards
- Animated pipeline: Input → Orb → Dashboard

### Section 4: Live Map — "Africa Under Watch" (60% scroll)

- Full-width D3.js map of Africa
- 15 district points glow with resistance data
- Color: resColor() based on resistance percentage
- Hover: district expands, tooltip shows drug breakdown
- Click: opens detail panel
- Arc connections pulse between outbreak-linked districts
- Orb hovers near map, stretches toward hovered district

### Section 5: Alerts — "Active Threats" (72% scroll)

- Alert cards slide in from left/right alternating
- Each card: severity indicator (pulsing dot), title, message, district, drug
- Critical = red glow, High = amber, Medium = cyan
- Orb flashes on critical alerts

### Section 6: Cases — "Field Reports" (82% scroll)

- Cases table with source badges (telegram, whatsapp, ussd, sms, manual)
- Rows animate in with stagger (50ms delay each)
- Columns: ID, Source, Complaint, District, Severity, Age/Sex, Time
- Severity dots with color coding
- Source badges with distinct styles

### Section 7: Resistance — "The Drug War" (90% scroll)

- Drug resistance bars fill with spring animation
- 12 drugs, sorted by resistance percentage
- Trend chart (Chart.js) draws itself line by line
- Drug selector dropdown for trend filtering
- Orb settles into calm breathing

### Section 8: Close — "Built for Africa" (100% scroll)

- "Built for Africa. Built for the world." (Syne, 48px)
- STAI logo + links
- Orb fades into the logo
- Footer with credits

---

## The Living Orb

### Properties

- **Shape**: Soft circle, 60px diameter
- **Colors**: Aurora gradient (sage → teal → lavender) animated
- **Position**: Fixed, bottom-right (24px from edges)
- **Z-index**: 9999 (always on top)

### Behaviors

| State | Animation |
|-------|-----------|
| Idle | Scale 1.0 → 1.08 → 1.0, 4s cycle. Aurora gradient shifts. |
| Hovered | Scale to 1.15, show "STAI" label |
| Near alerts | Pulse amber/red |
| Near map | Stretch toward hovered district |
| Critical alert | Flash red, brief scale 1.3 |
| Section transition | Shift color to match section mood |

### Technical

- CSS animation for breathing (transform: scale)
- JS for position reactions (map hover, section detection)
- `IntersectionObserver` for section detection
- Mouse tracking for aurora mesh parallax

---

## Dashboard Components

### Stat Cards (Hero Stats)

Glass cards with:
- Large number (JetBrains Mono, 36px)
- Label (Satoshi, 12px, muted)
- Change indicator (↑/↓ with color)
- Animated counter on scroll-in
- Subtle border glow on hover

### Map (D3.js)

- SVG-based Africa outline
- District points as glowing circles
- Size proportional to case count
- Color: resColor() gradient
- Arc connections with animated dash-offset
- Tooltip: district name, resistance %, top drug, case count
- Responsive: scales with container

### Alerts

Cards with:
- Severity dot (pulsing CSS animation)
- Title (Syne, 14px, bold)
- Message (Satoshi, 12px, dim)
- District tag + Drug tag
- Time ago
- Glass background with severity-colored left border

### Cases Table

- Sticky header
- Rows with hover highlight
- Source badges: colored pill (telegram=blue, whatsapp=green, ussd=amber, sms=purple, manual=gray)
- Severity: colored dot + text
- Time: relative ("2h ago")
- Responsive: hide columns on mobile

### Drug Resistance Bars

- Horizontal bars with gradient fill
- Spring animation on scroll-in
- Drug name left, percentage right
- Color: resistance level (green < 25% < cyan < 50% < amber < 75% < red)

### Trend Chart (Chart.js)

- Line chart, 30-day window
- Multiple lines (one per drug-district combo)
- Animated draw-on-scroll
- Dark grid, muted labels
- Hover: crosshair with values

---

## Demo Data

Embedded in frontend for GitHub Pages (no backend required). Falls back to API if available (2s timeout).

Data includes:
- 250 cases across 15 districts
- 10 active alerts (critical/high/medium)
- 12 drugs with resistance percentages
- 30-day trend data for 6 drug-district combos
- District geo-coordinates for map

---

## Technical Constraints

- **Single file**: `frontend/index.html` — all CSS/JS embedded
- **No build step**: Works directly on GitHub Pages
- **CDN dependencies**: D3.js v7, Chart.js v4, TopoJSON, Google Fonts
- **Responsive**: Mobile-first, breakpoints at 768px and 1024px
- **Performance**: Lazy-load below-fold sections, requestAnimationFrame for animations
- **Accessibility**: Reduced-motion media query disables animations, ARIA labels on interactive elements

---

## File Structure

```
frontend/
  index.html    ← Single file, all CSS/JS embedded
  CNAME         ← stai.is-a.software
```

---

## Success Criteria

1. Page loads in < 3s on 3G
2. Scroll is smooth 60fps throughout
3. Orb never blocks content or feels gimmicky
4. Dashboard is fully functional with demo data
5. Works on mobile (responsive)
6. Reduced-motion mode works
7. Passes Lighthouse accessibility > 80
