# Syncd

Syncd is a music-aware dating app MVP built around:

- music taste onboarding
- compatibility-based discovery
- match-only chat direction
- **Karaoke Roulette** live speed-dating rooms
- subscription and credits foundation

This repo now has a real first-pass app foundation instead of an empty shell:

- **FastAPI + SQLite backend** in `backend/app.py`
- **Expo mobile stub** in `mobile/App.js`
- product spec in `docs/PRODUCT_SPEC.md`

## What works in this starter

### Backend
- creates SQLite tables on startup
- seeds sample users, artist preferences, matches, and karaoke rooms
- returns discovery cards with compatibility scores
- returns seeded matches
- returns Karaoke Roulette room data
- returns a current profile

### Mobile
- renders a dark-theme Syncd stub
- tabs for Home, Discovery, Karaoke, Matches, Profile
- uses realistic MVP mock data matching the backend concept
- gives you something clean to open in VS Code and start extending

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/api/v1/meta/mvp-status`
- `http://127.0.0.1:8000/api/v1/discovery`
- `http://127.0.0.1:8000/api/v1/events/karaoke-rooms`

## Run the mobile app

```bash
cd mobile
npm install
npm run start
```

## Next thing to build

The repo foundation is here. The next serious step is:

1. add real like / pass API endpoints
2. create mutual matches when both sides like each other
3. replace mobile mock data with live API calls
4. add join-room / round-timer flow for Karaoke Roulette

## Current repo structure

```text
Syncd/
  README.md
  .gitignore
  docs/
    PRODUCT_SPEC.md
    uploads/
  backend/
    app.py
    requirements.txt
  mobile/
    App.js
    app.json
    babel.config.js
    package.json
```
