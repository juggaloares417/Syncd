import React, { useMemo, useState } from 'react';
import { SafeAreaView, ScrollView, StatusBar, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { currentUser, discoveryCards, karaokeRooms, matches } from './src/mockData';

const tabs = ['Home', 'Discovery', 'Karaoke', 'Matches', 'Profile'];

function Pill({ label, active = false }) {
  return (
    <View style={[styles.pill, active && styles.pillActive]}>
      <Text style={[styles.pillText, active && styles.pillTextActive]}>{label}</Text>
    </View>
  );
}

function SectionTitle({ title, subtitle }) {
  return (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {subtitle ? <Text style={styles.sectionSubtitle}>{subtitle}</Text> : null}
    </View>
  );
}

function HomeScreen() {
  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <View style={styles.heroCard}>
        <Text style={styles.eyebrow}>SYNCD MVP</Text>
        <Text style={styles.heroTitle}>Music chemistry first. Everything else second.</Text>
        <Text style={styles.heroBody}>
          Discovery, matches, and Karaoke Roulette are wired into the plan from day one so the app has an actual identity.
        </Text>
        <View style={styles.rowWrap}>
          <Pill label={`Premium: ${currentUser.premium ? 'On' : 'Off'}`} active />
          <Pill label={`${currentUser.credits} credits`} />
          <Pill label={currentUser.city} />
        </View>
      </View>

      <SectionTitle title="Build focus" subtitle="The first app gets finished by narrowing scope and shipping the spine." />
      <View style={styles.grid}>
        <View style={styles.infoCard}><Text style={styles.infoCardLabel}>Backend</Text><Text style={styles.infoCardValue}>FastAPI + SQLite</Text></View>
        <View style={styles.infoCard}><Text style={styles.infoCardLabel}>Frontend</Text><Text style={styles.infoCardValue}>Expo mobile-first</Text></View>
        <View style={styles.infoCard}><Text style={styles.infoCardLabel}>Core hook</Text><Text style={styles.infoCardValue}>Karaoke Roulette</Text></View>
        <View style={styles.infoCard}><Text style={styles.infoCardLabel}>Monetization</Text><Text style={styles.infoCardValue}>Premium + credits</Text></View>
      </View>

      <SectionTitle title="Top artists" subtitle="Pulled from the current profile seed." />
      <View style={styles.rowWrap}>
        {currentUser.topArtists.map((artist) => <Pill key={artist} label={artist} active />)}
      </View>
    </ScrollView>
  );
}

function DiscoveryScreen() {
  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <SectionTitle title="Discovery" subtitle="Music-aware matching with compatibility signals." />
      {discoveryCards.map((card) => (
        <View key={card.id} style={styles.profileCard}>
          <View style={styles.profileTopRow}>
            <View>
              <Text style={styles.profileName}>{card.name}, {card.age}</Text>
              <Text style={styles.profileMeta}>{card.city}</Text>
            </View>
            <View style={styles.scoreBadge}><Text style={styles.scoreText}>{card.score}%</Text></View>
          </View>
          <Text style={styles.profileBio}>{card.bio}</Text>
          <Text style={styles.profileReason}>{card.reason}</Text>
          <View style={styles.rowWrap}>
            {card.artists.map((artist) => <Pill key={artist} label={artist} />)}
          </View>
          <View style={styles.actionRow}>
            <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]}><Text style={styles.secondaryButtonText}>Pass</Text></TouchableOpacity>
            <TouchableOpacity style={styles.actionButton}><Text style={styles.actionButtonText}>Like</Text></TouchableOpacity>
          </View>
        </View>
      ))}
    </ScrollView>
  );
}

function KaraokeScreen() {
  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <SectionTitle title="Karaoke Roulette" subtitle="Speed dating meets music games." />
      {karaokeRooms.map((room) => (
        <View key={room.id} style={styles.roomCard}>
          <View style={styles.profileTopRow}>
            <View>
              <Text style={styles.roomTitle}>{room.title}</Text>
              <Text style={styles.profileMeta}>{room.theme}</Text>
            </View>
            {room.premiumOnly ? <Pill label="Premium" active /> : <Pill label="Open" />}
          </View>
          <Text style={styles.profileBio}>{room.description}</Text>
          <Text style={styles.roomLength}>Round length: {room.roundLength}</Text>
          <View style={styles.stageList}>
            {room.stages.map((stage) => <Text key={stage} style={styles.stageItem}>• {stage}</Text>)}
          </View>
          <View style={styles.actionRow}>
            <TouchableOpacity style={styles.actionButton}><Text style={styles.actionButtonText}>Join room</Text></TouchableOpacity>
          </View>
        </View>
      ))}
    </ScrollView>
  );
}

function MatchesScreen() {
  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <SectionTitle title="Matches" subtitle="Chat only unlocks after mutual interest." />
      {matches.map((match) => (
        <View key={match.id} style={styles.matchCard}>
          <View style={styles.profileTopRow}>
            <View>
              <Text style={styles.profileName}>{match.name}</Text>
              <Text style={styles.profileMeta}>{match.source}</Text>
            </View>
            <View style={styles.scoreBadge}><Text style={styles.scoreText}>{match.score}%</Text></View>
          </View>
          <Text style={styles.lastMessage}>{match.lastMessage}</Text>
          <TouchableOpacity style={styles.actionButton}><Text style={styles.actionButtonText}>Open chat</Text></TouchableOpacity>
        </View>
      ))}
    </ScrollView>
  );
}

function ProfileScreen() {
  const statRows = useMemo(() => [
    ['Name', currentUser.name],
    ['Age', String(currentUser.age)],
    ['City', currentUser.city],
    ['Credits', String(currentUser.credits)],
    ['Vibe', currentUser.vibe],
  ], []);

  return (
    <ScrollView contentContainerStyle={styles.screenContent}>
      <SectionTitle title="Profile" subtitle="Seeded MVP profile for the current user." />
      <View style={styles.profileCard}>
        {statRows.map(([label, value]) => (
          <View key={label} style={styles.statRow}>
            <Text style={styles.statLabel}>{label}</Text>
            <Text style={styles.statValue}>{value}</Text>
          </View>
        ))}
      </View>
      <SectionTitle title="Top artists" />
      <View style={styles.rowWrap}>
        {currentUser.topArtists.map((artist) => <Pill key={artist} label={artist} active />)}
      </View>
    </ScrollView>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState('Home');

  const content = {
    Home: <HomeScreen />,
    Discovery: <DiscoveryScreen />,
    Karaoke: <KaraokeScreen />,
    Matches: <MatchesScreen />,
    Profile: <ProfileScreen />,
  }[activeTab];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <View style={styles.header}>
        <Text style={styles.logo}>Syncd</Text>
        <Text style={styles.headerSub}>Music-aware dating MVP</Text>
      </View>
      <View style={styles.tabBar}>
        {tabs.map((tab) => (
          <TouchableOpacity key={tab} onPress={() => setActiveTab(tab)} style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}>
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>{tab}</Text>
          </TouchableOpacity>
        ))}
      </View>
      {content}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
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
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  infoCard: {
    width: '47%',
    backgroundColor: '#11182b',
    borderRadius: 18,
    padding: 14,
    borderWidth: 1,
    borderColor: '#23304d',
  },
  infoCardLabel: {
    color: '#94a3b8',
    fontSize: 12,
    marginBottom: 6,
  },
  infoCardValue: {
    color: '#f8fafc',
    fontWeight: '700',
    fontSize: 16,
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
  profileCard: {
    backgroundColor: '#11182b',
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: '#23304d',
    gap: 12,
  },
  roomCard: {
    backgroundColor: '#11182b',
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: '#23304d',
    gap: 12,
  },
  matchCard: {
    backgroundColor: '#11182b',
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: '#23304d',
    gap: 12,
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
  roomLength: {
    color: '#e2e8f0',
    fontWeight: '700',
  },
  stageList: {
    gap: 6,
  },
  stageItem: {
    color: '#cbd5e1',
    fontSize: 14,
  },
  lastMessage: {
    color: '#cbd5e1',
    fontSize: 15,
    lineHeight: 20,
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
});
