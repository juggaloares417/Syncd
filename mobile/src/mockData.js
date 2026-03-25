export const currentUser = {
  name: 'Steven',
  age: 37,
  city: 'Grass Valley, CA',
  premium: true,
  credits: 40,
  vibe: 'Builder by day. Music and chaos by night.',
  topArtists: ['Breaking Benjamin', 'DizzyIsDead', 'Matchbox Twenty'],
};

export const discoveryCards = [
  {
    id: 2,
    name: 'Luna',
    age: 31,
    city: 'Sacramento, CA',
    score: 91,
    bio: 'Alt girl, karaoke menace, and emotionally fluent when caffeinated.',
    artists: ['Paramore', 'Breaking Benjamin', 'Evanescence'],
    reason: '1 shared artist pick, 2 genre overlaps',
  },
  {
    id: 3,
    name: 'Jade',
    age: 29,
    city: 'Reno, NV',
    score: 64,
    bio: 'Country roads, loud choruses, dive bars, and a suspiciously competitive duet streak.',
    artists: ['Chris Stapleton', 'Jelly Roll', 'Lainey Wilson'],
    reason: 'Different playlists, but still worth a live vibe check',
  },
  {
    id: 4,
    name: 'Ivy',
    age: 33,
    city: 'San Jose, CA',
    score: 84,
    bio: 'Emo night forever. If your playlist has emotional damage, we should probably talk.',
    artists: ['My Chemical Romance', 'Paramore', 'Evanescence'],
    reason: '2 genre overlaps and strong live-room chemistry potential',
  },
];

export const karaokeRooms = [
  {
    id: 1,
    title: 'Emo Night',
    theme: 'emo night',
    premiumOnly: false,
    roundLength: '2m 30s',
    stages: ['25s intro', '60s chorus challenge', '45s mini chat', 'quick vibe vote'],
    description: 'Fast rounds for people whose playlists are mostly feelings and damage.',
  },
  {
    id: 2,
    title: 'Country Confessions',
    theme: 'country night',
    premiumOnly: false,
    roundLength: '2m 45s',
    stages: ['30s intro', '75s duet or chorus', '45s mini chat', 'quick vibe vote'],
    description: 'Boots, heartbreak, and duet bait.',
  },
  {
    id: 3,
    title: 'Toxic Ex Anthems',
    theme: 'premium room',
    premiumOnly: true,
    roundLength: '3m 00s',
    stages: ['20s intro', '90s anthem round', '45s mini chat', 'quick vibe vote'],
    description: 'Premium room for dramatic chorus energy and suspiciously specific song choices.',
  },
];

export const matches = [
  {
    id: 1,
    name: 'Luna',
    source: 'Karaoke Roulette',
    lastMessage: 'You better not dodge the Paramore duet next round.',
    score: 91,
  },
  {
    id: 2,
    name: 'Ivy',
    source: 'Discovery',
    lastMessage: 'Your playlist looks like therapy with guitars.',
    score: 84,
  },
];
