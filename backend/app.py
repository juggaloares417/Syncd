import hashlib
import secrets
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    or_,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DATABASE_URL = "sqlite:///./syncd.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(UTC)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return secrets.compare_digest(digest.hex(), digest_hex)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String(120))
    interested_in: Mapped[str] = mapped_column(String(120), default="women")
    bio: Mapped[str] = mapped_column(Text, default="")
    work: Mapped[str] = mapped_column(String(120), default="")
    kids: Mapped[str] = mapped_column(String(50), default="not specified")
    premium: Mapped[bool] = mapped_column(Boolean, default=False)
    credits: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    artists: Mapped[list["ArtistPreference"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class ArtistPreference(Base):
    __tablename__ = "artist_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    artist_name: Mapped[str] = mapped_column(String(120), index=True)
    genre: Mapped[str] = mapped_column(String(120), default="")
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    user: Mapped[User] = relationship(back_populates="artists")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Swipe(Base):
    __tablename__ = "swipes"
    __table_args__ = (UniqueConstraint("from_user_id", "to_user_id", name="uq_swipe_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_user_id: Mapped[int] = mapped_column(Integer, index=True)
    to_user_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(50), default="discovery")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("user_a_id", "user_b_id", name="uq_match_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_a_id: Mapped[int] = mapped_column(Integer, index=True)
    user_b_id: Mapped[int] = mapped_column(Integer, index=True)
    source: Mapped[str] = mapped_column(String(50), default="discovery")
    compatibility_score: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="matched")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    sender_user_id: Mapped[int] = mapped_column(Integer, index=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class KaraokeRoom(Base):
    __tablename__ = "karaoke_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(120))
    theme: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    premium_only: Mapped[bool] = mapped_column(Boolean, default=False)
    min_age: Mapped[int] = mapped_column(Integer, default=18)
    round_seconds: Mapped[int] = mapped_column(Integer, default=150)
    mode: Mapped[str] = mapped_column(String(50), default="voice-video-optional")


class KaraokeRoundTemplate(Base):
    __tablename__ = "karaoke_round_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("karaoke_rooms.id"), index=True)
    intro_seconds: Mapped[int] = mapped_column(Integer, default=30)
    performance_seconds: Mapped[int] = mapped_column(Integer, default=60)
    chat_seconds: Mapped[int] = mapped_column(Integer, default=45)
    prompt: Mapped[str] = mapped_column(Text, default="Sing a chorus or finish the lyric.")


class RoomParticipant(Base):
    __tablename__ = "room_participants"
    __table_args__ = (UniqueConstraint("room_id", "user_id", name="uq_room_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(Integer, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class KaraokeRound(Base):
    __tablename__ = "karaoke_rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(Integer, index=True)
    participant_a_id: Mapped[int] = mapped_column(Integer, index=True)
    participant_b_id: Mapped[int] = mapped_column(Integer, index=True)
    intro_seconds: Mapped[int] = mapped_column(Integer)
    performance_seconds: Mapped[int] = mapped_column(Integer)
    chat_seconds: Mapped[int] = mapped_column(Integer)
    prompt: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class KaraokeVote(Base):
    __tablename__ = "karaoke_votes"
    __table_args__ = (UniqueConstraint("round_id", "voter_user_id", name="uq_round_voter"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    round_id: Mapped[int] = mapped_column(Integer, index=True)
    voter_user_id: Mapped[int] = mapped_column(Integer, index=True)
    target_user_id: Mapped[int] = mapped_column(Integer, index=True)
    liked_vibe: Mapped[bool] = mapped_column(Boolean, default=False)
    friend_vibe: Mapped[bool] = mapped_column(Boolean, default=False)
    romantic_vibe: Mapped[bool] = mapped_column(Boolean, default=False)
    same_music_taste: Mapped[bool] = mapped_column(Boolean, default=False)
    want_another_round: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SubscriptionRecord(Base):
    __tablename__ = "subscription_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    status: Mapped[str] = mapped_column(String(50), default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CreditLedger(Base):
    __tablename__ = "credit_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    delta: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ArtistPreferenceOut(BaseModel):
    artist_name: str
    genre: str
    weight: float

    model_config = {"from_attributes": True}


class ProfileOut(BaseModel):
    id: int
    email: str
    display_name: str
    age: int
    city: str
    interested_in: str
    bio: str
    work: str
    kids: str
    premium: bool
    credits: int
    artists: list[ArtistPreferenceOut]

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)
    display_name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=18, le=99)
    city: str = Field(min_length=2, max_length=120)
    interested_in: str = Field(min_length=2, max_length=120)
    bio: str = Field(default="", max_length=500)
    work: str = Field(default="", max_length=120)
    kids: str = Field(default="not specified", max_length=50)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)


class AuthResponse(BaseModel):
    token: str
    expires_at: datetime
    user: ProfileOut


class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=18, le=99)
    city: str = Field(min_length=2, max_length=120)
    interested_in: str = Field(min_length=2, max_length=120)
    bio: str = Field(max_length=500)
    work: str = Field(max_length=120)
    kids: str = Field(max_length=50)


class DiscoveryCard(BaseModel):
    user_id: int
    display_name: str
    age: int
    city: str
    bio: str
    favorite_artists: list[str]
    genres: list[str]
    compatibility_score: int
    compatibility_reason: str


class SwipeRequest(BaseModel):
    target_user_id: int
    action: str = Field(pattern="^(like|pass)$")
    source: str = Field(default="discovery", max_length=50)


class SwipeResponse(BaseModel):
    ok: bool
    action: str
    created_match: bool
    match_id: int | None = None


class MatchOut(BaseModel):
    id: int
    other_user_id: int
    other_display_name: str
    source: str
    compatibility_score: int
    status: str


class ChatMessageOut(BaseModel):
    id: int
    sender_user_id: int
    body: str
    created_at: datetime


class ChatSendRequest(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class KaraokeRoomOut(BaseModel):
    id: int
    slug: str
    title: str
    theme: str
    description: str
    premium_only: bool
    min_age: int
    round_seconds: int
    mode: str

    model_config = {"from_attributes": True}


class KaraokeRoomDetail(KaraokeRoomOut):
    intro_seconds: int
    performance_seconds: int
    chat_seconds: int
    prompt: str
    active_participants: int


class KaraokeJoinResponse(BaseModel):
    room_id: int
    joined: bool
    credits_remaining: int
    active_participants: int


class KaraokeRoundOut(BaseModel):
    id: int
    room_id: int
    partner_user_id: int
    partner_display_name: str
    intro_seconds: int
    performance_seconds: int
    chat_seconds: int
    prompt: str
    status: str
    started_at: datetime
    ends_at: datetime


class KaraokeVoteRequest(BaseModel):
    liked_vibe: bool = False
    friend_vibe: bool = False
    romantic_vibe: bool = False
    same_music_taste: bool = False
    want_another_round: bool = False


class KaraokeVoteResponse(BaseModel):
    ok: bool
    mutual_match_created: bool
    match_id: int | None = None


class BillingOut(BaseModel):
    premium: bool
    credits: int
    subscription_plan: str


class CreditPurchaseRequest(BaseModel):
    credits: int = Field(ge=1, le=500)


class SubscriptionRequest(BaseModel):
    plan: str = Field(pattern="^(free|premium)$")


class MvpStatus(BaseModel):
    app: str
    stage: str
    backend_ready: bool
    mobile_live_api_ready: bool
    auth_ready: bool
    discovery_ready: bool
    chat_ready: bool
    karaoke_ready: bool
    billing_ready: bool
    next_priority: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def issue_token(db: Session, user_id: int) -> AuthToken:
    token = AuthToken(
        user_id=user_id,
        token=secrets.token_urlsafe(32),
        expires_at=utcnow() + timedelta(days=14),
    )
    db.add(token)
    db.flush()
    return token


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token_value = authorization.split(" ", 1)[1].strip()
    token = db.query(AuthToken).filter(AuthToken.token == token_value).first()
    if not token or token.expires_at < utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.get(User, token.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def build_profile(user: User) -> ProfileOut:
    return ProfileOut.model_validate(user)


def get_subscription_plan(db: Session, user_id: int) -> str:
    record = (
        db.query(SubscriptionRecord)
        .filter(SubscriptionRecord.user_id == user_id)
        .order_by(SubscriptionRecord.id.desc())
        .first()
    )
    return record.plan if record else "free"


def normalize_pair(user_a_id: int, user_b_id: int) -> tuple[int, int]:
    return tuple(sorted((user_a_id, user_b_id)))


def get_or_create_match(
    db: Session,
    user_a_id: int,
    user_b_id: int,
    source: str,
    compatibility_score: int,
) -> Match:
    first_id, second_id = normalize_pair(user_a_id, user_b_id)
    match = (
        db.query(Match)
        .filter(Match.user_a_id == first_id, Match.user_b_id == second_id)
        .first()
    )
    if match:
        return match

    match = Match(
        user_a_id=first_id,
        user_b_id=second_id,
        source=source,
        compatibility_score=compatibility_score,
        status="matched",
    )
    db.add(match)
    db.flush()
    return match


def compute_discovery_cards(db: Session, current_user: User) -> list[DiscoveryCard]:
    grouped: dict[int, list[ArtistPreference]] = defaultdict(list)
    for pref in db.query(ArtistPreference).all():
        grouped[pref.user_id].append(pref)

    swiped_ids = {
        swipe.to_user_id
        for swipe in db.query(Swipe).filter(Swipe.from_user_id == current_user.id).all()
    }

    query = db.query(User).filter(User.id != current_user.id)
    if swiped_ids:
        query = query.filter(User.id.notin_(swiped_ids))
    all_users = query.all()
    current_artists = {item.artist_name.lower() for item in grouped.get(current_user.id, [])}
    current_genres = {
        item.genre.lower() for item in grouped.get(current_user.id, []) if item.genre
    }

    cards: list[DiscoveryCard] = []
    for user in all_users:
        user_prefs = grouped.get(user.id, [])
        artists = [item.artist_name for item in user_prefs]
        genres = sorted({item.genre for item in user_prefs if item.genre})
        overlap_artists = sum(1 for item in user_prefs if item.artist_name.lower() in current_artists)
        overlap_genres = sum(
            1 for item in user_prefs if item.genre and item.genre.lower() in current_genres
        )
        score = min(99, 45 + overlap_artists * 20 + overlap_genres * 7)

        reason_bits = []
        if overlap_artists:
            reason_bits.append(f"{overlap_artists} shared artist picks")
        if overlap_genres:
            reason_bits.append(f"{overlap_genres} genre overlaps")
        if not reason_bits:
            reason_bits.append("different playlists, but still worth a live vibe check")

        cards.append(
            DiscoveryCard(
                user_id=user.id,
                display_name=user.display_name,
                age=user.age,
                city=user.city,
                bio=user.bio,
                favorite_artists=artists,
                genres=genres,
                compatibility_score=score,
                compatibility_reason=", ".join(reason_bits),
            )
        )

    cards.sort(key=lambda item: item.compatibility_score, reverse=True)
    return cards


def seed_db(db: Session) -> None:
    if db.query(User).count() > 0:
        return

    users = [
        User(
            email="steven@syncd.local",
            password_hash=hash_password("syncd123"),
            display_name="Steven",
            age=37,
            city="Grass Valley, CA",
            interested_in="women",
            bio="Builder by day. Music and chaos by night. Looking for chemistry that actually feels alive.",
            work="Residential remodeling",
            kids="not specified",
            premium=True,
            credits=40,
        ),
        User(
            email="luna@syncd.local",
            password_hash=hash_password("syncd123"),
            display_name="Luna",
            age=31,
            city="Sacramento, CA",
            interested_in="men",
            bio="Alt girl, karaoke menace, and emotionally fluent when caffeinated.",
            work="Tattoo artist",
            kids="no kids",
            premium=False,
            credits=12,
        ),
        User(
            email="jade@syncd.local",
            password_hash=hash_password("syncd123"),
            display_name="Jade",
            age=29,
            city="Reno, NV",
            interested_in="men",
            bio="Country roads, loud choruses, dive bars, and a suspiciously competitive duet streak.",
            work="Bartender",
            kids="one kid",
            premium=True,
            credits=22,
        ),
        User(
            email="ivy@syncd.local",
            password_hash=hash_password("syncd123"),
            display_name="Ivy",
            age=33,
            city="San Jose, CA",
            interested_in="men",
            bio="Emo night forever. If your playlist has emotional damage, we should probably talk.",
            work="Product designer",
            kids="no kids",
            premium=False,
            credits=18,
        ),
    ]
    db.add_all(users)
    db.flush()

    db.add_all(
        [
            ArtistPreference(user_id=users[0].id, artist_name="Breaking Benjamin", genre="rock", weight=1.0),
            ArtistPreference(user_id=users[0].id, artist_name="DizzyIsDead", genre="alt", weight=0.8),
            ArtistPreference(user_id=users[0].id, artist_name="Matchbox Twenty", genre="rock", weight=0.7),
            ArtistPreference(user_id=users[1].id, artist_name="Paramore", genre="alt", weight=1.0),
            ArtistPreference(user_id=users[1].id, artist_name="Breaking Benjamin", genre="rock", weight=0.9),
            ArtistPreference(user_id=users[1].id, artist_name="Evanescence", genre="rock", weight=0.8),
            ArtistPreference(user_id=users[2].id, artist_name="Chris Stapleton", genre="country", weight=1.0),
            ArtistPreference(user_id=users[2].id, artist_name="Jelly Roll", genre="country rock", weight=0.8),
            ArtistPreference(user_id=users[2].id, artist_name="Lainey Wilson", genre="country", weight=0.7),
            ArtistPreference(user_id=users[3].id, artist_name="My Chemical Romance", genre="emo", weight=1.0),
            ArtistPreference(user_id=users[3].id, artist_name="Paramore", genre="alt", weight=0.9),
            ArtistPreference(user_id=users[3].id, artist_name="Evanescence", genre="rock", weight=0.8),
        ]
    )

    db.add_all(
        [
            SubscriptionRecord(user_id=users[0].id, plan="premium", status="active"),
            SubscriptionRecord(user_id=users[1].id, plan="free", status="active"),
            SubscriptionRecord(user_id=users[2].id, plan="premium", status="active"),
            SubscriptionRecord(user_id=users[3].id, plan="free", status="active"),
        ]
    )

    rooms = [
        KaraokeRoom(
            slug="emo-night",
            title="Emo Night",
            theme="emo night",
            description="Fast rounds for people whose playlists are mostly feelings and damage.",
            premium_only=False,
            round_seconds=150,
            mode="voice-video-optional",
        ),
        KaraokeRoom(
            slug="country-confessions",
            title="Country Confessions",
            theme="country night",
            description="Boots, heartbreak, and duet bait.",
            premium_only=False,
            round_seconds=165,
            mode="audio-or-video",
        ),
        KaraokeRoom(
            slug="toxic-ex-anthems",
            title="Toxic Ex Anthems",
            theme="toxic ex anthems",
            description="Premium room for dramatic chorus energy and suspiciously specific song choices.",
            premium_only=True,
            round_seconds=180,
            mode="voice-video-optional",
        ),
    ]
    db.add_all(rooms)
    db.flush()

    db.add_all(
        [
            KaraokeRoundTemplate(
                room_id=rooms[0].id,
                intro_seconds=25,
                performance_seconds=60,
                chat_seconds=45,
                prompt="Sing a chorus that wrecked you in high school or finish the lyric your partner starts.",
            ),
            KaraokeRoundTemplate(
                room_id=rooms[1].id,
                intro_seconds=30,
                performance_seconds=75,
                chat_seconds=45,
                prompt="Pick a country chorus or trade lines in a duet verse.",
            ),
            KaraokeRoundTemplate(
                room_id=rooms[2].id,
                intro_seconds=20,
                performance_seconds=90,
                chat_seconds=45,
                prompt="Give them the break-up anthem, then decide whether the vibe is romance or just beautiful damage.",
            ),
        ]
    )

    db.add_all(
        [
            RoomParticipant(room_id=rooms[0].id, user_id=users[1].id, active=True),
            RoomParticipant(room_id=rooms[1].id, user_id=users[2].id, active=True),
            RoomParticipant(room_id=rooms[2].id, user_id=users[3].id, active=True),
        ]
    )

    match = get_or_create_match(db, users[0].id, users[1].id, "karaoke_roulette", 91)
    db.add(
        ChatMessage(
            match_id=match.id,
            sender_user_id=users[1].id,
            body="You better not dodge the Paramore duet next round.",
        )
    )
    db.add(
        ChatMessage(
            match_id=match.id,
            sender_user_id=users[0].id,
            body="Only if you can actually hit the chorus.",
        )
    )

    db.commit()


app = FastAPI(title="Syncd API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_db(db)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "Syncd API"}


@app.get("/api/v1/meta/mvp-status", response_model=MvpStatus)
def mvp_status() -> MvpStatus:
    return MvpStatus(
        app="Syncd",
        stage="Persisted MVP foundation",
        backend_ready=True,
        mobile_live_api_ready=True,
        auth_ready=True,
        discovery_ready=True,
        chat_ready=True,
        karaoke_ready=True,
        billing_ready=True,
        next_priority="Add websocket transport and true real-time karaoke orchestration.",
    )


@app.post("/api/v1/auth/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        age=payload.age,
        city=payload.city,
        interested_in=payload.interested_in,
        bio=payload.bio,
        work=payload.work,
        kids=payload.kids,
        premium=False,
        credits=10,
    )
    db.add(user)
    db.flush()
    db.add(SubscriptionRecord(user_id=user.id, plan="free", status="active"))
    db.add(CreditLedger(user_id=user.id, delta=10, reason="signup bonus"))
    token = issue_token(db, user.id)
    db.commit()
    db.refresh(user)
    return AuthResponse(token=token.token, expires_at=token.expires_at, user=build_profile(user))


@app.post("/api/v1/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = issue_token(db, user.id)
    db.commit()
    return AuthResponse(token=token.token, expires_at=token.expires_at, user=build_profile(user))


@app.get("/api/v1/auth/me", response_model=ProfileOut)
def auth_me(current_user: User = Depends(get_current_user)) -> ProfileOut:
    return build_profile(current_user)


@app.get("/api/v1/profile/me", response_model=ProfileOut)
def get_me(current_user: User = Depends(get_current_user)) -> ProfileOut:
    return build_profile(current_user)


@app.put("/api/v1/profile/me", response_model=ProfileOut)
def update_me(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileOut:
    for field, value in payload.model_dump().items():
        setattr(current_user, field, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return build_profile(current_user)


@app.get("/api/v1/discovery", response_model=list[DiscoveryCard])
def list_discovery_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DiscoveryCard]:
    return compute_discovery_cards(db, current_user)


@app.post("/api/v1/discovery/swipe", response_model=SwipeResponse)
def swipe_user(
    payload: SwipeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SwipeResponse:
    if payload.target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot swipe on yourself")

    target_user = db.get(User, payload.target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    swipe = (
        db.query(Swipe)
        .filter(Swipe.from_user_id == current_user.id, Swipe.to_user_id == payload.target_user_id)
        .first()
    )
    if swipe:
        swipe.action = payload.action
        swipe.source = payload.source
    else:
        swipe = Swipe(
            from_user_id=current_user.id,
            to_user_id=payload.target_user_id,
            action=payload.action,
            source=payload.source,
        )
        db.add(swipe)

    created_match = False
    match_id = None
    if payload.action == "like":
        reciprocal = (
            db.query(Swipe)
            .filter(
                Swipe.from_user_id == payload.target_user_id,
                Swipe.to_user_id == current_user.id,
                Swipe.action == "like",
            )
            .first()
        )
        if reciprocal:
            cards = compute_discovery_cards(db, current_user)
            score = next((card.compatibility_score for card in cards if card.user_id == payload.target_user_id), 75)
            match = get_or_create_match(db, current_user.id, payload.target_user_id, payload.source, score)
            created_match = True
            match_id = match.id

    db.commit()
    return SwipeResponse(ok=True, action=payload.action, created_match=created_match, match_id=match_id)


@app.get("/api/v1/matches", response_model=list[MatchOut])
def list_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MatchOut]:
    records = (
        db.query(Match)
        .filter(or_(Match.user_a_id == current_user.id, Match.user_b_id == current_user.id))
        .order_by(Match.id.desc())
        .all()
    )
    output: list[MatchOut] = []
    for record in records:
        other_user_id = record.user_b_id if record.user_a_id == current_user.id else record.user_a_id
        other_user = db.get(User, other_user_id)
        if not other_user:
            continue
        output.append(
            MatchOut(
                id=record.id,
                other_user_id=other_user_id,
                other_display_name=other_user.display_name,
                source=record.source,
                compatibility_score=record.compatibility_score,
                status=record.status,
            )
        )
    return output


@app.get("/api/v1/chats/{match_id}", response_model=list[ChatMessageOut])
def get_chat_messages(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChatMessageOut]:
    match = db.get(Match, match_id)
    if not match or current_user.id not in {match.user_a_id, match.user_b_id}:
        raise HTTPException(status_code=404, detail="Match not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.match_id == match_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )
    return [ChatMessageOut.model_validate(message, from_attributes=True) for message in messages]


@app.post("/api/v1/chats/{match_id}", response_model=ChatMessageOut)
def send_chat_message(
    match_id: int,
    payload: ChatSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatMessageOut:
    match = db.get(Match, match_id)
    if not match or current_user.id not in {match.user_a_id, match.user_b_id}:
        raise HTTPException(status_code=404, detail="Match not found")

    message = ChatMessage(match_id=match_id, sender_user_id=current_user.id, body=payload.body.strip())
    db.add(message)
    db.commit()
    db.refresh(message)
    return ChatMessageOut.model_validate(message, from_attributes=True)


@app.get("/api/v1/events/karaoke-rooms", response_model=list[KaraokeRoomOut])
def list_karaoke_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[KaraokeRoom]:
    _ = current_user
    return db.query(KaraokeRoom).order_by(KaraokeRoom.premium_only, KaraokeRoom.id).all()


@app.get("/api/v1/events/karaoke-rooms/{room_id}", response_model=KaraokeRoomDetail)
def get_karaoke_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KaraokeRoomDetail:
    _ = current_user
    room = db.get(KaraokeRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    template = db.query(KaraokeRoundTemplate).filter(KaraokeRoundTemplate.room_id == room_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Round template not found")

    active_participants = (
        db.query(RoomParticipant)
        .filter(RoomParticipant.room_id == room_id, RoomParticipant.active == True)
        .count()
    )

    return KaraokeRoomDetail(
        id=room.id,
        slug=room.slug,
        title=room.title,
        theme=room.theme,
        description=room.description,
        premium_only=room.premium_only,
        min_age=room.min_age,
        round_seconds=room.round_seconds,
        mode=room.mode,
        intro_seconds=template.intro_seconds,
        performance_seconds=template.performance_seconds,
        chat_seconds=template.chat_seconds,
        prompt=template.prompt,
        active_participants=active_participants,
    )


@app.post("/api/v1/events/karaoke-rooms/{room_id}/join", response_model=KaraokeJoinResponse)
def join_karaoke_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KaraokeJoinResponse:
    room = db.get(KaraokeRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if current_user.age < room.min_age:
        raise HTTPException(status_code=403, detail="You do not meet the age requirement")

    if room.premium_only and not current_user.premium:
        raise HTTPException(status_code=402, detail="Premium required for this room")

    participant = (
        db.query(RoomParticipant)
        .filter(RoomParticipant.room_id == room_id, RoomParticipant.user_id == current_user.id)
        .first()
    )
    if participant:
        participant.active = True
    else:
        participant = RoomParticipant(room_id=room_id, user_id=current_user.id, active=True)
        db.add(participant)

    active_count = (
        db.query(RoomParticipant)
        .filter(RoomParticipant.room_id == room_id, RoomParticipant.active == True)
        .count()
    )

    db.commit()
    return KaraokeJoinResponse(
        room_id=room_id,
        joined=True,
        credits_remaining=current_user.credits,
        active_participants=active_count,
    )


@app.post("/api/v1/events/karaoke-rooms/{room_id}/start-round", response_model=KaraokeRoundOut)
def start_karaoke_round(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KaraokeRoundOut:
    room = db.get(KaraokeRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    me = (
        db.query(RoomParticipant)
        .filter(RoomParticipant.room_id == room_id, RoomParticipant.user_id == current_user.id, RoomParticipant.active == True)
        .first()
    )
    if not me:
        raise HTTPException(status_code=400, detail="Join the room before starting a round")

    partner_participant = (
        db.query(RoomParticipant)
        .filter(
            RoomParticipant.room_id == room_id,
            RoomParticipant.user_id != current_user.id,
            RoomParticipant.active == True,
        )
        .order_by(RoomParticipant.joined_at.asc())
        .first()
    )
    if not partner_participant:
        raise HTTPException(status_code=409, detail="No partner is currently available in this room")

    template = db.query(KaraokeRoundTemplate).filter(KaraokeRoundTemplate.room_id == room_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Round template not found")

    started_at = utcnow()
    duration = template.intro_seconds + template.performance_seconds + template.chat_seconds
    round_record = KaraokeRound(
        room_id=room_id,
        participant_a_id=current_user.id,
        participant_b_id=partner_participant.user_id,
        intro_seconds=template.intro_seconds,
        performance_seconds=template.performance_seconds,
        chat_seconds=template.chat_seconds,
        prompt=template.prompt,
        status="active",
        started_at=started_at,
        ends_at=started_at + timedelta(seconds=duration),
    )
    db.add(round_record)
    db.commit()
    db.refresh(round_record)

    partner_user = db.get(User, partner_participant.user_id)
    return KaraokeRoundOut(
        id=round_record.id,
        room_id=round_record.room_id,
        partner_user_id=partner_user.id,
        partner_display_name=partner_user.display_name,
        intro_seconds=round_record.intro_seconds,
        performance_seconds=round_record.performance_seconds,
        chat_seconds=round_record.chat_seconds,
        prompt=round_record.prompt,
        status=round_record.status,
        started_at=round_record.started_at,
        ends_at=round_record.ends_at,
    )


@app.post("/api/v1/events/karaoke-rounds/{round_id}/vote", response_model=KaraokeVoteResponse)
def vote_on_round(
    round_id: int,
    payload: KaraokeVoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KaraokeVoteResponse:
    round_record = db.get(KaraokeRound, round_id)
    if not round_record or current_user.id not in {round_record.participant_a_id, round_record.participant_b_id}:
        raise HTTPException(status_code=404, detail="Round not found")

    target_user_id = (
        round_record.participant_b_id if current_user.id == round_record.participant_a_id else round_record.participant_a_id
    )

    vote = (
        db.query(KaraokeVote)
        .filter(KaraokeVote.round_id == round_id, KaraokeVote.voter_user_id == current_user.id)
        .first()
    )
    if vote:
        vote.liked_vibe = payload.liked_vibe
        vote.friend_vibe = payload.friend_vibe
        vote.romantic_vibe = payload.romantic_vibe
        vote.same_music_taste = payload.same_music_taste
        vote.want_another_round = payload.want_another_round
    else:
        vote = KaraokeVote(
            round_id=round_id,
            voter_user_id=current_user.id,
            target_user_id=target_user_id,
            liked_vibe=payload.liked_vibe,
            friend_vibe=payload.friend_vibe,
            romantic_vibe=payload.romantic_vibe,
            same_music_taste=payload.same_music_taste,
            want_another_round=payload.want_another_round,
        )
        db.add(vote)

    reciprocal = (
        db.query(KaraokeVote)
        .filter(KaraokeVote.round_id == round_id, KaraokeVote.voter_user_id == target_user_id)
        .first()
    )

    mutual_match_created = False
    match_id = None
    if reciprocal and reciprocal.romantic_vibe and payload.romantic_vibe:
        match = get_or_create_match(db, current_user.id, target_user_id, "karaoke_roulette", 88)
        mutual_match_created = True
        match_id = match.id

    db.commit()
    return KaraokeVoteResponse(ok=True, mutual_match_created=mutual_match_created, match_id=match_id)


@app.get("/api/v1/billing/me", response_model=BillingOut)
def get_billing(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingOut:
    return BillingOut(
        premium=current_user.premium,
        credits=current_user.credits,
        subscription_plan=get_subscription_plan(db, current_user.id),
    )


@app.post("/api/v1/billing/credits/purchase", response_model=BillingOut)
def purchase_credits(
    payload: CreditPurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingOut:
    current_user.credits += payload.credits
    db.add(current_user)
    db.add(CreditLedger(user_id=current_user.id, delta=payload.credits, reason="manual purchase"))
    db.commit()
    db.refresh(current_user)
    return BillingOut(
        premium=current_user.premium,
        credits=current_user.credits,
        subscription_plan=get_subscription_plan(db, current_user.id),
    )


@app.post("/api/v1/billing/subscription", response_model=BillingOut)
def update_subscription(
    payload: SubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingOut:
    current_user.premium = payload.plan == "premium"
    db.add(current_user)
    db.add(SubscriptionRecord(user_id=current_user.id, plan=payload.plan, status="active"))
    db.commit()
    db.refresh(current_user)
    return BillingOut(
        premium=current_user.premium,
        credits=current_user.credits,
        subscription_plan=get_subscription_plan(db, current_user.id),
    )
