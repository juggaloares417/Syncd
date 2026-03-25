const API_BASE_URL = 'http://localhost:8000';

export async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

export const SyncdApi = {
  getMvpStatus: () => fetchJson('/api/v1/meta/mvp-status'),
  getCurrentProfile: () => fetchJson('/api/v1/profile/me'),
  getDiscovery: () => fetchJson('/api/v1/discovery'),
  getMatches: () => fetchJson('/api/v1/matches'),
  getKaraokeRooms: () => fetchJson('/api/v1/events/karaoke-rooms'),
  getKaraokeRoom: (roomId) => fetchJson(`/api/v1/events/karaoke-rooms/${roomId}`),
};
