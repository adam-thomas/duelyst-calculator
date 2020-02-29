import argparse


AVG_NON_SINGLETON_COPIES = 2.5

class DuelystDrawSimulator:
    def __init__(self, total_cards, singleton, copies, target_turn, draws_per_turn, *, verbose=False):
        self.total_cards = total_cards
        self.copies = copies
        self.target_turn = target_turn
        self.draws_per_turn = draws_per_turn
        self.verbose = verbose

        # Replaces in Duelyst can't draw the same card again, so we need some estimation
        # of the number of copies of a typical card in a deck.
        self.copies_per_avg_card = 1 if singleton else AVG_NON_SINGLETON_COPIES

        # Accumulate the chance of having not yet drawn the card we want.
        # Before the start of the game, we have a 100% chance of not drawing it, since
        # we haven't drawn any cards yet.
        self.fail_chance = 1

    def replace(self):
        """Simulate a replace."""
        possible_cards = self.total_cards - (self.copies_per_avg_card - 1)
        undesired_cards = possible_cards - self.copies
        self.fail_chance = self.fail_chance * (undesired_cards / possible_cards)

        if self.verbose:
            print(
                F"   Card replaced. Chance of missing is now {self.fail_chance}; "
                F"{self.total_cards} cards remain in the deck."
            )

    def draw(self):
        """Simulate a draw."""
        possible_cards = self.total_cards
        undesired_cards = possible_cards - self.copies
        self.fail_chance = self.fail_chance * (undesired_cards / possible_cards)
        self.total_cards -= 1

        if self.verbose:
            print(
                F"   Card drawn. Chance of missing is now {self.fail_chance}; "
                F"{self.total_cards} cards remain in the deck."
            )

    def run(self):
        # The opening hand, assuming we hard mulligan for the desired card.
        if self.verbose:
            print("Opening hand:")
        for i in range(0, 5):
            self.draw()
        self.replace()
        self.replace()

        # On each turn except the target turn, we get a replace and an end-of-turn draw.
        for i in range(1, self.target_turn):
            if self.verbose:
                print(F"Turn {i}:")

            self.replace()
            for j in range(0, self.draws_per_turn):
                self.draw()

        # On the target turn, we only get a replace.
        if self.verbose:
            print(F"Turn {self.target_turn}:")
        self.replace()

        # We now have the odds of not having seen the desired card.
        # Subtract that from 1 to get our result.
        return (1 - self.fail_chance)



def main():
    """
    Calculate the odds of seeing a certain card by a certain turn number in Duelyst.

    Ask the user a number of questions to find the parameters of the simulation, then
    run it and print a friendly-looking percentage.
    """
    parser = argparse.ArgumentParser(description=(
        "Calculate the odds of seeing a certain card "
        "by a certain turn number in Duelyst."
    ))

    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")
    args = parser.parse_args()
    verbose = vars(args).get("verbose", False)

    trial_str = input("Does the deck contain a Trial card? (y/n)\n> ")
    trial = (trial_str == "y") or (trial_str == "Y")
    total_cards = 39 if trial else 40

    singleton_str = input("Is the deck singleton? (y/n)\n> ")
    singleton = (singleton_str == "y") or (singleton_str == "Y")

    if not singleton:
        copies = int(input("How many copies of this card are in the deck?\n> "))
    else:
        copies = 1

    target_turn = int(input("Which turn do you want to play the card on?\n> "))
    draws_str = input("Do you want to use 2-draw? (y/n)\n> ")
    two_draw = (draws_str == "y") or (draws_str == "Y")
    draws_per_turn = 2 if two_draw else 1

    simulator = DuelystDrawSimulator(
        total_cards,
        singleton,
        copies,
        target_turn,
        draws_per_turn,
        verbose=verbose
    )
    success_chance = simulator.run()

    percentage = success_chance * 100
    percentage = round(percentage, 3)
    print(
        F"The chance of drawing at least one copy of this card "
        F"by turn {target_turn} is {percentage}%."
    )


if __name__ == "__main__":
    main()
