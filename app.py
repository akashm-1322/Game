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

# ---------------- GLOBAL STYLES (TRUE RESPONSIVE) ----------------
st.markdown("""
<style>
/* ---------- GLOBAL ---------- */
.block-container {
    max-width: 1200px;
    padding-top: 1rem;
    padding-bottom: 1.5rem;
}

/* ---------- BADGE ---------- */
.badge {
    padding: 6px 16px;
    border-radius: 999px;
    font-weight: 700;
    color: black;
}
.badge-easy { background: linear-gradient(135deg,#2ecc71,#27ae60); }
.badge-medium { background: linear-gradient(135deg,#f1c40f,#f39c12); }
.badge-hard { background: linear-gradient(135deg,#e74c3c,#c0392b); }

/* ---------- BUTTONS ---------- */
.stButton>button {
    width: 100%;
    min-height: 44px;
    border-radius: 10px;
    font-weight: 600;
}

/* ---------- KEYBOARD ---------- */
.keyboard-desktop { display: block; }
.keyboard-mobile { display: none; }

.key-btn button {
    font-size: 16px;
    padding: 10px 0;
}

/* ---------- MOBILE ---------- */
@media (max-width: 768px) {
    .keyboard-desktop { display: none; }
    .keyboard-mobile { display: block; }
    h2 { font-size: 20px; }
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

# ================= START MENU =================
if not st.session_state.started:
    st.title("🧠 AI Hangman")

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
    f"<div style='text-align:center;margin-bottom:8px'>"
    f"<span class='badge {badge_class}'>🎚 {st.session_state.difficulty.upper()}</span>"
    f"</div>",
    unsafe_allow_html=True
)

img = os.path.join(ASSETS_PATH,f"hangman{st.session_state.wrong}.png")
if os.path.exists(img):
    st.image(img, width=220)

st.progress(min((st.session_state.wrong + st.session_state.hint_used)/MAX_TRIES,1.0))

display = " ".join(c.upper() if c in st.session_state.guessed else "_" for c in st.session_state.word)
st.markdown(f"<h2 style='text-align:center'>{display}</h2>", unsafe_allow_html=True)

# ================= LETTER KEYBOARDS =================
letters = list(string.ascii_lowercase)

def render_keyboard(rows, css_class):
    st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
    idx = 0
    for r in rows:
        cols = st.columns(r)
        for c in cols:
            if idx >= len(letters):
                break
            l = letters[idx]
            with c:
                st.markdown("<div class='key-btn'>", unsafe_allow_html=True)
                if st.button(l.upper(), disabled=l in st.session_state.guessed, key=f"{css_class}_{l}"):
                    st.session_state.guessed.add(l)
                    if l not in st.session_state.word:
                        st.session_state.wrong += 1
                        st.toast("Wrong!", icon="💀")
                    else:
                        st.toast("Correct!", icon="🎯")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            idx += 1
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("### ⌨️ Choose a Letter")

# Desktop: wide & natural
render_keyboard([8, 8, 8, 2], "keyboard-desktop")

# Mobile: compact & touch-friendly
render_keyboard([5, 5, 5, 5, 6], "keyboard-mobile")

# ================= RESULT =================
won = all(c in st.session_state.guessed for c in st.session_state.word)
final_score = max(0, MAX_TRIES - st.session_state.wrong - st.session_state.hint_used)

if st.session_state.wrong >= MAX_TRIES:
    if st.session_state.hint_used > 0:
        final_score = 0
    won = False

if won:
    st.success("🎉 YOU WON!")
    st.balloons()
elif st.session_state.wrong >= MAX_TRIES:
    st.error("💀 YOU LOST!")
    st.info(f"Word was **{st.session_state.word.upper()}**")

if (won or st.session_state.wrong >= MAX_TRIES) and not st.session_state.score_updated:
    update_score(st.session_state.user, won, final_score, st.session_state.difficulty)
    st.session_state.score_updated = True

# ================= RESTART =================
if st.button("🔄 Restart Game"):
    st.session_state.started = False
    st.session_state.hint_letters = []
    st.session_state.score_updated = False
    st.rerun()
