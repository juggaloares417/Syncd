export function renderApp() {
  return `
    <div class="app-shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-badge">S</div>
          <div>
            <h1>Syncd</h1>
            <p>Music-first dating stub</p>
          </div>
        </div>
        <nav>
          <button class="nav-item active">Dashboard</button>
          <button class="nav-item">Profile</button>
          <button class="nav-item">Matches</button>
          <button class="nav-item">Chats</button>
          <button class="nav-item">Karaoke Roulette</button>
          <button class="nav-item">Subscription</button>
        </nav>
      </aside>
      <main class="main">
        <header class="hero card">
          <div>
            <span class="pill">Web Stub v0.1</span>
            <h2>Syncd is live as a browser stub now.</h2>
            <p>
              This is the web sidecar for the existing mobile scaffold. It gives you a fast,
              clickable place to shape discovery, matching, and Karaoke Roulette before wiring real services.
            </p>
          </div>
          <div class="hero-stats">
            <div class="stat card"><strong>12</strong><span>Mock matches</span></div>
            <div class="stat card"><strong>3</strong><span>Unread chats</span></div>
            <div class="stat card"><strong>4</strong><span>Live rooms</span></div>
          </div>
        </header>

        <section class="grid two-up">
          <article class="card">
            <h3>Discovery</h3>
            <p>Swipe/discovery stays primary. Search and filters come second.</p>
            <ul>
              <li>Music compatibility score</li>
              <li>Favorite artists and genres</li>
              <li>Intent and distance filters</li>
            </ul>
          </article>
          <article class="card">
            <h3>Karaoke Roulette MVP</h3>
            <p>Speed dating meets karaoke with short timed rounds and fast mutual ratings.</p>
            <ul>
              <li>20 to 30 second intro</li>
              <li>45 to 90 second karaoke or lyric challenge</li>
              <li>30 to 60 second mini chat</li>
              <li>Mutual vibe rating and rotate</li>
            </ul>
          </article>
        </section>

        <section class="grid two-up">
          <article class="card">
            <h3>Matches</h3>
            <div class="match-list">
              <div class="match-row"><span>Jade</span><span>92% music match</span></div>
              <div class="match-row"><span>Marcus</span><span>88% music match</span></div>
              <div class="match-row"><span>Nina</span><span>84% music match</span></div>
            </div>
          </article>
          <article class="card">
            <h3>Next build targets</h3>
            <ol>
              <li>Persist profile and onboarding locally</li>
              <li>Unify shared mock data between mobile and web</li>
              <li>Wire real auth</li>
              <li>Add backend matchmaking endpoints</li>
            </ol>
          </article>
        </section>
      </main>
    </div>
  `;
}
