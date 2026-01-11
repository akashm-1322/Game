import pygame

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (0, 180, 0)
RED = (200, 0, 0)

def draw_word(screen, font, word, guessed):
    display = " ".join([c if c in guessed else "_" for c in word])
    text = font.render(display, True, BLACK)
    screen.blit(text, (50, 420))

def draw_status(screen, font, tries, difficulty):
    t = font.render(f"Tries Left: {6 - tries}", True, BLACK)
    d = font.render(f"Difficulty: {difficulty.upper()}", True, BLACK)
    screen.blit(t, (30, 30))
    screen.blit(d, (30, 70))
