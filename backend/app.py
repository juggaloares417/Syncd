from collections import defaultdict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DATABASE_URL = "sqlite:///./syncd.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
CURRENT_USER_ID = 1


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String(120))
    interested_in: Mapped[str] = mapped_column(String(120), default="women")
    bio: Mapped[str] = mapped_column(Text, default="")
    work: Mapped[str] = mapped_column(String(120), default="")
    kids: Mapped[str] = mapped_column(String(50), default="not specified")
    premium: Mapped[bool] = mapped_column(Boolean, default=False)
    credits: Mapped[int] = mapped_column(Integer, default=0)

    artists: Mapped[list["ArtistPreference"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class ArtistPreference(Base):
    __tablename__ = "artist_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    artist_name: Mapped[str] = mapped_column(String(120), index=True)
    genre: Mapped[str] = mapped_column(String(120), default="")
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    user: Mapped[User] = relationship(back_populates="artists")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_a_id: Mapped[int] = mapped_column(Integer, index=True)
    user_b_id: Mapped[int] = mapped_column(Integer, index=True)
    source: Mapped[str] = mapped_column(String(50), default="discovery")
    compatibility_score: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="matched")


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


class MatchOut(BaseModel):
    id: int
    other_user_id: int
    other_display_name: str
    source: str
    compatibility_score: int
    status: str


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


class MvpStatus(BaseModel):
    app: str
    stage: str
    backend_ready: bool
    mobile_stub_ready: bool
    karaoke_rooms_seeded: bool
    next_priority: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_db(db: Session) -> None:
    if db.query(User).count() > 0:
        return

    steven = User(
        email="steven@syncd.local",
        display_name="Steven",
        age=37,
        city="Grass Valley, CA",
        interested_in="women",
        bio="Builder by day. Music and chaos by night. Looking for chemistry that actually feels alive.",
        work="Residential remodeling",
        kids="not specified",
        premium=True,
        credits=40,
    )
    luna = User(
        email="luna@syncd.local",
        display_name="Luna",
        age=31,
        city="Sacramento, CA",
        interested_in="men",
        bio="Alt girl, karaoke menace, and emotionally fluent when caffeinated.",
        work="Tattoo artist",
        kids="no kids",
        premium=False,
        credits=6,
    )
    jade = User(
        email="jade@syncd.local",
        display_name="Jade",
        age=29,
        city="Reno, NV",
        interested_in="men",
        bio="Country roads, loud choruses, dive bars, and a suspiciously competitive duet streak.",
        work="Bartender",
        kids="one kid",
        premium=True,
        credits=22,
    )
    ivy = User(
        email="ivy@syncd.local",
        display_name="Ivy",
        age=33,
        city="San Jose, CA",
        interested_in="men",
        bio="Emo night forever. If your playlist has emotional damage, we should probably talk.",
        work="Product designer",
        kids="no kids",
        premium=False,
        credits=12,
    )

    db.add_all([steven, luna, jade, ivy])
    db.flush()

    db.add_all(
        [
            ArtistPreference(user_id=steven.id, artist_name="Breaking Benjamin", genre="rock", weight=1.0),
            ArtistPreference(user_id=steven.id, artist_name="DizzyIsDead", genre="alt", weight=0.8),
            ArtistPreference(user_id=steven.id, artist_name="Matchbox Twenty", genre="rock", weight=0.7),
            ArtistPreference(user_id=luna.id, artist_name="Paramore", genre="alt", weight=1.0),
            ArtistPreference(user_id=luna.id, artist_name="Breaking Benjamin", genre="rock", weight=0.9),
            ArtistPreference(user_id=luna.id, artist_name="Evanescence", genre="rock", weight=0.8),
            ArtistPreference(user_id=jade.id, artist_name="Chris Stapleton", genre="country", weight=1.0),
            ArtistPreference(user_id=jade.id, artist_name="Jelly Roll", genre="country rock", weight=0.8),
            ArtistPreference(user_id=jade.id, artist_name="Lainey Wilson", genre="country", weight=0.7),
            ArtistPreference(user_id=ivy.id, artist_name="My Chemical Romance", genre="emo", weight=1.0),
            ArtistPreference(user_id=ivy.id, artist_name="Paramore", genre="alt", weight=0.9),
            ArtistPreference(user_id=ivy.id, artist_name="Evanescence", genre="rock", weight=0.8),
        ]
    )

    db.add(
        Match(
            user_a_id=steven.id,
            user_b_id=luna.id,
            source="karaoke_roulette",
            compatibility_score=91,
            status="matched",
        )
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

    db.commit()


app = FastAPI(title="Syncd API", version="0.1.0")
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
        stage="MVP foundation",
        backend_ready=True,
        mobile_stub_ready=True,
        karaoke_rooms_seeded=True,
        next_priority="Wire like/pass actions to mutual match creation.",
    )


@app.get("/api/v1/profile/me", response_model=ProfileOut)
def get_me(db: Session = Depends(get_db)) -> User:
    user = db.get(User, CURRENT_USER_ID)
    if not user:
        raise HTTPException(status_code=404, detail="Current user not found")
    return user


@app.put("/api/v1/profile/me", response_model=ProfileOut)
def update_me(payload: ProfileUpdate, db: Session = Depends(get_db)) -> User:
    user = db.get(User, CURRENT_USER_ID)
    if not user:
        raise HTTPException(status_code=404, detail="Current user not found")

    for field, value in payload.model_dump().items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/api/v1/discovery", response_model=list[DiscoveryCard])
def list_discovery_cards(db: Session = Depends(get_db)) -> list[DiscoveryCard]:
    grouped: dict[int, list[ArtistPreference]] = defaultdict(list)
    for pref in db.query(ArtistPreference).all():
        grouped[pref.user_id].append(pref)

    all_users = db.query(User).filter(User.id != CURRENT_USER_ID).all()
    current_artists = {item.artist_name.lower() for item in grouped.get(CURRENT_USER_ID, [])}
    current_genres = {item.genre.lower() for item in grouped.get(CURRENT_USER_ID, []) if item.genre}

    cards: list[DiscoveryCard] = []
    for user in all_users:
        user_prefs = grouped.get(user.id, [])
        artists = [item.artist_name for item in user_prefs]
        genres = sorted({item.genre for item in user_prefs if item.genre})
        overlap_artists = sum(1 for item in user_prefs if item.artist_name.lower() in current_artists)
        overlap_genres = sum(1 for item in user_prefs if item.genre and item.genre.lower() in current_genres)
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


@app.get("/api/v1/matches", response_model=list[MatchOut])
def list_matches(db: Session = Depends(get_db)) -> list[MatchOut]:
    records = db.query(Match).filter((Match.user_a_id == CURRENT_USER_ID) | (Match.user_b_id == CURRENT_USER_ID)).all()
    output: list[MatchOut] = []

    for record in records:
        other_user_id = record.user_b_id if record.user_a_id == CURRENT_USER_ID else record.user_a_id
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


@app.get("/api/v1/events/karaoke-rooms", response_model=list[KaraokeRoomOut])
def list_karaoke_rooms(db: Session = Depends(get_db)) -> list[KaraokeRoom]:
    return db.query(KaraokeRoom).order_by(KaraokeRoom.premium_only, KaraokeRoom.id).all()


@app.get("/api/v1/events/karaoke-rooms/{room_id}", response_model=KaraokeRoomDetail)
def get_karaoke_room(room_id: int, db: Session = Depends(get_db)) -> KaraokeRoomDetail:
    room = db.get(KaraokeRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    template = db.query(KaraokeRoundTemplate).filter(KaraokeRoundTemplate.room_id == room_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Round template not found")

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
    )
