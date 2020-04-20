import pyglet
from ..common.gameutils import AbaloneUtils

class Header:

    DISPLAYED_INFO = [
        "Player",
        "Episode",
        "Turns",
        "State",
        "Score"
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

    def __init__(self, game, theme, batch, groups):
        
        self.game = game
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

        #AbaloneUtils.load_fonts()

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

    def update(self):
        infos_tuple = [None] * len(Header.DISPLAYED_INFO)
        infos_tuple[0] = self.theme["players_name"][self.game.current_player]
        infos_tuple[1] = self.game.episode
        infos_tuple[2] = self.game.turns_count
        infos_tuple[3] = 'ON GOING' if not self.game.game_over else 'OVER'
        infos_tuple[4] = " : ".join([f'{self.theme["players_name"][p][0].upper()} {self.game.players_victories[p]}' 
                                     for p in range(self.game.players)])
        self.draw(infos_tuple)
