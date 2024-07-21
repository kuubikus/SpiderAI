"""
Solitaire clone
"""
import arcade
import cards
import settings
import random
import arcade.gui 
import gymnasium as gym
from gymnasium import spaces
import numpy as np

class GameView(arcade.View, gym.Env):
    """ Main application class. """
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, render_mode=None):
        super().__init__()
        self.game_over = False
        self.render_mode = render_mode
        # History
        self.no_of_moves_made = 0
        # Necessary to undo more than one turn
        self.undo_counter = -1
        # All visible mats with 104 cards in total
        self.observation_space = spaces.Box(low=0,high=52,shape=(settings.PILE_COUNT,104),dtype=np.int8)
        # Action space as move/deal/undo, move(source, destination)
        self.action_space = spaces.MultiDiscrete([3, 10, 10])
        # Reward
        self.reward = 0
        # History. A dictinary in the format key: source index, item: destiantion index
        self.history = {}

        # Timer set up
        self.total_time = 0.0
        self.timer_text = arcade.Text(
            text="00:00:00",
            start_x=settings.TIMER_X,
            start_y=settings.TIMER_Y,
            color=arcade.color.WHITE,
            font_size=10,
            anchor_x="center",
        )
        # Score set up
        self.score = 500
        self.score_text = arcade.Text(
            text=f"Score: {self.score}",
            start_x=settings.TIMER_X,
            start_y=settings.SCORE_Y,
            color=arcade.color.WHITE,
            font_size=10,
            anchor_x="center",
        )
        #  list of cards
        self.card_list = None
        arcade.set_background_color(arcade.color.AMAZON)
        #  cards being dragged
        self.held_cards = None
        #  og location
        self.held_cards_og_pos = None
        #  mats
        self.pile_mat_list = None
        #  a list of lists for each pile
        self.piles = None

    def place_cards(self, pile_no, i):
        for x in range(i):
            # Pop the card off the deck we are dealing from
            card = self.piles[settings.BOTTOM_FACE_DOWN_PILE].pop()
            # Put in the proper pile
            self.piles[pile_no].append(card)
            # Move card to same position as pile we just put it in
            if x == 0:
                card.position = self.pile_mat_list[pile_no].position
            else:
                last_card = self.piles[pile_no][-2]
                card.position = last_card.center_x, last_card.center_y - settings.CARD_VERTICAL_OFFSET
            # Put on top in draw order
            self.pull_to_top(card)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        self.game_over = False
        # Timer
        self.total_time = 0.0
        # Score
        self.score = 500
        #  cards being dragged
        self.held_cards = []
        self.held_cards_og_pos = []

        # ---  Create the mats the cards go on.

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Create the 10 piles
        for i in range(10):
            pile = arcade.SpriteSolidColor(settings.MAT_WIDTH, settings.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = settings.START_X + i * settings.X_SPACING, settings.TOP_Y
            self.pile_mat_list.append(pile)

        # Create the mat for the bottom face down pile
        pile = arcade.SpriteSolidColor(settings.MAT_WIDTH, settings.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = settings.START_X, settings.BOTTOM_Y
        self.pile_mat_list.append(pile)

        # Create foundation pile
        pile = arcade.SpriteSolidColor(settings.MAT_WIDTH, settings.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = settings.TIMER_X, settings.TIMER_Y/2
        self.pile_mat_list.append(pile)

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = arcade.SpriteList()

        # Create every card
        for x in range(2):
            for card_suit in settings.CARD_SUITS:
                for card_value in settings.CARD_VALUES:
                    card = cards.Card(card_suit, card_value, settings.CARD_SCALE)
                    card.position = settings.START_X, settings.BOTTOM_Y
                    self.card_list.append(card)
        
        """# Shuffle the cards
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)"""

        self.piles = [[] for x in range(settings.PILE_COUNT)]
        # Put all the cards in the bottom face-down pile
        for card in self.card_list:
            self.piles[settings.BOTTOM_FACE_DOWN_PILE].append(card)

        # - Pull from that pile into the middle piles, all face-down
        # Loop for each pile
        for pile_no in range(settings.PLAY_PILE_1, settings.PLAY_PILE_10 + 1):
            # Deal proper number of cards for that pile
            if pile_no < 6:
                # Deal 6 cards
                self.place_cards(pile_no,6)
            else:
                # Deal 5 cards
                self.place_cards(pile_no,5)
                
        # Flip up the top cards
        for i in range(settings.PLAY_PILE_1, settings.PLAY_PILE_10 + 1):
            self.piles[i][-1].face_up()          

    def pull_to_top(self, card: arcade.Sprite):
        """ Pull card to top of rendering order (last to render, looks on-top) """
        # Remove, and append to the end
        self.card_list.remove(card)
        self.card_list.append(card)

    def on_draw(self):
        if self.render_mode == "human":
            """ Render the screen. """
            #  Clear the screen
            self.clear()
            #  draw mats
            self.pile_mat_list.draw()
            # Draw timer
            self.timer_text.draw()
            # Draw Score
            self.score_text.draw()
            #  draw cards
            self.card_list.draw()
        else:
            pass
        
    def get_last_cards(self, card_in_hand):
        """ get a SpriteList of all last cards in a pile """
        pile_last_card_list: arcade.SpriteList = arcade.SpriteList()
        for pile in self.piles:
                #  if there is a last card
                if len(pile) > 0:
                    #  not the same as the one in hand
                    if pile[-1] != card_in_hand and pile[-1].is_face_up:
                        pile_last_card_list.append(pile[-1])
        return pile_last_card_list
    
    def get_playable_cards(self):
        """ 
        finds all the playable cards at a given state of the game. A playable card is one that can be moved.
        If it belongs to a moveable stack then it return the top card. The whole stack will  be moved.
        Function returns a list of all the cards.
        """
        playable_cards = []
        for pile in self.piles:
            # Not an empty pile
            if len(pile) > 0:
                sequence = []
                pile_face_up = [card for card in pile if card.is_face_up]
                for card_index in range(-1,-len(pile_face_up)-1,-1):
                    card = pile_face_up[card_index]
                    if len(sequence) > 0:
                        # If sequence valid then add card
                        if card.value_index - sequence[-1].value_index == 1 and card.suit == sequence[-1].suit:
                            sequence.append(card)
                        # If card can't be added then stop looking
                        else:
                            break
                    if len(sequence) == 0:
                        # first card
                        sequence.append(card)
                if sequence:  
                    playable_cards.append(sequence[-1])
        return playable_cards

    def is_placable(self, pile_index):
        #  check if there are cards in the pile
        if self.piles[pile_index]:
            last_card = self.piles[pile_index][-1]
            if last_card.value_index - self.held_cards[0].value_index == 1:
                return True
            else:
                return False
        else:
            return True

    def get_closest_sprite(self, card_in_hand):
        pile_from_mat, distance_from_mat = arcade.get_closest_sprite(card_in_hand, self.pile_mat_list)
        last_cards = self.get_last_cards(card_in_hand)
        if last_cards:
            pile_from_card, distance_from_card = arcade.get_closest_sprite(card_in_hand, last_cards)   # returns the nearest card but not the corresponding pile
            if distance_from_mat > distance_from_card:
                #  get the pile correspdonding to that card
                return pile_from_card, self.get_pile_for_card(pile_from_card)
        return pile_from_mat, self.pile_mat_list.index(pile_from_mat)

    def get_pile_for_card(self, card):
        """ What pile is this card in? """
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index
    
    def remove_card_from_pile(self, card):
        """ Remove card from whatever pile it was in. """
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def move_card_to_new_pile(self, card, pile_index):
        """ Move the card to a new pile """
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

    def stack_completed(self, pile_index):
        """ 
        Checks if the cards in a pile make up a foundation
        Return True if a foundation exists in a pile and the index of the King
        """
        sequence = []
        pile = self.piles[pile_index]
        pile_upwards = [card for card in pile if card.is_face_up]
        for card_index in range(-1,-len(pile_upwards)-1,-1):
            card = pile_upwards[card_index]
            if len(sequence) > 0:
                # If sequence valid then add card
                if card.value_index - sequence[-1].value_index == 1 and card.suit==sequence[-1].suit:
                    sequence.append(card)
                # If card can't be added then stop looking
                else:
                    sequence =[]
                    break

            # Check if the sequence has all the values 
            if len(sequence) == len(settings.CARD_VALUES):
                return sequence
            
            # Sequence is empty and the top card is an Ace
            if card.value == "A" and len(sequence) == 0:
                # Start the sequence
                sequence.append(card)

        sequence = []
        return sequence
    
    def remove_stack(self, sequence):
        # A stack has already been removed
        if self.piles[settings.FOUNDATION_PILE]:
            # Get the top card from previous stack
            previous_top_card = self.piles[settings.FOUNDATION_PILE][-1]
            # Place new stack on top the old stack with an offset 
            for card in sequence:
                card.position = previous_top_card.position[0], previous_top_card.position[1] - settings.CARD_VERTICAL_OFFSET
                self.pull_to_top(card)
                self.move_card_to_new_pile(card, settings.FOUNDATION_PILE)
        else:
            # Place new stack on top of the mat
            for card in sequence:
                card.position = self.pile_mat_list[settings.FOUNDATION_PILE].position
                self.pull_to_top(card)
                self.move_card_to_new_pile(card, settings.FOUNDATION_PILE)

    def on_update(self, delta_time):
        # Reset reward for action
        self.reward = 0
        # Accumulate the total time
        self.total_time += delta_time
        # Calculate minutes
        minutes = int(self.total_time) // 60
        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.total_time) % 60
        # Calculate 100s of a second
        seconds_100s = int((self.total_time - seconds) * 100)
        # Use string formatting to create a new text string for our timer
        self.timer_text.text = f"{minutes:02d}:{seconds:02d}:{seconds_100s:02d}"
        # Update score text
        self.score_text.text = f"Score: {self.score}"
        # Check if the game is over
        if self.game_over and len(self.piles[settings.FOUNDATION_PILE]) == 104:
            print("Game is done")
            self.score += 1000000/self.total_time
            self.reward = 1000000

        """if test_actions:
            action = test_actions.pop(0)
            print(action)
            next_state, reward, done, eh, info = self.step(action)
            print(f"Reward: {reward}, Done: {done}")
            print(f"The score is {self.score}")
            if not test_actions:
                self.game_over = True"""
        """if self.total_time > 2 and self.total_time < 3:
            print("writing to file")
            array_flattened = self.get_observations().reshape(-1, self.get_observations().shape[-1])
            np.savetxt("array_of_zeros.txt", array_flattened, fmt='%d')"""
        
    
    def get_possible_moves(self):
        """
        Returns a dictionray of possible moves. The key is the card that can be played. 
        The item is a list of cards that the key card can be placed on.
        """
        possible_moves = {}
        all_last_cards = self.get_last_cards(None)
        all_playable_cards = self.get_playable_cards()
        # Check each playable card against top cards in a pile
        for playable_card in all_playable_cards:
            possible_moves[playable_card] = []
            for last_card in all_last_cards:
                # Check accordance with the rules
                if last_card.value_index - playable_card.value_index == 1:
                    possible_moves[playable_card].append(last_card)
        return possible_moves
    
    # For  gymnasium
    def get_observations(self):
        """
        Returns observations as a 2D numpy array. Each row is a pile in the game. Cards are represented as a tuple (encoded value, encoded suit).
        If the card is not visible then it is 0.
        """
        observations = np.zeros(shape=(settings.PILE_COUNT, 104,2))
        for pile_index, pile in enumerate(self.piles):
            for card_index, card in enumerate(pile):
                if card.is_face_up:
                    observations[pile_index,card_index] = [card.get_value_encoded(), card.get_suit_encoded()]
                else:
                    observations[pile_index,card_index] = [-1,-1]
        return observations
    
    def reset(self):
        """
        Gymnasium API for initializing/resetting the game
        """
        self.setup()
        observation = self.get_observations()
        return observation, {}
    
    def move_card(self, source_pile_index, destination_pile_index):
        """
        Move a card (source) on top a last card in a pile or empty pile (destinaion)
        INPUTS: source: pile index for the card(s) to be moved from
                destination: pile index for the card(s) to be moved to
        """
        # Get all playable cards (along with stacks)
        playable_cards = self.get_playable_cards()

        for playable_card in playable_cards: 
            # Find a card that corresponds to the one we want to move
            if self.get_pile_for_card(playable_card) == source_pile_index:
                self.held_cards = [playable_card]
                break

        source = self.held_cards[0]
        print(f"Moving card with value {source.value} and suit {source.suit} to pile {destination_pile_index}")
        reset_position = True
        # Save the position
        self.held_cards_original_position = [self.held_cards[0].position]
        # Put on top in drawing order
        self.pull_to_top(self.held_cards[0])
        
        # Is this a stack of cards? If so, grab the other cards too
        card_index = self.piles[source_pile_index].index(source)
        for i in range(card_index + 1, len(self.piles[source_pile_index])):
            card = self.piles[source_pile_index][i]
            previous_card = self.held_cards[-1]
            # Check if accordance with rules
            if previous_card.value_index - card.value_index == 1 and previous_card.suit == card.suit:
                self.held_cards.append(card)
                self.held_cards_original_position.append(card.position)
                self.pull_to_top(card)
            else:
                # The stack is not moveable according to rules
                self.held_cards = []
                # Pull the remaining cards on top
                for remaining_card in self.piles[source_pile_index][i:]:
                    self.pull_to_top(remaining_card)
                break

        # Chech accordance with rules
        if self.is_placable(destination_pile_index):
            #  Is it the same pile we came from?
            if destination_pile_index == source_pile_index:
                # If so, who cares. We'll just reset our position.
                pass

            # Is it on a play pile?
            elif settings.PLAY_PILE_1 <= destination_pile_index <= settings.PLAY_PILE_10:
                # New action - reset undo counter
                self.undo_counter = -1
                # Are there already cards there?
                if len(self.piles[destination_pile_index]) > 0:
                    # Move cards to proper position
                    top_card = self.piles[destination_pile_index][-1]
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.add_to_history(self.no_of_moves_made, source_pile_index, self.held_cards_original_position[i])
                        dropped_card.position = top_card.center_x, \
                                                top_card.center_y - settings.CARD_VERTICAL_OFFSET * (i + 1)
                else:
                    # Are there no cards in the middle play pile?
                    for i, dropped_card in enumerate(self.held_cards):
                        # Move cards to proper position
                        dropped_card.add_to_history(self.no_of_moves_made, source_pile_index, self.held_cards_original_position[i])
                        dropped_card.position = self.piles[destination_pile_index][-1].center_x, \
                                                self.piles[destination_pile_index][-1].center_y - settings.CARD_VERTICAL_OFFSET * i

                
                for card in self.held_cards:
                    # Cards are in the right position, but we need to move them to the right list
                    self.move_card_to_new_pile(card, destination_pile_index)

                # Flip over top card
                if len(self.piles[source_pile_index]) > 0:
                    top_card = self.piles[source_pile_index][-1]
                    if not top_card.is_face_up:
                        top_card.face_up()
                        top_card.add_to_history(self.no_of_moves_made, flipped=True)
                        # Turning over a card adds 10 points
                        self.score += 10
                        self.reward += 10

                # Check if the move resulted in forming a stack
                sequence = self.stack_completed(destination_pile_index)
                if sequence:
                    print("Stack completed")
                    # Remove stack from game
                    self.remove_stack(sequence)
                    # Add points
                    self.score += 130
                    self.reward += 130
                    # check if a card needs to be turned over
                    if len(self.piles[destination_pile_index]) > 0:
                        top_card = self.piles[destination_pile_index][-1]
                        if not top_card.is_face_up:
                            top_card.face_up()
                            top_card.add_to_history(self.no_of_moves_made, flipped=True)
                            # Turning over a card adds 10 points
                            self.score += 10
                            self.reward += 10
                    # check if the game is over
                    if len(self.piles[settings.FOUNDATION_PILE]) == 104:
                        self.game_over = True

                # Success, don't reset position of cards
                reset_position = False
                # Add a reward for correct move
                self.reward += 1
                self.no_of_moves_made += 1

        if reset_position:
            print("Invalid move")
            # Where-ever we were dropped, it wasn't valid. Reset the each card's position
            # to its original spot.
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # We are no longer holding cards
        self.held_cards = []

    def step(self, action):
        action_type, source, destination = action
        # Move card action type
        if action_type == 0:
            self.move_card(source, destination)
        # Deal cards action type
        elif action_type == 1:
            # Deal cards
            # New action, reset undo counter
            self.undo_counter = -1
            # Figure out what pile the card is in
            self.reward -= 5
            self.score -= 10
            for pile_index in range(settings.PLAY_PILE_1, settings.PLAY_PILE_10 + 1):
                    pile = self.piles[pile_index]
                    if pile and self.piles[settings.BOTTOM_FACE_DOWN_PILE]:
                        last_card = pile[-1]
                        card = self.piles[settings.BOTTOM_FACE_DOWN_PILE][-1]
                        # Flip face up
                        card.face_up()
                        # Update history
                        card.add_to_history(self.no_of_moves_made, settings.BOTTOM_FACE_DOWN_PILE, card.position,True)
                        # Move card to position
                        card.position = last_card.center_x, last_card.center_y - settings.CARD_VERTICAL_OFFSET
                        # Remove card from face down pile
                        self.piles[settings.BOTTOM_FACE_DOWN_PILE].remove(card)
                        # Add card to correct pile
                        self.move_card_to_new_pile(card, pile_index)
                        # Put on top draw-order wise
                        self.pull_to_top(card)
                        
            self.no_of_moves_made += 1
        elif action_type == 2:
            self.undo_counter += 2
            print("Undo counter", self.undo_counter)
            self.undo(self.no_of_moves_made-self.undo_counter)
            self.no_of_moves_made += 1

        reward = self.reward
        observation = self.get_observations()
        return observation, reward, self.game_over, False, {}

    def undo(self, move_no):
        print("undo")
        for i in range(10,-1,-1):
            pile = self.piles[i]
            for j, card in enumerate(pile):
                if card.is_face_up:
                    if move_no in card.history.keys():
                        position, previous_pile_index, flipped = card.history[move_no]
                        if position is not None and previous_pile_index is not None:
                            # Move card
                            card.position = position
                            # Update pile
                            self.move_card_to_new_pile(card,previous_pile_index)
                            # Update card history
                            card.add_to_history(self.no_of_moves_made, previous_pile_index, card.position)
                        if flipped:
                            card.face_down()
                            self.reward -= 10

# For movement and drawing cards
#test_actions = [(1,0,0), (1,0,0),(0,1,0),(0,2,0),(0,3,0),(0,4,0),(0,5,0),(0,6,0),(0,7,0),(0,8,0),(0,9,0),(0,0,9),(1,0,0),(0,9,8),(0,1,0),(0,0,9)]
# For Undo
test_actions = [(0,2,4),(0,4,2),(2,0,0),(0,4,2),(0,0,2),(1,0,0),(0,2,1),(2,0,0),(2,0,0),(2,0,0)]

def main():
    """ Main function """
    window = arcade.Window(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, settings.SCREEN_TITLE)
    # Set frame rate
    # Agent makes a decision at each frame
    window.set_update_rate(1)
    env = GameView(render_mode="human")
    window.show_view(env)
    env.reset()
    arcade.run()
    
if __name__ == "__main__":
    main()