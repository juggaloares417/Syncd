# Music Identity and Matching System

## Core Rule
Music identity is a first-class system across:
- onboarding
- profile building
- matching
- discovery
- Mic Match
- chat prompts
- event recommendations

## Ways users define music taste
1. Manual entry
2. Streaming-service import
3. Combination of both

Manual choices should be allowed to override imported data.

## User Music Profile
Each user should store:
- favorite artists
- favorite songs
- favorite albums
- favorite genres
- current anthem
- breakup anthem
- green flag song
- red flag song
- karaoke anthem
- dream duet song
- mood tags

## Mood Tag Examples
- emo
- country
- rap
- pop
- rock
- sad songs
- villain energy
- soft romantic
- chaotic
- old soul
- alt
- party energy
- hopeless romantic
- late night drive
- gym rage
- nostalgia

## Connected Music Services
Architecture should support provider adapters for:
- Spotify
- Apple Music
- Amazon Music
- YouTube / YouTube playlists
- Pandora
- Deezer
- others later

## Music Connector Requirements
Each provider adapter should support where available:
- OAuth
- provider user id
- access token
- refresh token
- expiry tracking
- scopes
- top artists
- top songs
- playlists
- favorites/library if available
- sync timestamps
- reconnect flow

## Normalization Layer
Normalize imported data into:
- artists
- tracks
- albums
- genres
- playlists
- rankings
- recency score
- confidence score

## Vibe Sync Algorithm
Inputs:
- shared artists
- shared songs
- shared genres
- mood tag overlap
- anthem similarity
- karaoke overlap
- recency weighting
- complement bonus

Output:
- score from 0 to 100
- explanation chips

Example explanation chips:
- Shared artists
- Same late-night energy
- Strong karaoke match
- Same breakup anthem mood
