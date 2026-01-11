import streamlit as st
import string, os, random
from ai_word_selector import get_ai_word
from auth import login, signup, update_score, get_user_stats, get_leaderboard

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Hangman",
    page_icon="🎮",
    layout="centered"
)

MAX_TRIES = 6
ASSETS_PATH = "assets"

# ---------------- SESSION INIT ----------------
defaults = {
    "user": None,
    "started": False,
    "word": "",
    "guessed": set(),
    "wrong": 0,
    "difficulty": "medium",
    "hint_used": 0,
    "max_hints": 1,
    "score_updated": False,
    "hint_letters": []
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ===================== GLOBAL RESPONSIVE CSS =====================
st.markdown("""
<style>

/* ---------- ROOT FIXES ---------- */
html, body {
    overflow-x: hidden;
    max-width: 100%;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1.5rem;
    max-width: 720px;
    margin: auto;
}

/* ---------- HEADINGS ---------- */
h1, h2, h3 {
    text-align: center;
    word-wrap: break-word;
}

/* ---------- BADGES ---------- */
.badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 14px;
    color: black;
}
.badge-easy { background: linear-gradient(135deg,#2ecc71,#27ae60); }
.badge-medium { background: linear-gradient(135deg,#f1c40f,#f39c12); }
.badge-hard { background: linear-gradient(135deg,#e74c3c,#c0392b); }

/* ---------- SIDEBAR (ALL DEVICES) ---------- */
section[data-testid="stSidebar"] {
    min-width: 260px;
    max-width: 260px;
}

.sidebar-card {
    background: rgba(255,255,255,0.96);
    border-radius: 14px;
    padding: 12px;
    color: black;
    margin-bottom: 12px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}

/* ---------- BUTTONS ---------- */
.stButton > button {
    width: 100%;
    min-height: 44px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 15px;
}

/* ---------- LETTER KEYS ---------- */
.letter-btn button {
    min-height: 48px;
    font-size: 16px;
    padding: 8px 0;
}

/* ---------- IMAGE ---------- */
img {
    max-width: 100%;
    height: auto;
    margin: auto;
    display: block;
}

/* ---------- PROGRESS ---------- */
.stProgress > div {
    height: 14px;
    border-radius: 10px;
}

/* ---------- MOBILE ---------- */
@media (max-width: 600px) {

    /* Sidebar hidden by default, toggle via >> */
    section[data-testid="stSidebar"] {
        width: 260px !important;
    }

    .block-container {
        padding-left: 0.7rem;
        padding-right: 0.7rem;
    }

    h2 {
        font-size: 20px;
    }

    .badge {
        font-size: 13px;
        padding: 6px 14px;
    }

    .letter-btn button {
        min-height: 46px;
        font-size: 15px;
    }
}


/* ---------- TABLET ---------- */
@media (min-width: 601px) and (max-width: 1024px) {
    .block-container {
        max-width: 820px;
    }
}

/* ---------- DESKTOP ---------- */
@media (min-width: 1025px) {
    .block-container {
        max-width: 900px;
    }
}

</style>
""", unsafe_allow_html=True)

# ================= AUTH =================
if not st.session_state.user:
    st.title("🔐 AI Hangman")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u_login = st.text_input("Username")
        p_login = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login(u_login, p_login)
            if user:
                st.session_state.user = user["username"]
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u_signup = st.text_input("New Username")
        p_signup = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if signup(u_signup, p_signup):
                st.success("Account created! Login now.")
            else:
                st.error("Username exists")
    st.stop()

# ================= USER STATS =================
stats = get_user_stats(st.session_state.user) or {"best_score":0,"wins":0,"games_played":0}

# ================= START MENU =================
if not st.session_state.started:
    st.title("🧠 Ash's Hangman")

    st.session_state.difficulty = st.radio(
        "Choose Difficulty",
        ["easy","medium","hard"],
        horizontal=True
    )
    st.session_state.max_hints = 2 if st.session_state.difficulty=="hard" else 1

    if st.button("▶ Start Game"):
        st.session_state.word = get_ai_word(st.session_state.difficulty)
        st.session_state.guessed = set()
        st.session_state.wrong = 0
        st.session_state.hint_used = 0
        st.session_state.hint_letters = []
        st.session_state.started = True
        st.session_state.score_updated = False
        st.rerun()
    st.stop()

# ================= GAME UI =================
badge_class = f"badge-{st.session_state.difficulty}"
st.markdown(
    f"<div style='text-align:center;margin:100px'>"
    f"<span class='badge {badge_class}'>🎚 {st.session_state.difficulty.upper()}</span>"
    f"</div>",
    unsafe_allow_html=True
)

img = os.path.join(ASSETS_PATH,f"hangman{st.session_state.wrong}.png")
if os.path.exists(img):
    st.image(img, width=200)

st.progress(min((st.session_state.wrong + st.session_state.hint_used)/MAX_TRIES,1.0))

display = " ".join(c.upper() if c in st.session_state.guessed else "_" for c in st.session_state.word)
st.markdown(f"<h2 style='text-align:center'>{display}</h2>", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("## 🏆 Player Dashboard")

    # ---- Current User Stats ----
    st.markdown("### 👤 Your Stats")

    st.markdown(f"""
    <div class="sidebar-card">
        <b>Username:</b> {st.session_state.user}<br><br>
        🎮 <b>Games Played:</b> {stats["games_played"]}<br>
        ✅ <b>Wins:</b> {stats["wins"]}<br>
        🥇 <b>Best Score:</b> {stats["best_score"]}
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ---- Global Leaderboard ----
    st.markdown("### 🌍 Global Top 5")

    leaderboard = get_leaderboard() or []
    top5 = sorted(
        leaderboard,
        key=lambda x: x.get("best_score", 0),
        reverse=True
    )[:5]

    if not top5:
        st.info("No rankings yet")
    else:
        for i, player in enumerate(top5, start=1):
            st.markdown(f"""
            <div class="sidebar-card">
                🏅 <b>#{i} {player["username"]}</b><br><br>
                🎮 Games: {player["games_played"]}<br>
                ✅ Wins: {player["wins"]}<br>
                🥇 Best Score: {player["best_score"]}
            </div>
            """, unsafe_allow_html=True)


# ================= HINT SYSTEM =================
if st.session_state.hint_used < st.session_state.max_hints:
    if st.button("💡 Get Hint"):
        correct = list(set(st.session_state.word) - st.session_state.guessed)
        wrongs = list(set(string.ascii_lowercase) - set(st.session_state.word))
        if correct:
            st.session_state.hint_letters = random.sample(correct,1) + random.sample(wrongs,2)
            random.shuffle(st.session_state.hint_letters)
            st.session_state.hint_used += 1
            st.session_state.wrong += 1
            st.toast("Hint used! Chance lost", icon="⚠️")

if st.session_state.hint_letters:
    st.markdown("### 🔍 Choose the correct letter")
    cols = st.columns(len(st.session_state.hint_letters))
    for i,l in enumerate(st.session_state.hint_letters):
        if cols[i].button(l.upper()):
            st.session_state.guessed.add(l)
            st.session_state.hint_letters=[]
            st.rerun()

# ================= LETTER GRID (MOBILE FRIENDLY) =================
st.session_state.is_mobile = st.get_option("browser.gatherUsageStats") is not None and st.container

st.markdown("### ⌨️ Choose a Letter")

letters = list(string.ascii_lowercase)

is_mobile = st.session_state.get("is_mobile", False)

ROWS = [4, 4, 4, 4, 4, 4, 2] if is_mobile else [5, 5, 5, 5, 6]

idx = 0
for row_size in ROWS:
    cols = st.columns(row_size)
    for c in cols:
        if idx >= len(letters):
            break
        l = letters[idx]
        with c:
            st.markdown("<div class='letter-btn'>", unsafe_allow_html=True)
            if st.button(
                l.upper(),
                disabled=l in st.session_state.guessed,
                key=f"letter_{l}"
            ):
                st.session_state.guessed.add(l)
                if l not in st.session_state.word:
                    st.session_state.wrong += 1
                    st.toast("Wrong!", icon="💀")
                else:
                    st.toast("Correct!", icon="🎯")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        idx += 1

display_score = max(
    0,
    MAX_TRIES - st.session_state.wrong - st.session_state.hint_used
)

# ================= RESULT =================
won = all(c in st.session_state.guessed for c in st.session_state.word)

if won:
    st.success("🎉 YOU WON!")
    st.balloons()
    st.markdown(f"""
    <div style="text-align:center;padding:14px;background:#ecfdf5;
                border-radius:14px;color:black;">
        🏆 <b>Your Score:</b> {display_score}<br>
        💡 Hints Used: {st.session_state.hint_used}<br>
        ❌ Wrong Attempts: {st.session_state.wrong}
    </div>
    """, unsafe_allow_html=True)


elif st.session_state.wrong >= MAX_TRIES:
    st.error("💀 YOU LOST!")
    st.info(f"Word was **{st.session_state.word.upper()}**")
    st.markdown(f"""
    <div style="text-align:center;padding:12px;background:#fff1f2;
                border-radius:14px;color:black;">
        🏆 <b>Your Score:</b> 0<br>
        💡 Hints Used: {st.session_state.hint_used}<br>
        ❌ Wrong Attempts: {st.session_state.wrong}
    </div>
    """, unsafe_allow_html=True)


if (won or st.session_state.wrong >= MAX_TRIES) and not st.session_state.score_updated:
    update_score(
    st.session_state.user,
    won,
    st.session_state.wrong,
    st.session_state.hint_used,
    st.session_state.difficulty
)

    st.session_state.score_updated = True

# ================= RESTART =================
if st.button("🔄 Restart Game"):
    st.session_state.started = False
    st.session_state.hint_letters = []
    st.session_state.score_updated = False
    st.rerun()
