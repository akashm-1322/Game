import streamlit as st
import string, os, time, random
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

# ---------------- GLOBAL STYLES ----------------
st.markdown("""
<style>
.badge {
    display: inline-block;
    padding: 8px 18px;
    border-radius: 999px;
    font-weight: 700;
    color: white;
}
.badge-easy { background: linear-gradient(135deg,#2ecc71,#27ae60); }
.badge-medium { background: linear-gradient(135deg,#f1c40f,#f39c12); }
.badge-hard { background: linear-gradient(135deg,#e74c3c,#c0392b); }

.sidebar-card {
    background: rgba(255,255,255,0.95);
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 10px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}
button[kind="primary"] {
    width: 100%;
}
@media (max-width: 600px) {
    h2 { font-size: 22px; }
}
</style>
""", unsafe_allow_html=True)

# ================= AUTH =================
if not st.session_state.user:
    st.title("🔐 AI Hangman")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u_login = st.text_input("Username", key="login_user")
        p_login = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user = login(u_login, p_login)
            if user:
                st.session_state.user = user["username"]
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u_signup = st.text_input("New Username", key="signup_user")
        p_signup = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Create Account"):
            if signup(u_signup, p_signup):
                st.success("Account created! Login now.")
            else:
                st.error("Username exists")

    st.stop()

# ================= USER STATS =================
stats = get_user_stats(st.session_state.user) or {
    "best_score": 0,
    "wins": 0,
    "games_played": 0
}

# ================= SIDEBAR LEADERBOARD =================
st.sidebar.title("🏆 Global Rankings")
raw = get_leaderboard()
clean = []

for r in raw:
    username = r.get("username", "unknown")
    best = int(r.get("best_score", 0) or 0)
    wins = int(r.get("wins", 0) or 0)
    games = int(r.get("games_played", 0) or 0)
    avg = round(wins / games, 2) if games > 0 else 0.0
    clean.append({
        "username": username,
        "best_score": best,
        "wins": wins,
        "games_played": games,
        "avg_win_rate": avg
    })

ranked = sorted(
    clean,
    key=lambda x: (x["best_score"], x["avg_win_rate"], x["games_played"]),
    reverse=True
)

def get_badge(rank):
    return ["🥇 Gold", "🥈 Silver", "🥉 Bronze"][rank-1] if rank <= 3 else "🎯 Player"

for i, u in enumerate(ranked[:10], 1):
    st.sidebar.markdown(f"""
    <div class="sidebar-card">
        <b>{get_badge(i)} #{i} — {u['username']}</b><br>
        🏆 {u['best_score']} | 📈 {u['avg_win_rate']} | 🎮 {u['games_played']}
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
### 👤 {st.session_state.user}
🏆 Best: {stats['best_score']}  
🎯 Wins: {stats['wins']}  
🎮 Games: {stats['games_played']}
""")

# ================= START MENU =================
if not st.session_state.started:
    st.title("🧠 AI Hangman")

    st.session_state.difficulty = st.radio(
        "Choose Difficulty",
        ["easy", "medium", "hard"],
        horizontal=True
    )

    st.session_state.max_hints = 2 if st.session_state.difficulty == "hard" else 1

    if st.button("▶ Start Game", use_container_width=True):
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
    f"<div style='text-align:center'>"
    f"<span class='badge {badge_class}'>🎚 {st.session_state.difficulty.upper()}</span>"
    f"</div>",
    unsafe_allow_html=True
)

img = os.path.join(ASSETS_PATH, f"hangman{st.session_state.wrong}.png")
if os.path.exists(img):
    st.image(img, width=220)

st.progress(st.session_state.wrong / MAX_TRIES)

display = " ".join(
    c.upper() if c in st.session_state.guessed else "_"
    for c in st.session_state.word
)
st.markdown(f"<h2 style='text-align:center'>{display}</h2>", unsafe_allow_html=True)

# ================= HINT SYSTEM =================
if st.session_state.hint_used < st.session_state.max_hints:
    if st.button("💡 Get Hint", key=f"hint_button_{st.session_state.hint_used}"):
        correct = list(set(st.session_state.word) - st.session_state.guessed)
        wrongs = list(set(string.ascii_lowercase) - set(st.session_state.word))
        if correct:
            hint_letters = random.sample(correct, 1) + random.sample(wrongs, 2)
            random.shuffle(hint_letters)
            st.session_state.hint_letters = hint_letters
            st.session_state.hint_used += 1
            st.toast("Hint used! Score -1", icon="⚠️")

if st.session_state.hint_letters:
    st.markdown("### 🔍 Choose the correct letter")
    cols = st.columns(len(st.session_state.hint_letters))
    for i, l in enumerate(st.session_state.hint_letters):
        if cols[i].button(l.upper(), key=f"hint_{l}_{st.session_state.hint_used}"):
            st.session_state.guessed.add(l)
            st.session_state.hint_letters = []
            st.rerun()

# ================= LETTER GRID =================
cols = st.columns(7)
for i, l in enumerate(string.ascii_lowercase):
    if cols[i % 7].button(l.upper(), disabled=l in st.session_state.guessed, key=f"letter_{l}"):
        st.session_state.guessed.add(l)
        if l not in st.session_state.word:
            st.session_state.wrong += 1
            st.toast("Wrong!", icon="💀")
        else:
            st.toast("Correct!", icon="🎯")
        st.rerun()

# ================= RESULT =================
won = all(c in st.session_state.guessed for c in st.session_state.word)

if won:
    st.success("🎉 YOU WON!")
    st.balloons()
    final_score = st.session_state.wrong + st.session_state.hint_used
    st.markdown(
        f"""
        <div style="
            text-align:center;
            font-size:20px;
            padding:12px;
            background:#ecfdf5;
            border-radius:14px;
            margin-top:10px;
            box-shadow:0 6px 16px rgba(0,0,0,0.12);
        ">
            🏆 <b>Your Score:</b> {final_score}<br>
            💡 Hints Used: {st.session_state.hint_used}<br>
            ❌ Wrong Attempts: {st.session_state.wrong}
        </div>
        """,
        unsafe_allow_html=True
    )

elif st.session_state.wrong >= MAX_TRIES:
    st.error("💀 YOU LOST!")
    st.info(f"Word was **{st.session_state.word.upper()}**")

if (won or st.session_state.wrong >= MAX_TRIES) and not st.session_state.score_updated:
    update_score(
        st.session_state.user,
        won,
        st.session_state.wrong + st.session_state.hint_used,
        st.session_state.difficulty
    )
    st.session_state.score_updated = True

# ================= RESTART =================
if st.button("🔄 Restart Game", use_container_width=True, key="restart_game"):
    st.session_state.started = False
    st.session_state.hint_letters = []
    st.session_state.score_updated = False
    st.rerun()
