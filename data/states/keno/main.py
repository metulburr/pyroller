import random
import pygame as pg
from ...components.loggable import getLogger
from ...components.warning_window import NoticeWindow
from ...components.labels import Label, MultiLineLabel, NeonButton, ButtonGroup
from ... import tools, prepare

# Utilize the logger along with the following functions to print to console instead of prints.
log = getLogger("KENO")
#log.debug("testing debug log")
#log.info("testing info log")
#log.error("testing error log")

#http://casinogamblingtips.info/tag/pay-table
PAYTABLE = [
    [(0, 0)], #0
    [(1, 3)], #1
    [(2, 12)], #2
    [(2, 1), (3, 40)], #3
    [(2, 1), (3, 2), (4, 120)], #4
    [(3, 1), (4, 18), (5, 800)], #5
    [(3, 1), (4, 3), (5, 80), (6, 1500)], #6
    [(4, 1), (5, 18), (6, 360), (7, 5000)], #7
    [(5, 10), (6, 75), (7, 1000), (8, 15000)], #8
    [(5, 4), (6, 35), (7, 250), (8, 3000), (9, 20000)], #9
    [(5, 2), (6, 15), (7, 100), (8, 1500), (9, 8000), (10, 25000)], #10
]

def pick_numbers(spot):
    numbers = []
    while len(numbers) < spot:
        number = random.randint(0, 79)
        if number not in numbers:
            numbers.append(number)
    return numbers

def is_winner(spot, hit):
    paytable = PAYTABLE[spot]
    for entry in paytable:
        if entry[0] == hit:
            return True
    return False

class Bet(object):
    def __init__(self, casino_player):
        self.rect = pg.Rect(682, 760, 150, 75)
        self.font = prepare.FONTS["Saniretro"]
        self.label = Label(self.font, 32, 'BET 1', 'gold3', {'center':(0,0)})
        self.label.rect.center = self.rect.center
        self.color = '#181818'
        self.casino_player = casino_player
        self.bet = 0
        self.is_paid = False

    def update(self, amount):
        #unsafe - can end up withdrawing beyond zero...
        #issue #75 (must cast to integer):
        self.casino_player.stats["cash"] -= int(amount)
        self.bet += amount
        self.is_paid = True

    def clear(self):
        self.is_paid = False
        self.bet = 0

    def result(self, spot, hit):
        if not self.is_paid:
            bet = self.bet
            self.bet = 0
            self.update(bet)

        paytable = PAYTABLE[spot]
        payment = 0.0
        for entry in paytable:
            if entry[0] == hit:
                payment = entry[1]

            if payment > 0.0:
                break

        winnings = payment * self.bet
        #issue #75 (must cast to integer):
        self.casino_player.stats["cash"] += int(winnings)
        #self.bet = 0
        log.info("Won: {0}".format(winnings))

        self.is_paid = False

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color(self.color), self.rect, 0)
        self.label.draw(surface)

class Clear(object):
    def __init__(self, card, bet_action):
        self.rect = pg.Rect(526, 760, 150, 75)
        self.font = prepare.FONTS["Saniretro"]
        self.label = Label(self.font, 32, 'CLEAR', 'gold3', {'center':(0,0)})
        self.label.rect.center = self.rect.center
        self.color = '#181818'
        self.card = card
        self.bet_action = bet_action

    def update(self):
        self.card.ready_play(clear_all=True)
        self.bet_action.clear()

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color(self.color), self.rect, 0)
        self.label.draw(surface)

class RoundHistory(object):
    '''Round history showing hits per round.'''
    def __init__(self, card):
        self.rect = pg.Rect(24, 200, 304, 554)
        self.font = prepare.FONTS["Saniretro"]
        self.color = '#181818'
        self.card = card

        self.header_labels = []
        self.header_labels.extend([Label(self.font, 32, 'ROUND', 'white', {'center':(100,224)})])
        self.header_labels.extend([Label(self.font, 32, 'HITS', 'white', {'center':(280,224)})])

        self.result_labels = []

        self.round_x = 100
        self.hit_x   = 280
        self.row_y   = 224+32

        self.rounds  = 1

    def update(self, spot, hits):
        if self.rounds % 17 == 0:
            self.rounds = 1
            self.result_labels = []
            self.row_y = 224+32

        color = "white"

        if is_winner(spot, hits):
            color = "gold3"

        self.result_labels.extend([Label(self.font, 32, str(self.rounds), color, {'center':(self.round_x, self.row_y)})])
        self.result_labels.extend([Label(self.font, 32, str(hits), color, {'center':(self.hit_x, self.row_y)})])
        self.row_y+=32
        self.rounds+=1

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color(self.color), self.rect, 0)

        for label in self.header_labels:
            label.draw(surface)

        for label in self.result_labels:
            label.draw(surface)

class PayTable(object):
    '''Paytable readout for desired spot count'''
    def __init__(self, card):
        self.rect = pg.Rect(1036, 200, 340, 554)
        self.font = prepare.FONTS["Saniretro"]
        self.color = '#181818'
        self.card = card

        self.header_labels = []
        self.header_labels.extend([Label(self.font, 32, 'HIT', 'white', {'center':(1080,224)})])
        self.header_labels.extend([Label(self.font, 32, 'WIN', 'white', {'center':(1280,224)})])

        self.pay_labels = []

    def update(self, spot, bet=1):
        self.pay_labels = []
        row = PAYTABLE[spot]
        hit_x = 1080
        win_x = 1280
        row_y = 224+32
        for entry in row:
            hit, win = entry
            win *= bet
            self.pay_labels.extend([Label(self.font, 32, str(hit), 'white', {'center':(hit_x, row_y)})])
            self.pay_labels.extend([Label(self.font, 32, str(win), 'white', {'center':(win_x, row_y)})])
            row_y+=32


    def draw(self, surface):
        pg.draw.rect(surface, pg.Color(self.color), self.rect, 0)

        for label in self.header_labels:
            label.draw(surface)

        for label in self.pay_labels:
            label.draw(surface)

class Play(object):
    '''plays a game of keno'''
    def __init__(self, card):
        self.rect = pg.Rect(838, 760, 156, 75)
        self.font = prepare.FONTS["Saniretro"]
        self.label = Label(self.font, 32, 'PLAY', 'gold3', {'center':(0,0)})
        self.label.rect.center = self.rect.center
        self.color = '#181818'
        self.card = card

    def update(self):
        numbers = pick_numbers(20)

        self.card.ready_play()
        for number in numbers:
            self.card.toggle_hit(number)

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color(self.color), self.rect, 0)
        self.label.draw(surface)

class QuickPick(object):
    '''random picks max(10) numbers for play'''
    def __init__(self, card):
        self.rect = pg.Rect(370, 760, 150, 75)
        self.font = prepare.FONTS["Saniretro"]
        self.label = Label(self.font, 32, 'QUICK PICK', 'gold3', {'center':(0,0)})
        self.label.rect.center = self.rect.center
        self.color = '#181818'
        self.card = card

    def update(self):
        self.card.reset()
        numbers = pick_numbers(10)

        for number in numbers:
            self.card.toggle_owned(number)

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color(self.color), self.rect, 0)
        self.label.draw(surface)


class KenoSpot(object):
    COLORS = {
        'open': '#181818',
        'owned': '#9c8013',
        'hit': '#eedb1e',
        'miss': '#690808',
    }

    """A spot on a Keno card."""
    def __init__(self, left, top, width, height, label):
        self.rect = pg.Rect(left, top, width, height)
        label.rect.center = self.rect.center
        self.label = label
        self.color = self.COLORS['open']

        self.owned = False
        self.hit   = False

    def reset(self):
        self.owned = False
        self.hit   = False
        self.update_color()

    def toggle_owned(self):
        self.owned = not self.owned
        self.update_color()

    def toggle_hit(self):
        self.hit = not self.hit
        self.update_color()

    def update_color(self):
        if self.owned:
            self.color = self.COLORS['owned']
        else:
            self.color = self.COLORS['open']

        if self.hit and self.owned:
            self.color = self.COLORS['hit']
        elif self.hit:
            self.color = self.COLORS['miss']

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color(self.color), self.rect, 0)
        self.label.draw(surface)

class KenoCard(object):
    def __init__(self):
        self.font = prepare.FONTS["Saniretro"]
        self.spots = []
        self.build()

    def build(self):
        font_size = 48
        text = "0"
        text_color = "white"
        rect_attrib = {'center':(0,0)}

        x_origin = 336
        x = x_origin
        y = 200
        for row in range(0,8):
            for col in range(1,11):
                text = str(col+(10*row))
                label = Label(self.font, font_size, text, text_color, rect_attrib)
                spot = KenoSpot(x, y, 64, 64, label)
                self.spots.extend([spot])
                x += 70
            y += 70
            x = x_origin

    def get_spot_count(self):
        count = 0
        for spot in self.spots:
            if spot.owned:
                count+=1
        return count

    def get_hit_count(self):
        count = 0
        for spot in self.spots:
            if spot.hit and spot.owned:
                count+=1
        return count

    def toggle_owned(self, number):
        self.spots[number].toggle_owned()

    def toggle_hit(self, number):
        self.spots[number].toggle_hit()

    def ready_play(self, clear_all=False):
        for spot in self.spots:
            spot.hit = False
            spot.update_color()

        if clear_all:
            for spot in self.spots:
                spot.owned = False
                spot.update_color()

    def reset(self):
        for spot in self.spots:
            spot.reset()

    def update(self, mouse_pos):
        for spot in self.spots:
            if spot.rect.collidepoint(mouse_pos):
                if (self.get_spot_count() < 10 and not spot.owned) or spot.owned:
                    spot.toggle_owned()


    def draw(self, surface):
        for spot in self.spots:
            spot.draw(surface)

class Keno(tools._State):
    """Class to represent a casino game."""
    def __init__(self):
        super(Keno, self).__init__()
        self.screen_rect = pg.Rect((0, 0), prepare.RENDER_SIZE)
        self.game_started = False
        self.font = prepare.FONTS["Saniretro"]

        self.mock_label = Label(self.font, 64, 'KENO [WIP]', 'gold3', {'center':(680,140)})

        b_width = 360
        b_height = 90
        side_margin = 10
        w = self.screen_rect.right - (b_width + side_margin)
        h = self.screen_rect.bottom - (b_height+15)
        self.buttons = ButtonGroup()
        NeonButton((w, h), "Lobby", self.back_to_lobby, None, self.buttons)

        self.keno_card = KenoCard()

        self.quick_pick = QuickPick(self.keno_card)
        self.play = Play(self.keno_card)

        self.spot_count_label = Label(self.font, 64, 'SPOT COUNT: 0', 'gold3', {'center':(640,700)})
        self.prev_spot_count = 0

        self.hit_count_label = Label(self.font, 64, 'HIT COUNT: 0', 'gold3', {'center':(640,764)})

        self.pay_table = PayTable(self.keno_card)
        self.pay_table.update(0)

        self.round_history = RoundHistory(self.keno_card)

        self.alert = None

    def back_to_lobby(self, *args):
        self.game_started = False
        self.done = True
        self.next = "LOBBYSCREEN"

    def startup(self, current_time, persistent):
        """This method will be called each time the state resumes."""
        self.persist = persistent
        #This is the object that represents the user.
        self.casino_player = self.persist["casino_player"]
        self.bet_action = Bet(self.casino_player)
        self.clear_action = Clear(self.keno_card, self.bet_action)

        self.casino_player.stats["Keno"]["games played"] += 1

    def get_event(self, event, scale=(1,1)):
        """This method will be called for each event in the event queue
        while the state is active.
        """
        if event.type == pg.QUIT and not self.alert:
            self.done = True
            self.next = "LOBBYSCREEN"
        elif event.type == pg.MOUSEBUTTONDOWN and not self.alert:
            #Use tools.scaled_mouse_pos(scale, event.pos) for correct mouse
            #position relative to the pygame window size.
            event_pos = tools.scaled_mouse_pos(scale, event.pos)
            log.info(event_pos) #[for debugging positional items]
            if self.bet_action.rect.collidepoint(event_pos):
                self.bet_action.update(1)
                spot_count = self.keno_card.get_spot_count()
                bet_amount = self.bet_action.bet
                self.pay_table.update(spot_count, bet_amount)

            if self.quick_pick.rect.collidepoint(event_pos):
                self.quick_pick.update()
                self.hit_count_label = Label(self.font, 64, 'HIT COUNT: 0', 'gold3', {'center':(640,764)})

            if self.play.rect.collidepoint(event_pos):
                if self.bet_action.bet <= 0:
                    self.alert = NoticeWindow(self.screen_rect.center, "Please place your bet.")
                    return

                spot_count = self.keno_card.get_spot_count()
                if spot_count <= 0:
                    self.alert = NoticeWindow(self.screen_rect.center, "Please pick your spots.")
                    return

                self.play.update()
                hit_count = self.keno_card.get_hit_count()
                self.bet_action.result(spot_count, hit_count)
                self.round_history.update(spot_count, hit_count)
                self.hit_count_label = Label(self.font, 64, 'HIT COUNT: {0}'.format(hit_count), 'gold3', {'center':(640,764)})

            if self.clear_action.rect.collidepoint(event_pos):
                self.clear_action.update()
                self.hit_count_label = Label(self.font, 64, 'HIT COUNT: 0', 'gold3', {'center':(640,764)})

            self.keno_card.update(event_pos)

            spot_count = self.keno_card.get_spot_count()
            bet_amount = self.bet_action.bet
            if spot_count != self.prev_spot_count:
                self.pay_table.update(spot_count, bet_amount)
                self.prev_spot_count = spot_count

            self.spot_count_label = Label(self.font, 64, 'SPOT COUNT: {0}'.format(spot_count), 'gold3', {'center':(640,700)})
        if not self.alert:
            self.buttons.get_event(event)
        self.alert and self.alert.get_event(event)

    def draw(self, surface):
        """This method handles drawing/blitting the state each frame."""
        surface.fill(prepare.FELT_GREEN)

        self.mock_label.draw(surface)

        self.buttons.draw(surface)

        self.keno_card.draw(surface)

        self.quick_pick.draw(surface)
        self.play.draw(surface)

        #TODO: work these back in properly.
        #self.spot_count_label.draw(surface)
        #self.hit_count_label.draw(surface)

        self.pay_table.draw(surface)

        self.round_history.draw(surface)

        self.clear_action.draw(surface)

        self.bet_action.draw(surface)

        self.balance_label.draw(surface)
        self.bet_label.draw(surface)

        if self.alert and not self.alert.done:
            self.alert.draw(surface)

    def update(self, surface, keys, current_time, dt, scale):
        """
        This method will be called once each frame while the state is active.
        Surface is a reference to the rendering surface which will be scaled
        to pygame's display surface, keys is the return value of the last call
        to pygame.key.get_pressed. current_time is the number of milliseconds
        since pygame was initialized. dt is the number of milliseconds since
        the last frame.
        """
        total_text = "Balance:  ${}".format(self.casino_player.stats["cash"])

        self.balance_label = Label(self.font, 48, total_text, "gold3",
                               {"topleft": (1036, 760)})

        bet_text = "Bet: ${}".format(self.bet_action.bet)
        self.bet_label = Label(self.font, 48, bet_text, "gold3",
                               {"topleft": (24, 760)})

        mouse_pos = tools.scaled_mouse_pos(scale)
        self.buttons.update(mouse_pos)
        if self.alert:
            self.alert.update(mouse_pos)
            if self.alert.done:
                self.alert = None

        self.draw(surface)

