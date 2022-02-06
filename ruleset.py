# Wordle decision-making ruleset

class Ruleset:
    def __init__(self):
        self.randomise_selection = False
        self.pick_next_from_candidates = True
        self.guess_at_attempts = 5
        self.guess_at_remaining = 100
