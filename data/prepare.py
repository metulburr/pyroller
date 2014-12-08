"""
This module initializes the display and creates dictionaries of resources.
"""

import os
import pygame as pg
from . import tools


ORIGINAL_CAPTION = "Py Roller Casino"
START_SIZE = (1024, 768)
RENDER_SIZE = (1400, 1050)
RESOLUTIONS = [(800, 600), (1024, 768), (1280, 960), (1400, 1050)]
CARD_SIZE = (125, 181)
CHIP_SIZE = (32, 32)

#Pre-initialize the mixer for less delay before a sound plays
pg.mixer.pre_init(44100, -16, 1, 512)


#Initialization
pg.init()
os.environ['SDL_VIDEO_CENTERED'] = "TRUE"
pg.display.set_caption(ORIGINAL_CAPTION)
pg.display.set_mode(START_SIZE, pg.RESIZABLE)
pg.event.clear(pg.VIDEORESIZE)


#Resource loading (Fonts and music just contain path names).
FONTS = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC = tools.load_all_music(os.path.join("resources", "music"))
SFX   = tools.load_all_sfx(os.path.join("resources", "sound"))
GFX   = tools.load_all_gfx(os.path.join("resources", "graphics"))

#It's time to start the music, it's time to light the lights
pg.mixer.music.load(MUSIC["main_stem"])
pg.mixer.music.set_volume(.2)
pg.mixer.music.play(-1)