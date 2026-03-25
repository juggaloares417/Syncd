import React, { useEffect, useMemo, useState } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { SyncdApi } from './src/api';

const tabs = ['Home', 'Discovery', 'Karaoke', 'Matches', 'Profile', 'Billing'];

function SectionTitle({ title, subtitle }) {
  return (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {subtitle ? <Text style={styles.sectionSubtitle}>{subtitle}</Text> : null}
    </View>
  );
}

function Pill({ label, active = false }) {
  return (
    <View style={[styles.pill, active && styles.pillActive]}>
      <Text style={[styles.pillText, active && styles.pillTextActive]}>{label}</Text>
    </View>
  );
}

function ApiState({ loading, error }) {
  if (loading) {
    return <Text style={styles.helperText}>Loading live data...</Text>;
  }
  if (error) {
    return <Text style={styles.errorText}>{error}</Text>;
  }
  return null;
}

function AuthScreen({ email, password, setEmail, setPassword, onLogin, onRegister, loading, error }) {
  return (
    <View style={styles.authWrap}>
      <Text style={styles.logo}>Syncd</Text>
      <Text style={styles.authSubtitle}>Live API login. Seed account: steven@syncd.local / syncd123</Text>

      <TextInput
        value={email}
        onChangeText={setEmail}
        placeholder="Email"
        placeholderTextColor="#94a3b8"
        style={styles.input}
        autoCapitalize="none"
      />
      <TextInput
        value={password}
        onChangeText={setPassword}
        placeholder="Password"
        placeholderTextColor="#94a3b8"
        style={styles.input}
        secureTextEntry
      />

      <TouchableOpacity style={styles.actionButton} onPress={onLogin} disabled={loading}>
        <Text style={styles.actionButtonText}>{loading ? 'Signing in...' : 'Login'}</Text>
      </TouchableOpacity>

      <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]} onPress={onRegister} disabled={loading}>
        <Text style={styles.secondaryButtonText}>Quick register with current values</Text>
      </TouchableOpacity>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}
    </View>
  );
}

function HomeScreen({ me, status }) {
  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <View style={styles.heroCard}>
        <Text style={styles.eyebrow}>SYNCD LIVE MVP</Text>
        <Text style={styles.heroTitle}>Music chemistry first. Real backend. No fake data.</Text>
        <Text style={styles.heroBody}>
          This client is reading the live FastAPI backend and persisted SQLite data for auth, discovery, matches,
          chat, karaoke, and billing.
        </Text>
        <View style={styles.rowWrap}>
          <Pill label={`Premium: ${me?.premium ? 'On' : 'Off'}`} active={!!me?.premium} />
          <Pill label={`${me?.credits ?? 0} credits`} />
          <Pill label={me?.city || 'Unknown city'} />
        </View>
      </View>

      <SectionTitle title="Current account" />
      <View style={styles.card}>
        <Text style={styles.profileName}>{me?.display_name || 'Unknown user'}</Text>
        <Text style={styles.profileMeta}>{me?.email}</Text>
        <Text style={styles.profileBio}>{me?.bio}</Text>
      </View>

      <SectionTitle title="Backend status" />
      <View style={styles.card}>
        <Text style={styles.profileReason}>{status?.stage || 'Unknown stage'}</Text>
        <Text style={styles.profileBio}>Next priority: {status?.next_priority || 'Unknown'}</Text>
      </View>
    </ScrollView>
  );
}

function DiscoveryScreen({ discovery, onSwipe }) {
  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <SectionTitle title="Discovery" subtitle="Live discovery cards from the backend." />
      {discovery.map((card) => (
        <View key={card.user_id} style={styles.card}>
          <View style={styles.profileTopRow}>
            <View>
              <Text style={styles.profileName}>{card.display_name}, {card.age}</Text>
              <Text style={styles.profileMeta}>{card.city}</Text>
            </View>
            <View style={styles.scoreBadge}><Text style={styles.scoreText}>{card.compatibility_score}%</Text></View>
          </View>
          <Text style={styles.profileBio}>{card.bio}</Text>
          <Text style={styles.profileReason}>{card.compatibility_reason}</Text>
          <View style={styles.rowWrap}>
            {card.favorite_artists.map((artist) => <Pill key={artist} label={artist} />)}
          </View>
          <View style={styles.actionRow}>
            <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]} onPress={() => onSwipe(card.user_id, 'pass')}>
              <Text style={styles.secondaryButtonText}>Pass</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton} onPress={() => onSwipe(card.user_id, 'like')}>
              <Text style={styles.actionButtonText}>Like</Text>
            </TouchableOpacity>
          </View>
        </View>
      ))}
      {!discovery.length ? <Text style={styles.helperText}>No discovery cards left right now.</Text> : null}
    </ScrollView>
  );
}

function KaraokeScreen({ rooms, activeRoom, activeRound, onJoinRoom, onStartRound, onSelectRoom, onVote }) {
  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <SectionTitle title="Karaoke Roulette" subtitle="Live rooms and persisted rounds." />
      {rooms.map((room) => (
        <TouchableOpacity key={room.id} style={styles.card} onPress={() => onSelectRoom(room.id)}>
          <View style={styles.profileTopRow}>
            <View>
              <Text style={styles.roomTitle}>{room.title}</Text>
              <Text style={styles.profileMeta}>{room.theme}</Text>
            </View>
            {room.premium_only ? <Pill label="Premium" active /> : <Pill label="Open" />}
          </View>
          <Text style={styles.profileBio}>{room.description}</Text>
          <Text style={styles.profileMeta}>Round length: {room.round_seconds}s</Text>
          <View style={styles.actionRow}>
            <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]} onPress={() => onJoinRoom(room.id)}>
              <Text style={styles.secondaryButtonText}>Join room</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton} onPress={() => onStartRound(room.id)}>
              <Text style={styles.actionButtonText}>Start round</Text>
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      ))}

      {activeRoom ? (
        <View style={styles.card}>
          <SectionTitle title="Selected room detail" />
          <Text style={styles.profileName}>{activeRoom.title}</Text>
          <Text style={styles.profileMeta}>{activeRoom.active_participants} active participants</Text>
          <Text style={styles.profileBio}>{activeRoom.prompt}</Text>
        </View>
      ) : null}

      {activeRound ? (
        <View style={styles.card}>
          <SectionTitle title="Active round" subtitle="Live round state from backend." />
          <Text style={styles.profileName}>Partner: {activeRound.partner_display_name}</Text>
          <Text style={styles.profileMeta}>Ends at: {new Date(activeRound.ends_at).toLocaleString()}</Text>
          <Text style={styles.profileBio}>{activeRound.prompt}</Text>
          <View style={styles.actionRow}>
            <TouchableOpacity style={styles.actionButton} onPress={() => onVote(activeRound.id, { liked_vibe: true, romantic_vibe: true, same_music_taste: true, want_another_round: true })}>
              <Text style={styles.actionButtonText}>Romantic vibe</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]} onPress={() => onVote(activeRound.id, { liked_vibe: true, friend_vibe: true, same_music_taste: true, want_another_round: false })}>
              <Text style={styles.secondaryButtonText}>Friend vibe</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : null}
    </ScrollView>
  );
}

function MatchesScreen({ matches, activeMatchId, setActiveMatchId, messages, messageBody, setMessageBody, onSendMessage }) {
  const activeMatch = matches.find((item) => item.id === activeMatchId);

  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <SectionTitle title="Matches" subtitle="Persisted mutual matches and real chat." />
      {matches.map((match) => (
        <TouchableOpacity key={match.id} style={styles.card} onPress={() => setActiveMatchId(match.id)}>
          <View style={styles.profileTopRow}>
            <View>
              <Text style={styles.profileName}>{match.other_display_name}</Text>
              <Text style={styles.profileMeta}>{match.source}</Text>
            </View>
            <View style={styles.scoreBadge}><Text style={styles.scoreText}>{match.compatibility_score}%</Text></View>
          </View>
        </TouchableOpacity>
      ))}
      {!matches.length ? <Text style={styles.helperText}>No matches yet. Like someone back or trigger one from a karaoke round.</Text> : null}

      {activeMatch ? (
        <View style={styles.card}>
          <SectionTitle title={`Chat with ${activeMatch.other_display_name}`} />
          <View style={styles.messageList}>
            {messages.map((message) => (
              <View key={message.id} style={styles.messageRow}>
                <Text style={styles.messageMeta}>User {message.sender_user_id}</Text>
                <Text style={styles.profileBio}>{message.body}</Text>
              </View>
            ))}
          </View>
          <TextInput
            value={messageBody}
            onChangeText={setMessageBody}
            placeholder="Send a message"
            placeholderTextColor="#94a3b8"
            style={styles.input}
          />
          <TouchableOpacity style={styles.actionButton} onPress={onSendMessage}>
            <Text style={styles.actionButtonText}>Send</Text>
          </TouchableOpacity>
        </View>
      ) : null}
    </ScrollView>
  );
}

function ProfileScreen({ me }) {
  const statRows = useMemo(() => [
    ['Name', me?.display_name || 'Unknown'],
    ['Age', String(me?.age || '')],
    ['City', me?.city || 'Unknown'],
    ['Credits', String(me?.credits || 0)],
    ['Work', me?.work || 'Unknown'],
    ['Kids', me?.kids || 'Unknown'],
  ], [me]);

  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <SectionTitle title="Profile" subtitle="Loaded from the live profile endpoint." />
      <View style={styles.card}>
        {statRows.map(([label, value]) => (
          <View key={label} style={styles.statRow}>
            <Text style={styles.statLabel}>{label}</Text>
            <Text style={styles.statValue}>{value}</Text>
          </View>
        ))}
        <Text style={styles.profileBio}>{me?.bio}</Text>
      </View>
      <SectionTitle title="Top artists" />
      <View style={styles.rowWrap}>
        {(me?.artists || []).map((artist) => <Pill key={artist.artist_name} label={artist.artist_name} active />)}
      </View>
    </ScrollView>
  );
}

function BillingScreen({ billing, onBuyCredits, onSetPlan }) {
  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <SectionTitle title="Billing" subtitle="Persisted credits and subscription state." />
      <View style={styles.card}>
        <Text style={styles.profileName}>Plan: {billing?.subscription_plan || 'free'}</Text>
        <Text style={styles.profileMeta}>Premium: {billing?.premium ? 'Yes' : 'No'}</Text>
        <Text style={styles.profileMeta}>Credits: {billing?.credits ?? 0}</Text>
        <View style={styles.actionRow}>
          <TouchableOpacity style={styles.actionButton} onPress={() => onBuyCredits(10)}>
            <Text style={styles.actionButtonText}>Buy 10 credits</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]} onPress={() => onSetPlan(billing?.premium ? 'free' : 'premium')}>
            <Text style={styles.secondaryButtonText}>{billing?.premium ? 'Switch to free' : 'Upgrade to premium'}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState('Home');
  const [email, setEmail] = useState('steven@syncd.local');
  const [password, setPassword] = useState('syncd123');
  const [token, setToken] = useState(null);
  const [me, setMe] = useState(null);
  const [status, setStatus] = useState(null);
  const [discovery, setDiscovery] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [matches, setMatches] = useState([]);
  const [billing, setBilling] = useState(null);
  const [activeRoom, setActiveRoom] = useState(null);
  const [activeRound, setActiveRound] = useState(null);
  const [activeMatchId, setActiveMatchId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageBody, setMessageBody] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function loadAll(nextToken = token) {
    if (!nextToken) return;
    setLoading(true);
    setError('');
    try {
      const [statusData, meData, discoveryData, roomsData, matchesData, billingData] = await Promise.all([
        SyncdApi.getMvpStatus(),
        SyncdApi.getCurrentProfile(nextToken),
        SyncdApi.getDiscovery(nextToken),
        SyncdApi.getKaraokeRooms(nextToken),
        SyncdApi.getMatches(nextToken),
        SyncdApi.getBilling(nextToken),
      ]);
      setStatus(statusData);
      setMe(meData);
      setDiscovery(discoveryData);
      setRooms(roomsData);
      setMatches(matchesData);
      setBilling(billingData);
      if (!activeMatchId && matchesData.length) {
        setActiveMatchId(matchesData[0].id);
      }
    } catch (err) {
      setError(err.message || 'Failed to load live data');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, [token]);

  useEffect(() => {
    async function loadMessages() {
      if (!token || !activeMatchId) return;
      try {
        const data = await SyncdApi.getMessages(token, activeMatchId);
        setMessages(data);
      } catch (err) {
        setError(err.message || 'Failed to load messages');
      }
    }
    loadMessages();
  }, [token, activeMatchId]);

  async function handleLogin() {
    setLoading(true);
    setError('');
    try {
      const response = await SyncdApi.login(email, password);
      setToken(response.token);
      setMe(response.user);
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister() {
    setLoading(true);
    setError('');
    try {
      const response = await SyncdApi.register({
        email,
        password,
        display_name: email.split('@')[0],
        age: 30,
        city: 'Alta Sierra, CA',
        interested_in: 'women',
        bio: 'Fresh Syncd account',
        work: 'Builder',
        kids: 'not specified',
      });
      setToken(response.token);
      setMe(response.user);
    } catch (err) {
      setError(err.message || 'Register failed');
    } finally {
      setLoading(false);
    }
  }

  async function handleSwipe(targetUserId, action) {
    try {
      await SyncdApi.swipe(token, { target_user_id: targetUserId, action, source: 'discovery' });
      await loadAll();
      setActiveTab('Matches');
    } catch (err) {
      setError(err.message || 'Swipe failed');
    }
  }

  async function handleSelectRoom(roomId) {
    try {
      const room = await SyncdApi.getKaraokeRoom(token, roomId);
      setActiveRoom(room);
    } catch (err) {
      setError(err.message || 'Failed to load room');
    }
  }

  async function handleJoinRoom(roomId) {
    try {
      await SyncdApi.joinRoom(token, roomId);
      await loadAll();
      await handleSelectRoom(roomId);
    } catch (err) {
      setError(err.message || 'Failed to join room');
    }
  }

  async function handleStartRound(roomId) {
    try {
      const round = await SyncdApi.startRound(token, roomId);
      setActiveRound(round);
      setActiveTab('Karaoke');
    } catch (err) {
      setError(err.message || 'Failed to start round');
    }
  }

  async function handleVote(roundId, payload) {
    try {
      const result = await SyncdApi.voteRound(token, roundId, payload);
      if (result.mutual_match_created) {
        await loadAll();
        setActiveTab('Matches');
      }
    } catch (err) {
      setError(err.message || 'Failed to submit round vote');
    }
  }

  async function handleSendMessage() {
    if (!messageBody.trim() || !activeMatchId) return;
    try {
      await SyncdApi.sendMessage(token, activeMatchId, { body: messageBody.trim() });
      setMessageBody('');
      const data = await SyncdApi.getMessages(token, activeMatchId);
      setMessages(data);
    } catch (err) {
      setError(err.message || 'Failed to send message');
    }
  }

  async function handleBuyCredits(credits) {
    try {
      const data = await SyncdApi.purchaseCredits(token, credits);
      setBilling(data);
      await loadAll();
    } catch (err) {
      setError(err.message || 'Failed to buy credits');
    }
  }

  async function handleSetPlan(plan) {
    try {
      const data = await SyncdApi.setSubscription(token, plan);
      setBilling(data);
      await loadAll();
    } catch (err) {
      setError(err.message || 'Failed to update subscription');
    }
  }

  if (!token) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" />
        <AuthScreen
          email={email}
          password={password}
          setEmail={setEmail}
          setPassword={setPassword}
          onLogin={handleLogin}
          onRegister={handleRegister}
          loading={loading}
          error={error}
        />
      </SafeAreaView>
    );
  }

  const content = {
    Home: <HomeScreen me={me} status={status} />,
    Discovery: <DiscoveryScreen discovery={discovery} onSwipe={handleSwipe} />,
    Karaoke: (
      <KaraokeScreen
        rooms={rooms}
        activeRoom={activeRoom}
        activeRound={activeRound}
        onJoinRoom={handleJoinRoom}
        onStartRound={handleStartRound}
        onSelectRoom={handleSelectRoom}
        onVote={handleVote}
      />
    ),
    Matches: (
      <MatchesScreen
        matches={matches}
        activeMatchId={activeMatchId}
        setActiveMatchId={setActiveMatchId}
        messages={messages}
        messageBody={messageBody}
        setMessageBody={setMessageBody}
        onSendMessage={handleSendMessage}
      />
    ),
    Profile: <ProfileScreen me={me} />,
    Billing: <BillingScreen billing={billing} onBuyCredits={handleBuyCredits} onSetPlan={handleSetPlan} />,
  }[activeTab];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <View style={styles.header}>
        <Text style={styles.logo}>Syncd</Text>
        <Text style={styles.headerSub}>Live API client</Text>
      </View>
      <View style={styles.tabBar}>
        {tabs.map((tab) => (
          <TouchableOpacity key={tab} onPress={() => setActiveTab(tab)} style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}>
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>{tab}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <ApiState loading={loading} error={error} />
      {content}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0b1020',
  },
  authWrap: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
    gap: 14,
    backgroundColor: '#0b1020',
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 8,
  },
  logo: {
    color: '#f8fafc',
    fontSize: 28,
    fontWeight: '800',
  },
  headerSub: {
    color: '#94a3b8',
    marginTop: 4,
    fontSize: 14,
  },
  authSubtitle: {
    color: '#94a3b8',
    marginBottom: 8,
    lineHeight: 20,
  },
  tabBar: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 12,
    paddingBottom: 8,
    gap: 8,
  },
  tabButton: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 999,
    backgroundColor: '#172036',
  },
  tabButtonActive: {
    backgroundColor: '#7c3aed',
  },
  tabText: {
    color: '#cbd5e1',
    fontWeight: '600',
  },
  tabTextActive: {
    color: '#ffffff',
  },
  screenContent: {
    padding: 16,
    paddingBottom: 40,
    gap: 16,
  },
  heroCard: {
    backgroundColor: '#11182b',
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    borderColor: '#23304d',
  },
  card: {
    backgroundColor: '#11182b',
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: '#23304d',
    gap: 12,
  },
  eyebrow: {
    color: '#a78bfa',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: 8,
  },
  heroTitle: {
    color: '#f8fafc',
    fontSize: 24,
    fontWeight: '800',
    lineHeight: 30,
  },
  heroBody: {
    color: '#cbd5e1',
    fontSize: 15,
    lineHeight: 22,
    marginTop: 10,
  },
  sectionHeader: {
    gap: 4,
  },
  sectionTitle: {
    color: '#f8fafc',
    fontSize: 20,
    fontWeight: '700',
  },
  sectionSubtitle: {
    color: '#94a3b8',
    fontSize: 13,
    lineHeight: 18,
  },
  rowWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  pill: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 999,
    backgroundColor: '#1e293b',
    borderWidth: 1,
    borderColor: '#334155',
  },
  pillActive: {
    backgroundColor: '#2e1065',
    borderColor: '#7c3aed',
  },
  pillText: {
    color: '#cbd5e1',
    fontSize: 12,
    fontWeight: '600',
  },
  pillTextActive: {
    color: '#f5f3ff',
  },
  profileTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 12,
  },
  profileName: {
    color: '#f8fafc',
    fontSize: 22,
    fontWeight: '800',
  },
  roomTitle: {
    color: '#f8fafc',
    fontSize: 20,
    fontWeight: '800',
  },
  profileMeta: {
    color: '#94a3b8',
    marginTop: 4,
    fontSize: 13,
  },
  profileBio: {
    color: '#e2e8f0',
    fontSize: 15,
    lineHeight: 21,
  },
  profileReason: {
    color: '#a78bfa',
    fontSize: 13,
    fontWeight: '600',
  },
  scoreBadge: {
    backgroundColor: '#1d4ed8',
    borderRadius: 999,
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  scoreText: {
    color: '#eff6ff',
    fontWeight: '800',
  },
  actionRow: {
    flexDirection: 'row',
    gap: 10,
  },
  actionButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 14,
    backgroundColor: '#7c3aed',
  },
  actionButtonText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 15,
  },
  secondaryButton: {
    backgroundColor: '#1e293b',
    borderWidth: 1,
    borderColor: '#334155',
  },
  secondaryButtonText: {
    color: '#e2e8f0',
    fontWeight: '700',
    fontSize: 15,
  },
  statRow: {
    borderBottomWidth: 1,
    borderBottomColor: '#24324f',
    paddingVertical: 12,
    gap: 4,
  },
  statLabel: {
    color: '#94a3b8',
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  statValue: {
    color: '#f8fafc',
    fontSize: 16,
    fontWeight: '600',
  },
  input: {
    borderWidth: 1,
    borderColor: '#334155',
    backgroundColor: '#11182b',
    color: '#f8fafc',
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  helperText: {
    color: '#94a3b8',
    paddingHorizontal: 16,
    paddingBottom: 8,
  },
  errorText: {
    color: '#fda4af',
    paddingHorizontal: 16,
    paddingBottom: 8,
  },
  messageList: {
    gap: 8,
  },
  messageRow: {
    borderRadius: 12,
    padding: 10,
    backgroundColor: '#1a2339',
  },
  messageMeta: {
    color: '#94a3b8',
    fontSize: 12,
    marginBottom: 4,
  },
});
