"""
Solitaire clone
"""
import arcade
import cards
import settings
import random
import arcade.gui 
import gymnasium as gym

class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()
        self.game_over = False
        # Creating a UI MANAGER to handle the UI 
        self.uimanager = arcade.gui.UIManager() 
        self.uimanager.enable()
        # Creating Button using UIFlatButton 
        button = arcade.gui.UIFlatButton(text="Show moves", 
                                               width=100) 
        # Adding button in our uimanager 
        self.uimanager.add( 
            arcade.gui.UIAnchorWidget( 
                anchor_x="right", 
                anchor_y="bottom", 
                child=button))
        
        @button.event("on_click")
        def on_click_button(event):
            print("Showing moves")
            # Show possible moves
            possible_moves = self.get_possible_moves()
            screen = MovesView(self, possible_moves)
            self.window.show_view(screen)

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

        # Create the mat for the bottom face down pile
        pile = arcade.SpriteSolidColor(settings.MAT_WIDTH, settings.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = settings.START_X, settings.BOTTOM_Y
        self.pile_mat_list.append(pile)

        # Create the 10 piles
        for i in range(10):
            pile = arcade.SpriteSolidColor(settings.MAT_WIDTH, settings.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = settings.START_X + i * settings.X_SPACING, settings.TOP_Y
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
        
        # Shuffle the cards
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)

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

        # Load the start view
        start_screen = StartView(self)
        self.window.show_view(start_screen)          

    def pull_to_top(self, card: arcade.Sprite):
        """ Pull card to top of rendering order (last to render, looks on-top) """
        # Remove, and append to the end
        self.card_list.remove(card)
        self.card_list.append(card)

    def on_draw(self):
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
        # Drawing our ui manager 
        self.uimanager.draw() 

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)
        
        # Have we clicked on a card?
        if len(cards) > 0:
            # Might be a stack of cards, get the top one
            primary_card = cards[-1]
            # Figure out what pile the card is in
            pile_index = self.get_pile_for_card(primary_card)

            # Are we clicking on the bottom deck, to deal cards on top?
            if pile_index == settings.BOTTOM_FACE_DOWN_PILE:
                for pile_index in range(settings.PLAY_PILE_1, settings.PLAY_PILE_10 + 1):
                    pile = self.piles[pile_index]
                    if pile and self.piles[settings.BOTTOM_FACE_DOWN_PILE]:
                        last_card = pile[-1]
                        card = self.piles[settings.BOTTOM_FACE_DOWN_PILE][-1]
                        # Flip face up
                        card.face_up()
                        # Move card to position
                        card.position = last_card.center_x, last_card.center_y - settings.CARD_VERTICAL_OFFSET
                        # Remove card from face down pile
                        self.piles[settings.BOTTOM_FACE_DOWN_PILE].remove(card)
                        # Add card to correct pile
                        self.move_card_to_new_pile(card, pile_index)
                        # Put on top draw-order wise
                        self.pull_to_top(card)

            else:
                # All other cases, grab the face-up card we are clicking on
                self.held_cards = [primary_card]
                # Save the position
                self.held_cards_original_position = [self.held_cards[0].position]
                # Put on top in drawing order
                self.pull_to_top(self.held_cards[0])

                # Is this a stack of cards? If so, grab the other cards too
                card_index = self.piles[pile_index].index(primary_card)
                for i in range(card_index + 1, len(self.piles[pile_index])):
                    card = self.piles[pile_index][i]
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
                        for remaining_card in self.piles[pile_index][i:]:
                            self.pull_to_top(remaining_card)
                        break
        
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

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return
        
        # Find the closest pile, in case we are in contact with more than one
        pile, pile_index = self.get_closest_sprite(self.held_cards[0])
        reset_position = True

        #  the pile from where the clicked card came from
        last_pile_index = self.get_pile_for_card(self.held_cards[0])

        # See if we are in contact with the closest pile or the last card in the pile and in accordance with the rules
        if arcade.check_for_collision(self.held_cards[0], pile) and self.is_placable(pile_index):

            #  Is it the same pile we came from?
            if pile_index == last_pile_index:
                # If so, who cares. We'll just reset our position.
                pass

            # Is it on a middle play pile?
            elif settings.PLAY_PILE_1 <= pile_index <= settings.PLAY_PILE_10:
                # Are there already cards there?
                if len(self.piles[pile_index]) > 0:
                    # Move cards to proper position
                    top_card = self.piles[pile_index][-1]
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = top_card.center_x, \
                                                top_card.center_y - settings.CARD_VERTICAL_OFFSET * (i + 1)
                else:
                    # Are there no cards in the middle play pile?
                    for i, dropped_card in enumerate(self.held_cards):
                        # Move cards to proper position
                        dropped_card.position = pile.center_x, \
                                                pile.center_y - settings.CARD_VERTICAL_OFFSET * i

                
                for card in self.held_cards:
                    # Cards are in the right position, but we need to move them to the right list
                    self.move_card_to_new_pile(card, pile_index)

                # Success, don't reset position of cards
                reset_position = False

                # Flip over top card
                if len(self.piles[last_pile_index]) > 0:
                    top_card = self.piles[last_pile_index][-1]
                    if not top_card.is_face_up:
                        top_card.face_up()
                        # Turning over a card adds 10 points
                        self.score += 10

                # Check if the move resulted in forming a stack
                sequence = self.stack_completed(pile_index)
                if sequence:
                    print("Stack completed")
                    # Remove stack from game
                    self.remove_stack(sequence)
                    # Add points
                    self.score += 130
                    # check if a card needs to be turned over
                    if len(self.piles[pile_index]) > 0:
                        top_card = self.piles[pile_index][-1]
                        if not top_card.is_face_up:
                            top_card.face_up()
                            # Turning over a card adds 10 points
                            self.score += 10
                    # check if the game is over
                    if len(self.piles[settings.FOUNDATION_PILE]) == 104:
                        self.game_over = True

        if reset_position:
            # Where-ever we were dropped, it wasn't valid. Reset the each card's position
            # to its original spot.
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # We are no longer holding cards
        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

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

    def on_key_press(self, symbol: int, modifiers: int):
        """ User presses key """
        if symbol == arcade.key.R:
            # Restart
            self.setup()

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
            # Load the end view
            end_screen = EndView(self)
            self.window.show_view(end_screen)

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
    

class StartView(arcade.View):
    """ View to show before the game starts """
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
    
    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.game_view.on_draw()

        arcade.draw_text("Click to start",
                         settings.SCREEN_WIDTH / 2,
                         settings.SCREEN_HEIGHT / 2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        self.window.show_view(self.game_view)

class EndView(arcade.View):
    """ View to show when the game ends """
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        #  draw mats
        self.game_view.pile_mat_list.draw()
        # Draw timer
        self.game_view.timer_text.draw()
        # Draw Score
        self.game_view.score_text.draw()
        #  draw cards
        self.game_view.card_list.draw()

        # Calculate minutes
        minutes = int(self.game_view.total_time) // 60
        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.game_view.total_time) % 60
        # Calculate 100s of a second
        seconds_100s = int((self.game_view.total_time - seconds) * 100)
        # Use string formatting to create a new text string for our timer
        timer_text = f"{minutes:02d}:{seconds:02d}:{seconds_100s:02d}"

        arcade.draw_text("Click to re-start the game. "
                         "Your score was {} with time {}".format(int(self.game_view.score), timer_text),
                         settings.SCREEN_WIDTH / 2,
                         settings.SCREEN_HEIGHT / 2,
                         arcade.color.BLACK,
                         font_size=20,
                         multiline=True,
                         anchor_x="center",
                         width=375)
    
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, re-start the game. """
        game = GameView()
        game.setup()
        self.window.show_view(game)

class MovesView(arcade.View):
    """View for displaying possible moves to a player"""
    def __init__(self, game_view, possible_moves):
        super().__init__()
        self.game_view = game_view
        self.moves = possible_moves
        self.time_span = 3
        self.total_time = 0
        self.shown_moves = {}
        self.item = None
        self.key = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()
        #  draw mats
        self.game_view.pile_mat_list.draw()
        # Draw timer
        self.game_view.timer_text.draw()
        # Draw Score
        self.game_view.score_text.draw()
        #  draw cards
        self.game_view.card_list.draw()

        if self.item is not None and self.key is not None and self.key !=self.item:
            # Draw an orange rectangle on position to place key
            arcade.draw_rectangle_outline(self.item.position[0],
                                        self.item.position[1], 
                                        width=settings.CARD_WIDTH+3,
                                        height=settings.CARD_HEIGHT+3,
                                        color=arcade.color.RED,
                                        border_width=3)
            # Draw an yellow rectangle around key
            arcade.draw_rectangle_outline(self.key.position[0],
                                        self.key.position[1], 
                                        width=settings.CARD_WIDTH+3,
                                        height=settings.CARD_HEIGHT+3,
                                        color=arcade.color.YELLOW,
                                        border_width=3)
    
    def on_update(self, delta_time: float):
        # Take the first value pair in the moves dict
        if self.moves.keys():
            key = list(self.moves.keys())[0]
            # list of possible new positions
            items = self.moves[key]
            # Draw the possible move
            if items and self.time_span > 3:
                # Take a single possible move
                item = items.pop(0)
                self.item = item
                self.key = key
                # Draw that move
                self.on_draw()
                # Reset timer
                self.time_span = 0
            if not items and self.time_span > 3:
                # No more moves for that key. Remove from dict
                self.moves.pop(key)
        else: 
            # No more moves to show. Switch back to game
            self.window.show_view(self.game_view)

        self.time_span += delta_time
        # Update game timer
        # Accumulate the total time
        self.game_view.total_time += delta_time
        # Calculate minutes
        minutes = int(self.game_view.total_time) // 60
        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.game_view.total_time) % 60
        # Calculate 100s of a second
        seconds_100s = int((self.game_view.total_time - seconds) * 100)
        # Use string formatting to create a new text string for our timer
        self.game_view.timer_text.text = f"{minutes:02d}:{seconds:02d}:{seconds_100s:02d}"
                
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, stop showing possible moves. """
        self.window.show_view(self.game_view)

def main():

    """ Main function """
    window = arcade.Window(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, settings.SCREEN_TITLE)
    start_view = GameView()
    window.show_view(start_view)
    start_view.setup()
    arcade.run()


if __name__ == "__main__":
    main()