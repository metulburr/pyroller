import os
import json
import pygame as pg

from .. import tools, prepare
from ..components.labels import Label, GameButton, NeonButton, ButtonGroup
from ..components.flair_pieces import ChipCurtain


CURTAIN_SETTINGS = {"single_color" : True,
                    "start_y" : prepare.RENDER_SIZE[1]-5,
                    "scroll_speed" : 0.05,
                    "cycle_colors" : True,
                    "spinner_settings" : {"variable" : False,
                                          "frequency" : 120}}


class LobbyScreen(tools._State):
    """
    This state represents the casino lobby where the player can choose
    which game they want to play or view their game statistics. This is also
    the exit point for the game.
    """
    def __init__(self):
        super(LobbyScreen, self).__init__()
        screen_rect = pg.Rect((0, 0), prepare.RENDER_SIZE)
        self.games = [("Bingo", "BINGO"), ("Blackjack", "BLACKJACK"),
                      ("Craps", "CRAPS"), ("Keno", "KENO"),
                      ("video_poker", "VIDEOPOKER"), ("Pachinko", "PACHINKO")]
        game_buttons = self.make_game_buttons(screen_rect)
        navigation_buttons = self.make_navigation_buttons(screen_rect)
        self.buttons = ButtonGroup(game_buttons, navigation_buttons)
        self.chip_curtain = None #Created on startup.

    def make_game_buttons(self, screen_rect):
        columns = 3
        size = GameButton.ss_size
        spacer_x, spacer_y = 50, 100
        start_x = (screen_rect.w-size[0]*columns-spacer_x*(columns-1))//2
        start_y = screen_rect.top+130
        step_x, step_y = size[0]+spacer_x, size[1]+spacer_y
        buttons = ButtonGroup()
        for i,data in enumerate(self.games):
            game,payload = data
            y,x = divmod(i, columns)
            pos = (start_x+step_x*x, start_y+step_y*y)
            GameButton(pos, game, self.start_game, payload, buttons)
        return buttons

    def make_navigation_buttons(self, screen_rect):
        buttons = ButtonGroup()
        pos = (9, screen_rect.bottom-(NeonButton.height+11))
        NeonButton(pos, "Credits", self.change_state, "CREDITSSCREEN", buttons)
        pos = (screen_rect.right-(NeonButton.width+10),
               screen_rect.bottom-(NeonButton.height+11))
        NeonButton(pos, "Stats", self.change_state, "STATSMENU", buttons)
        pos = (screen_rect.centerx-(NeonButton.width//2),
               screen_rect.bottom-(NeonButton.height+11))
        NeonButton(pos, "Exit", self.exit_game, None, buttons)
        return buttons

    def start_game(self, chosen_game):
        self.done = True
        self.next = chosen_game

    def startup(self, current_time, persistent):
        self.persist = persistent
        if not self.chip_curtain:
            self.chip_curtain = ChipCurtain(None, **CURTAIN_SETTINGS)

    def exit_game(self, *args):
        with open(os.path.join("resources", "save_game.json"), "w") as f:
            json.dump(self.persist["casino_player"].stats, f)
        self.done = True
        self.quit = True

    def change_state(self, next_state):
        self.done = True
        self.next = next_state

    def get_event(self, event, scale=(1,1)):
        if event.type == pg.QUIT:
            self.exit_game()
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.exit_game()
        self.buttons.get_event(event)

    def update(self, surface, keys, current_time, dt, scale):
        mouse_pos = tools.scaled_mouse_pos(scale)
        self.chip_curtain.update(dt)
        self.buttons.update(mouse_pos)
        self.draw(surface)

    def draw(self, surface):
        surface.fill(prepare.BACKGROUND_BASE)
        self.chip_curtain.draw(surface)
        self.buttons.draw(surface)
