import arcade
import settings

class Card(arcade.Sprite):
    """ Card sprite """

    def __init__(self, suit, value, scale=1):
        """ Card constructor """

        # Attributes for suit and value
        self.suit = suit
        self.value = value
        self.value_index = settings.CARD_VALUES.index(self.value)
        self.history={}
        # Image to use for the sprite when face up
        self.image_file_name = f":resources:images/cards/card{self.suit}{self.value}.png"
        self.is_face_up = False
        super().__init__(settings.FACE_DOWN_IMAGE, scale, hit_box_algorithm="None")

    def add_to_history(self, move_no, pile_index=None, position=None, flipped=False):
        self.history[move_no] = [position, pile_index, flipped]
        
    def face_down(self):
        """ Turn card face-down """
        self.texture = arcade.load_texture(settings.FACE_DOWN_IMAGE)
        self.is_face_up = False

    def face_up(self):
        """ Turn card face-up """
        self.texture = arcade.load_texture(self.image_file_name)
        self.is_face_up = True

    def get_suit_encoded(self):
        return settings.CARD_SUITS_ENCODED[self.suit]
    
    def get_value_encoded(self):
        return settings.CARD_VALUES_ENCODED[self.value]

    @property
    def is_face_down(self):
        """ Is this card face down? """
        return not self.is_face_up
