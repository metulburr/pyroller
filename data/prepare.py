"""
This module initializes the display and creates dictionaries of resources.
"""
import os
import pygame as pg
from . import tools
from . import events


CAPTION = "Py Rollers Casino"
START_SIZE = (928, 696)
RENDER_SIZE = (1400, 1050)
RESOLUTIONS = [(600,400),(800, 600), (928, 696), (1280, 960), (1400, 1050)]
CARD_SIZE = (125, 181)
CHIP_SIZE = (32, 19)
WIN_POS = (0,0)
MONEY = 999
ARGS = tools.get_cli_args(CAPTION, WIN_POS, START_SIZE, MONEY)
#adjust settings based on args
START_SIZE = int(ARGS['size'][0]), int(ARGS['size'][1])
MONEY = int(ARGS['money'])
DEBUG = bool(ARGS['debug'])

BACKGROUND_BASE = (5, 5, 15) #Pure Black is too severe.
FELT_GREEN = (0, 153, 51) #Use this if making a standard table-style game.

#Pre-initialize the mixer for less delay before a sound plays
pg.mixer.pre_init(44100, -16, 1, 512)

#Initialization
pg.init()
if ARGS['center']:
    os.environ['SDL_VIDEO_CENTERED'] = "True"
else:
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(*ARGS['winpos'])
pg.display.set_caption(CAPTION)
if ARGS['fullscreen']:
    pg.display.set_mode(START_SIZE, pg.FULLSCREEN)
else:
    pg.display.set_mode(START_SIZE, pg.RESIZABLE)
    pg.event.clear(pg.VIDEORESIZE)


def _get_graphics_and_cards():
    """
    Load all graphics into a dictionary; then cut up the card sprite sheet
    so each card can be accessed individually. Also strips buttons from
    button sheet. Placed in a function to avoid adding unnecessary names to the
    prepare namespace.
    """
    gfx = tools.load_all_gfx(os.path.join("resources", "graphics"))
    card_width = 125
    card_height = 181
    sheet = gfx["cardsheet"]
    card_names = ["ace", 2, 3, 4, 5, 6, 7, 8, 9, 10, "jack", "queen", "king"]
    top = 0
    for suit in ["clubs", "hearts", "diamonds", "spades"]:
        left = 0
        for name in card_names:
            rect = pg.Rect(left, top, card_width, card_height)
            key = "{}_of_{}".format(name, suit)
            gfx[key] = sheet.subsurface(rect)
            left += card_width
        top += card_height
    b_width = 318
    b_height = 101
    b_sheet = gfx["button_sheet"]
    b_texts = ["Bingo", "Blackjack", "Craps", "Keno", "Credits", "Exit",
               "Stats", "Lobby", "New", "Load", "Again", "Deal", "Hit",
               "Stand", "Split", "Double", "Roll", "Back", "OK", "Cancel"]
    b_top = 0
    for text in b_texts:
        off_rect = pg.Rect(0, b_top, b_width, b_height)
        on_rect = off_rect.move(b_width, 0)
        off_key = "neon_button_off_{}".format(text.lower())
        on_key = "neon_button_on_{}".format(text.lower())
        gfx[off_key] = b_sheet.subsurface(off_rect)
        gfx[on_key] = b_sheet.subsurface(on_rect)
        b_top += b_height
    return gfx


#Resource loading (Fonts and music just contain path names).
FONTS = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC = tools.load_all_music(os.path.join("resources", "music"))
SFX   = tools.load_all_sfx(os.path.join("resources", "sound"))
GFX   = _get_graphics_and_cards()


#It's time to start the music, it's time to light the lights
pg.mixer.music.load(MUSIC["main_stem"])
pg.mixer.music.set_volume(.2)
if not ARGS["music_off"]:
    pg.mixer.music.play()

# Singleton to broadcast events throughout the game
BROADCASTER = events.Broadcaster()