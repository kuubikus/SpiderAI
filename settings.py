# Constants for sizing
CARD_SCALE = 0.6

# How big are the cards?
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

# How big is the mat we'll place the card on?
MAT_PERCENT_OVERSIZE = 1.25
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)

# How much space do we leave as a gap between the mats?
# Done as a percent of the mat size.
VERTICAL_MARGIN_PERCENT = 0.10
HORIZONTAL_MARGIN_PERCENT = 0.10

# The Y of the bottom row (2 piles)
BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The X of where to start putting things on the left side
START_X = MAT_WIDTH / 2 + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# Card constants
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_VALUES_ENCODED = {"A":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":11, "Q":12, "K":13}
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]
CARD_SUITS_ENCODED = {"Clubs":1, "Hearts":2, "Spades":3, "Diamonds":4}

# Screen title and size
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Drag and Drop Cards"

# Show moves button
BUTTON_X = SCREEN_WIDTH - 150
BUTTON_Y = SCREEN_HEIGHT - 100

# Face down image
FACE_DOWN_IMAGE = ":resources:images/cards/cardBack_red2.png"

# The Y of the top row (10 piles)
TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# How far apart each pile goes
X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# If we fan out cards stacked on each other, how far apart to fan them?
CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3

# Timer and score location
TIMER_X = SCREEN_WIDTH - 80
TIMER_Y = TOP_Y + MAT_HEIGHT / 2
SCORE_Y = TIMER_Y - 15

# Start and end screens


# Constants that represent "what pile is what" for the game
PILE_COUNT = 12
PLAY_PILE_1 = 0
PLAY_PILE_2 = 1
PLAY_PILE_3 = 2
PLAY_PILE_4 = 3
PLAY_PILE_5 = 4
PLAY_PILE_6 = 5
PLAY_PILE_7 = 6
PLAY_PILE_8 = 7
PLAY_PILE_9 = 8
PLAY_PILE_10 = 9
BOTTOM_FACE_DOWN_PILE = 10
FOUNDATION_PILE = 11
