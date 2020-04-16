import pyglet
from ..common.gameutils import AbaloneUtils

class Header:

    DISPLAYED_INFO = [
        "Player",
        "Episode",
        "Turns",
        "State"
    ]

    INFO_STYLE = {
        'font_name' : 'Arial',
        'font_size' : 12,
        'bold'      : True,
        'color'     : (255, 255, 255, 255),
        'anchor_x'  : 'left', 
        'anchor_y'  : 'center',
    }

    PADDING_X_0 = 10

    PADDING_X = 30 # pixel

    SEPARATORS = '|'

    def __init__(self, theme, batch, groups):
        self.theme = theme
        self.batch = batch
        self.groups = groups

        self.x0, self.y0 = 0, self.theme['dimension']['height']

        # display header background sprite
        im = AbaloneUtils.get_im_centered(self.theme['sprites']['header'], centered=False)
        sprite = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[0], x=self.x0, y=self.y0)
        self.header_sprite = sprite
        self.width, self.height = sprite.width, sprite.height

        self.infos_sprites = None
        self._init_sprites()

    def _init_sprites(self):
        self.infos_sprites = []
        for _ in range(len(Header.DISPLAYED_INFO)):
            info = pyglet.text.Label(batch=self.batch, group=self.groups[1], **Header.INFO_STYLE)
            self.infos_sprites.append(info)

    def draw(self, infos_tuple):
        #assert len(Header.DISPLAYED_INFO) == len(infos_tuple)
        x =  0
        y = self.y0 + self.height // 2

        for i, (info_name, info_data) in enumerate(zip(Header.DISPLAYED_INFO, infos_tuple)):
            x += (Header.PADDING_X if i>0 else Header.PADDING_X_0)

            displayed_string = " ".join((info_name, Header.SEPARATORS, str(info_data)))

            self.infos_sprites[i].text = displayed_string
            self.infos_sprites[i].x = x 
            self.infos_sprites[i].y = y

            x += self.infos_sprites[i].content_width

    def get_infos_tuple(self, game):
        infos_tuple = [None] * len(Header.DISPLAYED_INFO)
        infos_tuple[0] = self.theme["players_name"][game.current_player]
        infos_tuple[1] = game.episode
        infos_tuple[2] = game.turns_count
        infos_tuple[3] = 'ON GOING' if not game.game_over else 'OVER'
        return infos_tuple

    def update(self, game):
        infos_tuple = self.get_infos_tuple(game)
        self.draw(infos_tuple)