# MyAstroBoard - Roadmap

This document describes features that could potentially be integrated into MyAstroBoard. There are no guarantees; consider this file a list of ideas that may evolve based on my own ideas or future discussions.

---

## Recently Shipped

Features delivered in the **v0.7 – v0.8** cycle:

| Feature | Version |
|---------|---------|
| In-app notifications (N1–N7 triggers, per-user prefs, lead-time selectors) | 0.8.x |
| Web Push infrastructure (VAPID, push_manager, push_scheduler, SW handler) | 0.8.x |
| Seeing forecast integration in Plan My Night | 0.8.x |
| Exposure Calculator | 0.8.x |
| Moon calendar API + frontend | 0.8.x |
| IERS data caching and auto-update | 0.8.x |
| i18n expanded to 6 languages (EN, FR, ES, DE, IT, PT) | 0.7–0.8 |
| PWA service worker + app shell cache | 0.7–0.8 |
| Telescope selector UI in Plan My Night | 0.8.1 |
| CSV export normalization | 0.8.1 |

---

## 🗓️ Release Plan

### v0.9 — Close Web Push + Stabilize

**Objective:** Ship the one half-done feature before declaring stability.

The Web Push infrastructure (VAPID keys, `push_manager.py`, `push_scheduler.py`, API routes, SW handler) is fully built. What remains is end-to-end hardware validation.

- Complete VAPID Web Push E2E test on Android (Chrome) and iOS (Safari)
- Verify notifications fire correctly when the tab is closed — the main nighttime value
- Finalize `VAPID_CONTACT_EMAIL` requirement and document it in `1.INSTALLATION.md`

**Exit criteria:** push notification received on a real Android and iOS device; no open P1 bugs; CHANGELOG_NEXT empty.

---

### v1.0 — First Stable Release

**Objective:** A clean, self-hostable release that a new user can install and use in under 15 minutes.

- Docker `docker compose up` → usable without manual steps
- All 6 i18n languages at 0 missing keys (`python scripts/validate_i18n.py` passes clean)
- API routes stabilized — no breaking route changes after this point
- Documentation reviewed: `1.INSTALLATION.md`, `docs/` up to date

**Exit criteria:** clean install verified; CI passing; i18n 0 missing keys; no known P1/P2 bugs.

---

### v1.1 and beyond — New Features

#### v1.1 — Multi-location Profiles

| | |
|---|---|
| **Why** | Observers travel to dark sites; location drives every calculation (Plan My Night, Sky Tonight, aurora, horizon, etc.) |
| **Effort** | Medium |

What needs to be built:

- **Location presets** — per-user list of saved locations (name, lat/lon, elevation, timezone, horizon profile)
- **Location switcher** — quick selector in the navbar or settings; drives all active calculations
- **Backend extension** — extend existing location config in `auth.py` / `config_defaults.py`; no new storage module needed
- **Horizon profile per location** — associate a custom horizon with each preset
- **i18n** in 6 languages

---

#### v1.2 — Observation Log

| | |
|---|---|
| **Why** | Closes the loop: **Plan → Observe → Log → Astrodex** |
| **Effort** | High |

Users can record what they actually captured after a session, not just what they planned.

What needs to be built from scratch:

- **Session concept** — date, observing site, equipment combo, start/end time, sky conditions (SQM, seeing, transparency)
- **Per-target entries** — actual frame count, integration time, notes, rating (1–5), link to Astrodex
- **New backend module** (`observation_sessions.py`) with per-user JSON storage, same pattern as `astrodex.py`
- **Import from plan** — one-click to seed a session from tonight's Plan My Night targets
- **New frontend** — session list, session detail, entry editor, i18n in 6 languages

The equipment and object models (Equipment, Astrodex) are reusable as references, but the session and entry data model is entirely new. This is a full feature, not an incremental one.
