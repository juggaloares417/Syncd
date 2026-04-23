# Syncd Main App Feature Pack

This pack is **additive**. It does not require deleting the earlier MVP foundation.

## Added backend entrypoint

- `backend/app_main.py`

Run it with:

```bash
cd backend
uvicorn app_main:app --reload
```

## Added mobile entrypoints

- `mobile/src/mainApi.js`
- `mobile/src/MainApp.js`
- `mobile/App_main.js`

If you want this new client to become the active mobile entry, replace the existing `mobile/App.js` export with:

```js
import MainApp from './src/MainApp';
export default MainApp;
```

## What is really coded right now

### Backend
- auth register/login
- profile by username
- profile visibility model
- email hidden from public profiles
- public search defaults
- friends, followers, following split
- follow / friend request / block endpoints
- profile links
- provider connection scaffold including Pandora
- master playlist / liked playlist / user playlists
- drag-drop reorder API for playlists
- live sections and live rooms
- room detail endpoint
- moderator permissions
- silence / remove listener actions
- join queue for video requests
- saved room presets
- gift gallery and custom gift seed data
- fan club settings
- event creation and ticket terms
- new features page data
- coming soon page data
- billing explainer for where money is intended to go later

### Mobile
- tabs for Home, Search, New Features, Coming Soon, Live, Profile, Playlists
- public profile search
- profile preview by tapping a result
- follow / friend request / block actions
- live room list and room detail view
- queue request button
- demo buttons for silence/remove moderation actions
- profile sections for top songs, links, providers, fan club and ticket terms
- playlist, gift gallery, presets, and events views

## Still scaffolded / not truly finished

- real Spotify OAuth
- real Pandora OAuth
- image upload picker and storage
- autoplay audio playback in profile
- private audio/video calls
- real Stripe / Google Pay cashout routing
- host subscription billing enforcement
- feed posting system on profile pages

## Why this is split into a new entrypoint

You said not to wreck what already exists. So the safest move is:

- keep the older MVP intact
- add this larger main-app-first path beside it
- switch over only when ready
