import random
import json
import os

HANGMAN_PICS = [
    '''
       +---+
       |   |
           |
           |
           |
           |
    =========''', '''
       +---+
       |   |
       O   |
           |
           |
           |
    =========''', '''
       +---+
       |   |
       O   |
       |   |
           |
           |
    =========''', '''
       +---+
       |   |
       O   |
      /|   |
           |
           |
    =========''', '''
       +---+
       |   |
       O   |
      /|\\  |
           |
           |
    =========''', '''
       +---+
       |   |
       O   |
      /|\\  |
      /    |
           |
    =========''', '''
       +---+
       |   |
       O   |
      /|\\  |
      / \\  |
           |
    ========='''
]

STATS_FILE = 'hangman_stats.json'
GAME_STATE_FILE = 'game_state.json'

def clear_screen(): # this command we use for Clean the terminal screen for refresh display.
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_stats():# this command is used to load game results(wins/loses) from json data.
    """Load win/loss stats from a JSON file."""
    try:
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'wins': 0, 'losses': 0}

def save_stats(stats):# we use when we store win/loss date in a Json file.
    """Save win/loss stats to a JSON file."""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f)

def load_words(file_path='words.txt'):# This command use for load word from words.txt, categorized by difficulty tiers.
    """Load words from a text file, grouped by difficulty sections [Easy], [Medium], [Hard]."""
    words = {'easy': [], 'medium': [], 'hard': []}
    with open(file_path, 'r') as f:
        current_tier = None
        for line in f:
            line = line.strip()
            if line in ['[Easy]', '[Medium]', '[Hard]']:
                current_tier = line[1:-1].lower()
            elif line and current_tier:
                words[current_tier].append(line.upper())
    for tier in words:
        if not words[tier]:
            raise ValueError(f"Error: No words found for {tier} tier in {file_path}")
    return words

def get_random_word(words, tier):# this command randomly select a word from the given difficulty tier.
    """Select a random word from the specified tier."""
    return random.choice(words[tier])


def display_game_state(guessed_letters, secret):# Show updated game visuals and progress (hangman, misses, word)
    """Display hangman drawing, missed letters, and word progress."""
    missed = [l for l, v in guessed_letters.items() if v and l not in secret]
    print(HANGMAN_PICS[len(missed)])
    print(f"\nMissed letters: {' '.join(missed)}\n")
    display = ' '.join([ch if ch in guessed_letters and guessed_letters[ch] else '_' for ch in secret])
    print(display + "\n")


def get_player_guess(guessed_letters):# this command is used to obtain and verify player's letter guess.
    """Get and validate player's letter guess."""
    while True:
        guess = input('Guess a letter: ').lower().strip()
        if len(guess) != 1:
            print("Enter a single letter.")
        elif not guess.isalpha():
            print("Enter a LETTER.")
        elif guess.upper() in guessed_letters:
            print("You've already guessed that. Try again.")
        else:
            return guess.upper()


def save_game(secret_word, guessed_letters):# when we want to store the current game progress in a JSON file
    """Save the current game state to a JSON file."""
    with open(GAME_STATE_FILE, 'w') as f:
        json.dump({'secret_word': secret_word, 'guessed_letters': guessed_letters}, f)


def load_game():# this command for restore game state from a JSON save file.
    """Load a saved game state from a JSON file."""
    try:
        with open(GAME_STATE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def main_menu(stats):# this command shows the  main menu options and obtain the user's choice.
    """Display main menu and get user choice."""
    clear_screen()
    print('=============================')
    print('         HANGMAN GAME        ')
    print('=============================')
    print(f"Wins: {stats['wins']} | Losses: {stats['losses']}")
    print('1. New Game (Easy)')
    print('2. New Game (Medium)')
    print('3. New Game (Hard)')
    print('4. Continue Saved Game' if os.path.exists(GAME_STATE_FILE) else '4. (No saved game)')
    print('5. Quit')
    while True:
        choice = input('Choose an option (1-5): ').strip()
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        print("Enter a number between 1 and 5.")


def play_game():# Run the main game loop
    """Run the main game loop."""
    stats = load_stats()
    words = load_words()
    while True:
        choice = main_menu(stats)
        if choice == '5':
            print("Thanks for playing!")
            break
        if choice == '4' and os.path.exists(GAME_STATE_FILE):
            game_state = load_game()
            if not game_state:
                print("Failed to load game. Starting new game.")
                choice = '1'
        else:
            choice = '1' if choice == '4' else choice

        tier = {'1': 'easy', '2': 'medium', '3': 'hard'}[choice]
        secret_word = get_random_word(words, tier) if choice != '4' else game_state['secret_word']
        guessed_letters = {} if choice != '4' else game_state['guessed_letters']
        max_guesses = len(HANGMAN_PICS) - 1

        while len([l for l, v in guessed_letters.items() if v and l not in secret_word]) < max_guesses:
            clear_screen()
            display_game_state(guessed_letters, secret_word)
            print(f"Difficulty: {tier.capitalize()}" if choice != '4' else "Continuing saved game")
            guess = get_player_guess(guessed_letters)
            guessed_letters[guess] = True
            save_game(secret_word, guessed_letters)
            if all(ch in guessed_letters and guessed_letters[ch] for ch in secret_word):
                clear_screen()
                display_game_state(guessed_letters, secret_word)
                print(f"You guessed it! The word was '{secret_word}'")
                stats['wins'] += 1
                save_stats(stats)
                if os.path.exists(GAME_STATE_FILE):
                    os.remove(GAME_STATE_FILE)
                break
        else:
            clear_screen()
            display_game_state(guessed_letters, secret_word)
            print(f"You ran out of guesses! The word was '{secret_word}'")
            stats['losses'] += 1
            save_stats(stats)
            if os.path.exists(GAME_STATE_FILE):
                os.remove(GAME_STATE_FILE)

if __name__ == '__main__':
    play_game()
