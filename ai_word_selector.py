import nltk
import random
from nltk.corpus import words
from collections import Counter

# Download only once
try:
    words.words()
except LookupError:
    nltk.download("words")

WORD_LIST = [
    w.lower()
    for w in words.words()
    if w.isalpha() and 6 <= len(w) <= 10
]

LETTER_FREQ = Counter("".join(WORD_LIST))

def difficulty_score(word):
    return sum(1 / LETTER_FREQ[c] for c in word)

def get_ai_word(level="medium"):
    scored = [(w, difficulty_score(w)) for w in WORD_LIST]
    scored.sort(key=lambda x: x[1])

    if level == "easy":
        return random.choice(scored[:2000])[0]
    elif level == "hard":
        return random.choice(scored[-2000:])[0]
    else:
        return random.choice(scored[2000:4000])[0]
