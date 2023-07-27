import random

# Class to represent the card
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def show(self):
        print(f'{self.value} of {self.suit}')

    def get_value(self):
        if self.value.isnumeric():
            return int(self.value)
        elif self.value in ['J', 'Q', 'K']:
            return 10
        else:  # value is 'A'
            return 11 if self.value == 'A' else 1

# Class to represent the deck
class Deck:
    def __init__(self, num_decks):
        self.cards = []
        self.build(num_decks)

    def build(self, num_decks):
        suits = ['Spades', 'Clubs', 'Diamonds', 'Hearts']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        for _ in range(num_decks):
            for suit in suits:
                for value in values:
                    self.cards.append(Card(suit, value))
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop()

# Class to represent the player
class Player:
    def __init__(self, name, deck, initial_amount=1000):
        self.name = name
        self.deck = deck
        self.hand = []
        self.split_hands = []  # A list to keep track of split hands
        self.score = 0
        self.ace_count = 0
        self.card_count = 0
        self.total_cards_dealt = 0
        self.wallet = initial_amount

    def split(self):
        if len(self.hand) != 2:
            print('You can only split on your first two cards.')
            return False
        if self.hand[0].get_value() != self.hand[1].get_value():
            print('You can only split a pair.')
            return False
        if len(self.split_hands) == 3:
            print('You can only split up to three times.')
            return False

        self.split_hands.append([self.hand.pop()])  # Split the pair into two hands
        self.draw(count=False).draw(count=False)  # Draw two new cards, one for each hand
        print('You have split your hand.')
        return True

    def double_down(self):
        if len(self.hand) > 2:
            print('You can only double down on your first two cards.')
            return False
        if self.wallet < 2 * self.bet:
            print('You don\'t have enough money to double down.')
            return False

        self.wallet -= self.bet  # Double the bet
        self.draw()  # Draw one more card
        print('You have doubled down.')
        return True

    def draw(self, count=True):
        if len(self.deck.cards) == 0:
            self.deck = Deck(6)
            print("The shoe was shuffled.")
        card = self.deck.draw_card()
        self.hand.append(card)
        self.total_cards_dealt += 1
        if card.value == 'A':
            self.ace_count += 1
        if count:  # Only update count if it's visible to the player
            self.update_count(card)
        self.update_score(card)
        return self

    def update_score(self, card):
        # Updating score based on card value
        if card.value.isnumeric():
            self.score += int(card.value)
        elif card.value in ['J', 'Q', 'K']:
            self.score += 10
        else:  # value is 'A'
            self.score += 11 if self.score <= 10 else 1

    def update_count(self, card):
        # Updating running count based on card value
        if card.value in ['2', '3', '4', '5', '6']:
            self.card_count += 1
            count_comment = "Low card. Count goes up."
        elif card.value in ['7', '8', '9']:
            count_comment = "Neutral card. Count stays the same."
        else:  # card.value is '10', 'J', 'Q', 'K' or 'A'
            self.card_count -= 1
            count_comment = "High card. Count goes down."
        print(count_comment)  # Comment on why the count is what it is

    def get_true_count(self):
        # Estimating the number of decks remaining in the shoe
        total_cards = 6 * 52  # As we're using 6 decks and each deck has 52 cards
        cards_remaining = total_cards - self.total_cards_dealt
        decks_remaining = cards_remaining / 52

        # Calculate the true count
        true_count = self.card_count / decks_remaining
        return round(true_count, 2)  # Rounded to 2 decimal places for simplicity

    def show_hand(self):
        for card in self.hand:
            card.show()

    def show_score(self):
        print(f'{self.name} Score: {self.score}')

# Main game logic
def play_game():
    bet = 100  # The initial bet
    deck = Deck(6)
    player = Player('Player', deck, bet)
    dealer = Player('Dealer', deck, bet)

    while player.wallet > 0:  # Continue the game until the player's money runs out
        player.hand = []
        dealer.hand = []
        player.score = 0
        dealer.score = 0

        # Display the updated counts at the start of each round
        print('Updated Counts:')
        print('Running Count:', player.card_count)
        print('True Count:', player.get_true_count())
        print('\n')

        # Ask for the bet amount
        bet = int(input(f'You have {player.wallet} in your wallet. Enter your bet amount: '))

        # Initial draw
        player.draw()
        dealer.draw(count=False)  # Dealer's hole card isn't visible to the player, so don't count it
        player.draw()
        dealer.draw()

        # Show the dealer's face-up card
        print("\nDealer's face-up card:")
        dealer.hand[1].show()  # The dealer's face-up card is the second card they drew

        while True:
            print(f'\n{player.name}\'s turn:')
            player.show_hand()
            player.show_score()
            print('Running Count:', player.card_count)
            print('True Count:', player.get_true_count())

            action = input('What would you like to do? (hit/stand/double/split) ')
            if action.lower() == 'hit':
                player.draw()
                if player.score > 21:
                    print('Bust!')
                    player.wallet -= bet
                    break
            elif action.lower() == 'stand':
                break
            elif action.lower() == 'double':
                if not player.double_down():
                    continue  # If the player couldn't double down, let them choose another action
                break  # If the player doubled down, end their turn
            elif action.lower() == 'split':
                if not player.split():
                    continue  # If the player couldn't split, let them choose another action

        if player.score <= 21:
            print(f'\n{dealer.name}\'s hole card:')
            dealer.hand[0].show()  # Reveal the dealer's hole card
            player.update_count(dealer.hand[0])  # Now that the hole card is revealed, add it to the count
            dealer.update_score(dealer.hand[0])  # Update the dealer's score now that the hole card is revealed

            while dealer.score < 17:
                print(f'\n{dealer.name}\'s turn:')
                dealer.draw()
                dealer.show_hand()
                dealer.show_score()
                if dealer.score > 21:
                    print('Dealer busts!')
                    player.wallet += bet
                    break

        # Determine winner outside of the condition
        print(f'\nFinal Scores:\n{player.name}: {player.score}\n{dealer.name}: {dealer.score}')
        if player.score > 21:  # Player bust
            print(f'{dealer.name} wins!')
            player.wallet -= bet
        elif dealer.score > 21:  # Dealer bust
            print(f'{player.name} wins!')
            player.wallet += bet
        elif player.score > dealer.score:  # No one busts, but player score is higher
            print(f'{player.name} wins!')
            player.wallet += bet
        elif player.score < dealer.score:  # No one busts, but dealer score is higher
            print(f'{dealer.name} wins!')
            player.wallet -= bet
        else:  # Scores are the same
            print('It\'s a draw!')

        # Ask the player if they want to play another round
        play_again = input('Do you want to play again? (yes/no) ')
        if play_again.lower() != 'yes':
            break

# Let's play!
play_game()
