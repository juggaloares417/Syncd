const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(data?.detail || `Request failed: ${response.status}`);
  }

  return data;
}

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const SyncdApi = {
  getMvpStatus: () => request('/api/v1/meta/mvp-status'),
  register: (payload) =>
    request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  login: (email, password) =>
    request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  getCurrentProfile: (token) =>
    request('/api/v1/profile/me', {
      headers: authHeaders(token),
    }),
  getDiscovery: (token) =>
    request('/api/v1/discovery', {
      headers: authHeaders(token),
    }),
  swipe: (token, payload) =>
    request('/api/v1/discovery/swipe', {
      method: 'POST',
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    }),
  getMatches: (token) =>
    request('/api/v1/matches', {
      headers: authHeaders(token),
    }),
  getMessages: (token, matchId) =>
    request(`/api/v1/chats/${matchId}`, {
      headers: authHeaders(token),
    }),
  sendMessage: (token, matchId, payload) =>
    request(`/api/v1/chats/${matchId}`, {
      method: 'POST',
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    }),
  getKaraokeRooms: (token) =>
    request('/api/v1/events/karaoke-rooms', {
      headers: authHeaders(token),
    }),
  getKaraokeRoom: (token, roomId) =>
    request(`/api/v1/events/karaoke-rooms/${roomId}`, {
      headers: authHeaders(token),
    }),
  joinRoom: (token, roomId) =>
    request(`/api/v1/events/karaoke-rooms/${roomId}/join`, {
      method: 'POST',
      headers: authHeaders(token),
    }),
  startRound: (token, roomId) =>
    request(`/api/v1/events/karaoke-rooms/${roomId}/start-round`, {
      method: 'POST',
      headers: authHeaders(token),
    }),
  voteRound: (token, roundId, payload) =>
    request(`/api/v1/events/karaoke-rounds/${roundId}/vote`, {
      method: 'POST',
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    }),
  getBilling: (token) =>
    request('/api/v1/billing/me', {
      headers: authHeaders(token),
    }),
  purchaseCredits: (token, credits) =>
    request('/api/v1/billing/credits/purchase', {
      method: 'POST',
      headers: authHeaders(token),
      body: JSON.stringify({ credits }),
    }),
  setSubscription: (token, plan) =>
    request('/api/v1/billing/subscription', {
      method: 'POST',
      headers: authHeaders(token),
      body: JSON.stringify({ plan }),
    }),
};
