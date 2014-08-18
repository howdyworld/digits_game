"""
    Digits game
    based on pys60_gametemplate:
    https://github.com/howdyworld/pys60_gametemplate

    temporary all classes in one file
"""
import e32
import appuifw
import graphics
import random
import key_codes

# http://www.mobilenin.com/pys60/resources/ex_use_of_keys_descr.py
class Keyboard(object):

    def __init__(self, onevent=lambda:None):
        self._keyboard_state = {}
        self._downs = {}
        self._onevent = onevent

    def handle_event(self, event):
        if event['type'] == appuifw.EEventKeyDown:
            code = event['scancode']
            if not self.is_down(code):
                self._downs[code]=self._downs.get(code, 0) + 1
            self._keyboard_state[code] = 1

        elif event['type'] == appuifw.EEventKeyUp:
            self._keyboard_state[event['scancode']] = 0

        self._onevent()

    def is_down(self, scancode):
        return self._keyboard_state.get(scancode, 0)

    def pressed(self, scancode):
        if self._downs.get(scancode, 0):
            self._downs[scancode] -= 1
            return True
        return False


class GraphicBase(object):

    def __init__(self, handle_event, bg_color=(0, 0, 0)):
        """ Constructor
            Args:
                bg_color (tuple): RGB color three byte int
        """

        self.bg_color = bg_color
        #
        self.old_body = appuifw.app.body
        self.canvas = appuifw.Canvas(redraw_callback=self.clear_display,
                                     event_callback=handle_event)
        self.screen_size = self.canvas.size
        self.draw = graphics.Draw(self.canvas)
        appuifw.app.body = self.canvas

    def clear_display(self, rect=()):
        self.draw.clear(self.bg_color)

    def close_canvas(self):
        """ Return old body and destroy drawing objects """

        appuifw.app.body = self.old_body
        self.canvas = None
        self.draw = None


class Graphics(GraphicBase):
    """ All drawing logic here """

    RGB_BLACK = (0,0,0)
    RGB_YELLOW = (255,255,0)
    RGB_RED = (255,0,0)

    def __init__(self, keyboard_handler):
        GraphicBase.__init__(self, keyboard_handler)
        self.init_points()

    def init_points(self):
        x, y = self.screen_size
        
        x1 = 70       # my draw limit at left column
        x2 = x - 70   # my draw limit at right column
        x5 = x/2      # my draw limit at middle column
        y1 = 70       # my draw limit at top row
        y2 = y - 70   # my draw limit at bottom row
        y5 = y/2      # my draw limit at middle row

        self.point_top_left  = (x1, y1)
        self.point_top_right = (x2, y1)

        self.point_mid_left  = (x1, y5)
        self.point_mid_right = (x2, y5)
        
        self.point_btm_left  = (x1, y2)
        self.point_btm_right = (x2, y2)

    def draw_num(self, number, correct=True):
        """ Drawing number on all screen """

        # Draw a number, stop at negative values and numbers greater 9
        if number < 0 or number > 9:
            return

        # Set coordinates for drawing new number
        # elif and points adding needs optimization
        # http://legacy.python.org/dev/peps/pep-0275/
        # https://mail.python.org/pipermail/tutor/2011-September/085542.html
        points = []
        if number == 0:
            points += self.point_top_left + self.point_top_right + self.point_mid_right + self.point_btm_right
            points += self.point_btm_left + self.point_mid_left + self.point_top_left
        elif number == 1:
            points += self.point_top_right + self.point_mid_right + self.point_btm_right
        elif number == 2:
            points += self.point_top_left + self.point_top_right + self.point_mid_right + self.point_mid_left
            points += self.point_btm_left + self.point_btm_right
        elif number == 3:
            points += self.point_top_left + self.point_top_right + self.point_mid_right + self.point_mid_left
            points += self.point_mid_right + self.point_btm_right + self.point_btm_left
        elif number == 4:
            points += self.point_top_left + self.point_mid_left + self.point_mid_right + self.point_top_right
            points += self.point_btm_right
        elif number == 5:
            points += self.point_top_right + self.point_top_left + self.point_mid_left + self.point_mid_right
            points += self.point_btm_right + self.point_btm_left
        elif number == 6:
            points += self.point_top_right + self.point_top_left + self.point_btm_left + self.point_btm_right
            points += self.point_mid_right + self.point_mid_left
        elif number == 7:
            points += self.point_top_left + self.point_top_right + self.point_btm_right
        elif number == 8:
            points += self.point_mid_left + self.point_top_left + self.point_top_right + self.point_btm_right
            points += self.point_btm_left + self.point_mid_left + self.point_mid_right
        elif number == 9:
            points += self.point_mid_right + self.point_mid_left + self.point_top_left + self.point_top_right
            points += self.point_btm_right + self.point_btm_left
        else:
            # Should never get here, but avoid problems anyway
            number = 0
            points = self.point_top_left
        
        if correct:
            color = self.RGB_YELLOW
        else:
            color = self.RGB_RED

        self.draw.line(points, width=30, outline=color)

    def draw_info(self, dig_num, lives):
        self.draw.text((5, 25),
                        u"NUMS: "+unicode(dig_num),
                        self.RGB_YELLOW,
                        font=(u'Nokia Hindi S60', 24))
        self.draw.text((self.screen_size[0]-80, 25),
                        u"LIVES: "+unicode(lives),
                        self.RGB_YELLOW,
                        font=(u'Nokia Hindi S60', 24))

    def draw_gameover(self):
        x, y = self.screen_size
        self.draw.text((x*0.2, y*0.5),
                        u"GAME OVER!",
                        self.RGB_RED,
                        font=(u'Nokia Hindi S60', 32))

    def draw_ready(self):
        x, y = self.screen_size
        self.draw.text((x*0.3, y*0.5),
                        u"READY?",
                        self.RGB_YELLOW,
                        font=(u'Nokia Hindi S60', 32))


class GameCore(object):
    """ All game logic here """

    def __init__(self):
        self.keyboard = Keyboard()
        self.graphics = Graphics(self.keyboard.handle_event)

        self.numbers = []
        self.curr_numindex = 0
        self.digits_num = 3
        self.lives = 3
        self.player_wait = False
        self.show_nums_wait = False

        self.show_interval = 1.0

    def draw_gamefield(self):
        self.graphics.clear_display()
        self.graphics.draw_info(self.digits_num, self.lives)

    def init_new_game(self):
        self.curr_numindex = 0
        self.digits_num = 3
        self.lives = 3

    def player_turn(self):
        self.player_wait = True

        while self.player_wait:
            if self.lives == 0:
                self.draw_gamefield()
                self.graphics.draw_gameover()
                e32.ao_sleep(self.show_interval*1.5)
                self.init_new_game()
                break
            # if-elif statment needs optimization
            if self.keyboard.pressed(key_codes.EScancode0):
                self.check_num(0)
                
            elif self.keyboard.pressed(key_codes.EScancode1):
                self.check_num(1)

            elif self.keyboard.pressed(key_codes.EScancode2):
                self.check_num(2)

            elif self.keyboard.pressed(key_codes.EScancode3):
                self.check_num(3)

            elif self.keyboard.pressed(key_codes.EScancode3):
                self.check_num(3)

            elif self.keyboard.pressed(key_codes.EScancode4):
                self.check_num(4)

            elif self.keyboard.pressed(key_codes.EScancode5):
                self.check_num(5)

            elif self.keyboard.pressed(key_codes.EScancode6):
                self.check_num(6)

            elif self.keyboard.pressed(key_codes.EScancode7):
                self.check_num(7)

            elif self.keyboard.pressed(key_codes.EScancode8):
                self.check_num(8)

            elif self.keyboard.pressed(key_codes.EScancode9):
                self.check_num(9)

            # elif self.keyboard.pressed(key_codes.EScancodeRightSoftkey):
            #     self.player_wait = False

            e32.ao_sleep(0.1)

    def quit(self):
        """ Must be called when game ends """

        self.player_wait = False
        self.graphics.close_canvas()

    #
    def next_level(self):
        """ Re-init variables for next level """

        # wait before breaking current level loop and go to the next
        e32.ao_sleep(self.show_interval)
        # increase num number for next level
        self.curr_numindex = 0
        self.digits_num += 1
        self.player_wait = False

    def check_num(self, user_num):
        self.draw_gamefield()
        e32.ao_sleep(0.15)
        if user_num == self.numbers[self.curr_numindex]:
            self.graphics.draw_num(user_num, correct=True)
            self.curr_numindex += 1

            # if user pass all numbers
            if self.curr_numindex == self.digits_num:
                self.next_level()
        else:
            self.lives -= 1
            self.draw_gamefield()
            self.graphics.draw_num(user_num, correct=False)

    def gen_nums(self):
        """ Generates random numbers between 0 and 9 for self.numbers """

        self.numbers = []
        for i in range(self.digits_num):
            self.numbers.append(int(random.randrange(10)))

    def show_nums(self):
        """ Show numbers to user with specific interval """

        # before showing nums clear display and wait few millisec
        self.draw_gamefield()
        self.graphics.draw_ready()
        e32.ao_sleep(self.show_interval*1.5)

        for num in self.numbers:
            self.draw_gamefield()
            self.graphics.draw_num(num)
            e32.ao_sleep(self.show_interval)
            # show clear screen between numbers
            self.draw_gamefield()
            # wait on clear screen before showing next number
            e32.ao_sleep(self.show_interval * 0.25)


class Game(object):

    INTERVAL = 0.08

    def __init__(self, screen_mode="full"):
        """ Constructor
            Args:
                screen_mode (str): normal, large, full
        """

        appuifw.app.screen = screen_mode
        self.game_core = GameCore()
        appuifw.app.menu = [
            (u"Exit", self.set_exit)
        ]
        self.exit_flag = False

    def set_exit(self):
        """ Breaks game loop in self.run function """

        self.exit_flag = True
        self.game_core.quit()

    def run(self):
        """ Main game loop """

        appuifw.app.exit_key_handler = self.set_exit
        
        while not self.exit_flag:
            self.game_core.gen_nums()
            self.game_core.show_nums()
            self.game_core.player_turn()

            e32.ao_sleep(self.INTERVAL)

        #self.game_core.quit()


if __name__ == "__main__":
    try:
        app = Game()
    except Exception, e:
        appuifw.note(u"Exception: %s" % (e))
    else:
        app.run()
        del app