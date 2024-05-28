
import arcade
import pyautogui
import arcade.gui
import time
import math
from text_dia import dialogue

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Симбиоз"

relationship = [1, 1, 1, 1, 1]
level = []
score = []
score_1 = []
score_2 = []
score_3 = []

CHARACTER_SCALING = 0.4
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

SPRITE_SCALING_LASER = 0.8
SHOOT_SPEED = 12
BLADE_SPEED = 12
attack_DAMAGE = 2
BLADE_DAMAGE = 4
ENEMY_DAMAGE = 2

PLAYER_MOVEMENT_SPEED = 8
GRAVITY = 1.005
PLAYER_JUMP_SPEED = 20


LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 120
PLAYER_START_Y = 255

RIGHT_FACING = 0
LEFT_FACING = 1

LAYER_NAME_MOVING_PLATFORMS = "Moving"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Enemies"
LAYER_NAME_BLADE = "Blade"
LAYER_NAME_FRIEND = "Friend"
LAYER_NAME_KEY = "Key"
LAYER_NAME_BAR = "Bar"
LAYER_NAME_ENATTACK = "EnAttack"
LAYER_NAME_HEARTS = "Hearts"
LAYER_NAME_WINDOW = "Window"
LAYER_NAME_POWER = "Power"

def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]

class Enemy(arcade.Sprite):
    def __init__(self, name_folder, name_file):
        super().__init__()

        # Default to facing right
        self.facing_direction = RIGHT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING + 0.05
        self.character_face_direction = RIGHT_FACING

        main_path = f"enemies/{name_folder}/{name_file}"

        self.idle_texture_pair = load_texture_pair(f"{main_path}_base.png")
        self.dead_texture_pair = load_texture_pair(f"{main_path}_dead.png")
        self.walk_texture_pair = load_texture_pair(f"{main_path}_base.png")

        self.texture = self.idle_texture_pair[0]
        self.hit_box = self.texture.hit_box_points

        self.should_update_walk = 0

    def update_animation(self, delta_time: float = 1 / 2):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        if self.should_update_walk == 3:
            self.texture = self.walk_texture_pair[self.facing_direction]
            self.should_update_walk = 0
            return

        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        self.should_update_walk += 1


class MaleEnemy(Enemy):
    def __init__(self):
        self.health = 20
        self.enemy_is_dead = False
        self.dead_spot = 0
        # Set up parent class
        super().__init__("male", "male")


class FemaleEnemy(Enemy):
    def __init__(self):
        self.health = 15
        self.enemy_is_dead = False
        self.dead_spot = 0
        # Set up parent class
        super().__init__("female", "female")




class Friend(Enemy):
    def __init__(self):
        # Set up parent class
        super().__init__("friend", "Yvonn")




class PlayerCharacter(arcade.Sprite):

    def __init__(self):

        super().__init__()

        self.character_face_direction = RIGHT_FACING

        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.can_attack = False
        self.can_blade = False
        self.attack_needs_reset = True
        self.blade_needs_reset = True


        main_path = "Amara"

        self.idle_texture_pair = load_texture_pair(f"{main_path}/база 1 амара.png")
        self.fall_texture_pair = load_texture_pair("Amara/jump a/прыжок 7.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}/jump a/прыжок 4.png")

        self.walk_textures = []
        for i in range(1, 12):
            texture = load_texture_pair(f"{main_path}/steps/шаг {i}.png")
            self.walk_textures.append(texture)

        self.attack_textures = []
        for i in range(1, 16):
            texture = load_texture_pair(f"{main_path}/punch/удар {i}.png")
            self.attack_textures.append(texture)


        self.texture = self.idle_texture_pair[0]

        self.hit_box = self.texture.hit_box_points

    def update_animation(self,  delta_time: float = 1/2):

        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        if self.change_y > 0:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif -1 < self.change_y < 0:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return


        if self.can_attack and not self.attack_needs_reset:
            self.cur_texture += 1
            if self.cur_texture > 14:
                self.cur_texture = 0
                self.attack_needs_reset = True
            self.texture = self.attack_textures[self.cur_texture][
                self.character_face_direction]
            return

        if self.can_blade and not self.blade_needs_reset:
            self.cur_texture += 1
            if self.cur_texture > 14:
                self.cur_texture = 0
                self.blade_needs_reset = True
            self.texture = self.attack_textures[self.cur_texture][
                self.character_face_direction]
            return

        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        if self.change_y == 0:
            self.cur_texture += 1
            if self.cur_texture > 10:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][
                self.character_face_direction]


class MainMenu(arcade.View):

    def __init__(self):
        # Set up parent class
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.player = None

        self.sound = arcade.load_sound("menu.mp3")
        self.player = self.sound.play()

        # Render button
        default_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": (21, 19, 21),

            # used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.WHITE,  # also used when hovered
            "font_color_pressed": arcade.color.BLACK,
        }

        red_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": (21, 19, 21),

            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.BLACK,
        }

        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        button_1 = arcade.gui.UIFlatButton(text="Начать", width=200, style=default_style)
        button_2 = arcade.gui.UIFlatButton(text="Выход", width=200, style=red_style)

        button_1.on_click = self.on_button_click
        button_2.on_click = self.exit

        self.v_box.add(button_1)
        self.v_box.add(button_2)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_show_view(self):
        """Called when switching to this view."""

        arcade.set_background_color(arcade.color.SAPPHIRE)
        self.player.play()

    def on_draw(self):
        self.clear()

        self.manager.draw()

    def on_button_click(self, event):
        self.manager.disable()
        self.player.pause()
        game_view = FirstCut()
        self.window.show_view(game_view)

    def exit(self, event):
        arcade.close_window()


class Dialog(arcade.View):

    def __init__(self):

        super().__init__()
        self.choice = 0
        self.button_1 = None
        self.button_2 = None
        self.button_3 = None
        self.button_4 = None
        self.background = None
        self.dialogue_round = 1
        self.option_round = 0

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.sound = arcade.load_sound("gameplay.mp3")
        self.player = self.sound.play()

        self.narrative_style = {
                    "font_name": ("calibri", "arial"),
                    "font_size": 15,
                    "font_color": arcade.color.WHITE,
                    "border_width": 2,
                    "border_color": None,
                    "bg_color": arcade.color.DESERT,

                    "bg_color_pressed": None,
                    "border_color_pressed": arcade.color.WHITE,
                    "font_color_pressed": arcade.color.BLACK,
            }
        self.dialogue_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.COCOA_BROWN,
            ""

            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.BLACK,
        }
        self.v_box = arcade.gui.UIBoxLayout(space_between=0)




    def on_update_dialog(self, i):

        self.dialogue_round = i
        new_score = score_1 + score_3 + score_3

        if i == 35 and self.choice == 1:
            if len(relationship) < 9:
                self.choice = 0

        if i == 36 and self.choice == 1:
            self.player.pause()
            game_view = EndBad()
            self.window.show_view(game_view)

        if i == 36 and self.choice == 2:
            self.dialogue_round = 37

        if i == 35 and self.choice == 2:
            self.player.pause()
            game_view = EndBad()
            self.window.show_view(game_view)

        if self.option_round == 1035:
            self.player.pause()
            game_view = EndPeaceFriendship()
            self.window.show_view(game_view)

        if self.option_round == 2037:
            self.player.pause()
            game_view = EndPeaceNoYvonn()
            self.window.show_view(game_view)

        if self.choice != 0:
            if self.choice == 1:
                self.option_round = 1000 + self.dialogue_round
                if self.option_round in dialogue:
                    self.button_1 = arcade.gui.UIFlatButton(text=dialogue[self.option_round]["prompt"], width=SCREEN_WIDTH - 100,
                                                            style=self.narrative_style, align="left", height=100)
                    self.button_1.on_click = self.next_option
                    self.v_box.add(self.button_1)

            if self.choice == 2:
                self.option_round = 2000 + self.dialogue_round
                if self.option_round in dialogue:
                    self.button_1 = arcade.gui.UIFlatButton(text=dialogue[self.option_round]["prompt"], width=SCREEN_WIDTH - 100,
                                                            style=self.narrative_style, align="left", height=100)
                    self.button_1.on_click = self.next_option
                    self.v_box.add(self.button_1)

            if self.choice == 3:
                self.option_round = 3000 + self.dialogue_round
                if self.option_round in dialogue:
                    self.button_1 = arcade.gui.UIFlatButton(text=dialogue[self.option_round]["prompt"], width=SCREEN_WIDTH - 100,
                                                            style=self.narrative_style, align="left", height=100)
                    self.button_1.on_click = self.next_option
                    self.v_box.add(self.button_1)

        if (self.option_round not in dialogue and self.choice != 0) or self.choice == 0:
            self.choice = 0
            self.button_1 = arcade.gui.UIFlatButton(text=dialogue[i]["prompt"], width=SCREEN_WIDTH - 100,
                                                        height=100,
                                                        style=self.narrative_style, align="left")
            self.v_box.add(self.button_1)


            if 1 in dialogue[i]["options"]:
                if i == 34:
                    self.button_2 = arcade.gui.UIFlatButton(text=dialogue[i]["options"][1], width=SCREEN_WIDTH - 100,
                                                            style=self.dialogue_style, align="left", height= 100)
                    self.button_2.on_click = self.first_option
                    self.v_box.add(self.button_2)
                elif i != 29:
                    self.button_2 = arcade.gui.UIFlatButton(text=dialogue[i]["options"][1], width=SCREEN_WIDTH-100,
                                                            style=self.dialogue_style, align="left")
                    self.button_2.on_click = self.first_option
                    self.v_box.add(self.button_2)
                elif len(new_score) == 6:
                    self.button_2 = arcade.gui.UIFlatButton(text=dialogue[i]["options"][1],
                                                                width=SCREEN_WIDTH - 100,
                                                                style=self.dialogue_style, align="left")
                    self.button_2.on_click = self.first_option
                    self.v_box.add(self.button_2)

                if 2 in dialogue[i]["options"]:
                    self.button_3 = arcade.gui.UIFlatButton(text=dialogue[i]["options"][2], width=SCREEN_WIDTH-100,
                                                                style=self.dialogue_style, align="left")
                    self.v_box.add(self.button_3)
                    self.button_3.on_click = self.second_option

                    if 3 in dialogue[i]["options"]:
                        if i != 29:
                            self.button_4 = arcade.gui.UIFlatButton(text=dialogue[i]["options"][3], width=SCREEN_WIDTH-100,
                                                                        style=self.dialogue_style, align="left")
                            self.v_box.add(self.button_4)
                            self.button_4.on_click = self.third_option
                        else:
                            if len(new_score) != 6:
                                self.button_4 = arcade.gui.UIFlatButton(text=dialogue[i]["options"][3],
                                                                        width=SCREEN_WIDTH - 100,
                                                                        style=self.dialogue_style, align="left")
                                self.v_box.add(self.button_4)
                                self.button_4.on_click = self.third_option
            else:
                self.button_1.on_click = self.next

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                        child=self.v_box,
                        anchor_x="center",
                        anchor_y="center",
                        align_y= -250
            )

        )


        if i <= 3:
            self.background = arcade.load_texture("cut_1.jpg")
        elif 3 <= i <= 12:
            self.background = arcade.load_texture("cut_2.jpg")
        elif 10 <= i <= 29 or (self.option_round == 3032 or self.option_round == 2032 or self.option_round == 2030 or self.option_round == 2031 or self.option_round == 3030 or self.option_round == 3031):
            self.background = arcade.load_texture("midle_cut.jpg")
        elif 30 <= i <= 34 and (self.option_round != 3032 or self.option_round != 2032 or self.option_round!= 2030 or  self.option_round != 2031 or  self.option_round != 3030 or  self.option_round != 3031):
            self.background = arcade.load_texture("cut_3.jpg")


        if i == 12 or i == 20 or i == 28:
            self.player.pause()
            level.append(1)
            game_view = MyGame()
            self.window.show_view(game_view)

        if self.option_round == 3032 or self.option_round == 2032:
            self.player.pause()
            game_view = EndExit()
            self.window.show_view(game_view)




    def on_draw(self):
        """Draw the menu"""
        self.clear()
        self.player.play()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.manager.draw()

    def first_option(self, event):
        self.choice = 1
        self.dialogue_round += 1
        self.v_box.clear()
        relationship.append(1)
        self.on_update_dialog(i=self.dialogue_round)

    def second_option(self, event):
        self.dialogue_round += 1
        self.choice = 2
        self.v_box.clear()
        del relationship[1]
        self.on_update_dialog(i=self.dialogue_round)

    def third_option(self, event):
        self.dialogue_round += 1
        self.choice = 3
        self.v_box.clear()
        self.on_update_dialog(i=self.dialogue_round)

    def next(self, event):
        self.v_box.clear()
        self.dialogue_round += 1
        self.on_update_dialog(i=self.dialogue_round)

    def next_option(self, event):
        if self.option_round == 1025 or self.option_round == 2025:
            self.dialogue_round = 24
            self.choice = 0
        self.v_box.clear()
        self.dialogue_round += 1
        self.on_update_dialog(i=self.dialogue_round)


class FirstCut(arcade.View):

    def on_show_view(self):
        self.background = arcade.load_texture("cut_1.jpg")

    def on_draw(self):
        self.clear()

        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = Dialog()
        game_view.on_update_dialog(1)
        self.window.show_view(game_view)


class EndExit(arcade.View):
    def __init__(self):
        # Set up parent class
        super().__init__()
        self.choice = 0
        self.button_1 = None
        self.button_2 = None
        self.button_3 = None
        self.button_4 = None
        self.background = None
        self.dialogue_round = 1
        self.option_round = 0

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.background = arcade.load_texture("cut_3.jpg")
        self.sound = arcade.load_sound("bad_end.mp3")
        self.player = self.sound.play()

        self.narrative_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.DESERT,

            # used if button is pressed
            "bg_color_pressed": None,
            "border_color_pressed": arcade.color.WHITE,  # also used when hovered
            "font_color_pressed": arcade.color.BLACK,
        }


    def on_update_dialog(self):

        self.button_1 = arcade.gui.UIFlatButton(text="РАССКАЗЧИК\nАмара ушла и не узнала о тайной лаборатории демидов, где людей превращают в монтров. Два народа остаются объеденены только взаимной ненавистью, которая только растет и готовится вспыхнуть войной в любой момент.", width=SCREEN_WIDTH - 100,
                                                    height=100,
                                                    style=self.narrative_style, align="left")
        self.v_box = arcade.gui.UIBoxLayout(space_between=0)
        self.v_box.add(self.button_1)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                child=self.v_box,
                anchor_x="center",
                anchor_y="center",
                align_y=-250
            )

        )

    def on_show_view(self):
        self.on_update_dialog()
        self.player.play()

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.manager.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        self.player.pause()
        game_view = MainMenu()
        self.window.show_view(game_view)

class EndBad(arcade.View):
    def __init__(self):
        # Set up parent class
        super().__init__()
        self.choice = 0
        self.button_1 = None
        self.button_2 = None
        self.button_3 = None
        self.button_4 = None
        self.background = None
        self.dialogue_round = 1
        self.option_round = 0

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.background = arcade.load_texture("end_2.png")
        self.sound = arcade.load_sound("bad_end.mp3")
        self.player = self.sound.play()

        self.narrative_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.DESERT,

            # used if button is pressed
            "bg_color_pressed": None,
            "border_color_pressed": arcade.color.WHITE,  # also used when hovered
            "font_color_pressed": arcade.color.BLACK,
        }


    def on_update_dialog(self):

        self.button_1 = arcade.gui.UIFlatButton(text="РАССКАЗЧИК\nИвонн воссоединилась с сестрой, но большой ценой. Люди, узнав о нарушении договора, начали войну. Амара стала командовать людьскими полками, Ивонн встала на сторону демидов. В следующий раз герои встретятся на поле боя.", width=SCREEN_WIDTH - 100,
                                                    height=150,
                                                    style=self.narrative_style, align="left")
        self.v_box = arcade.gui.UIBoxLayout(space_between=0)
        self.v_box.add(self.button_1)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                child=self.v_box,
                anchor_x="center",
                anchor_y="center",
                align_y=-250
            )

        )

    def on_show_view(self):
        self.on_update_dialog()
        self.player.play()

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.manager.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        self.player.pause()
        game_view = MainMenu()
        self.window.show_view(game_view)

class EndPeaceFriendship(arcade.View):
    def __init__(self):
        # Set up parent class
        super().__init__()
        self.choice = 0
        self.button_1 = None
        self.button_2 = None
        self.button_3 = None
        self.button_4 = None
        self.background = None
        self.dialogue_round = 1
        self.option_round = 0
        self.player = None

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.background = arcade.load_texture("end_1.jpg")
        self.sound = arcade.load_sound("good_end.mp3")
        self.player = self.sound.play()

        self.narrative_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.DESERT,

            # used if button is pressed
            "bg_color_pressed": None,
            "border_color_pressed": arcade.color.WHITE,  # also used when hovered
            "font_color_pressed": arcade.color.BLACK,
        }


    def on_update_dialog(self):

        self.button_1 = arcade.gui.UIFlatButton(text="РАССКАЗЧИК\nДемиды потеряв большую часть военной мощи испугались возможного нападения людей. Начались переговоры о новом мире, в котором не будет места насилию, где народы будут работать сообща. Амара и Ивоннн вызвались помогать за столом переговоров. Их пример крепкой дружбы мотивировал остальных принять чужой народ. С этого момента жизнь на планете стала лучше, демиды и люди рука об руку стремятся к процветанию.", width=SCREEN_WIDTH - 100,
                                                    height=150,
                                                    style=self.narrative_style, align="left")
        self.v_box = arcade.gui.UIBoxLayout(space_between=0)
        self.v_box.add(self.button_1)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                child=self.v_box,
                anchor_x="center",
                anchor_y="center",
                align_y=-250
            )

        )

    def on_show_view(self):
        self.on_update_dialog()
        self.player.play()

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.manager.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        self.player.pause()
        game_view = MainMenu()
        self.window.show_view(game_view)

class EndPeaceNoYvonn(arcade.View):
    def __init__(self):

        super().__init__()
        self.choice = 0
        self.button_1 = None
        self.button_2 = None
        self.button_3 = None
        self.button_4 = None
        self.background = None
        self.dialogue_round = 1
        self.option_round = 0

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.background = arcade.load_texture("end_1.jpg")
        self.sound = arcade.load_sound("good_end.mp3")
        self.player = self.sound.play()

        self.narrative_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.DESERT,

            "bg_color_pressed": None,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.BLACK,
        }


    def on_update_dialog(self):

        self.button_1 = arcade.gui.UIFlatButton(text="РАССКАЗЧИК\nДемиды потеряв большую часть военной мощи испугались возможного нападения людей. Начались переговоры о новом мире, в котором не будет места насилию, где народы будут работать сообща. Амара вызвалась помогать за столом переговоров. Процесс шел медленно и тяжело, некоторые так и не смогут принять чужой народ, но и такие изменения поменяют жизнь на этой планете.", width=SCREEN_WIDTH - 100,
                                                    height=150,
                                                    style=self.narrative_style, align="left")
        self.v_box = arcade.gui.UIBoxLayout(space_between=0)
        self.v_box.add(self.button_1)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                child=self.v_box,
                anchor_x="center",
                anchor_y="center",
                align_y=-250
            )

        )

    def on_show_view(self):
        self.on_update_dialog()
        arcade.play_sound(self.sound)


    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.manager.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        self.player.pause()
        game_view = MainMenu()
        self.window.show_view(game_view)

class MyGame(arcade.View):

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__()

        # Level
        self.level = int(len(level))

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.attack_pressed = False
        self.power_pressed = False
        self.shift_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.attack_needs_reset = True
        self.blade_needs_reset = True
        self.shoot_timer = 0
        self.pause_on = False
        self.power_time = 0
        self.bar_grow = False
        self.reset_started = 0
        self.cd_enattack = 0
        self.keys_pressed = set()
        self.player_health = 3
        self.hits = 0

        self.max_health = 10
        self.current_health = 10
        self.widthb = 200
        self.heightb = 20
        self.red_bar = arcade.SpriteSolidColor(self.widthb, self.heightb, arcade.color.COCOA_BROWN)
        self.green_bar = arcade.SpriteSolidColor(self.widthb, self.heightb, arcade.color.COBALT)
        self.red_bar.position = (400, 50)
        self.green_bar.position = (400, 50)

        self.enemy_m = None
        self.enemy_f = None

        self.tile_map = None

        self.scene = None
        self.screen_center_x = 0
        self.spot = 0
        self.state = None

        self.player_sprite = None
        self.friend_sprite = None
        self.heart_sprite = None

        self.physics_engine = None

        self.camera = None

        self.gui_camera = None
        self.end_of_map = 2610

        self.can_blade = False
        self.shoot_timer = 0

        self.collect_coin_sound = arcade.load_sound("coins.mp3")
        self.jump_sound = arcade.load_sound("jump.mp3")

        self.sword = arcade.load_sound("sword.mp3")
        self.power_gone = arcade.load_sound("power gone.mp3")
        self.power_give = arcade.load_sound("power give.mp3")
        self.shoot_sound = arcade.load_sound("waves.mp3")
        self.sound = arcade.load_sound("gameplay.mp3")
        self.player = self.sound.play()

    def setup(self):

        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)

        self.player.play()

        map_name = f"map_{self.level}.tmj"

        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_PLATFORMS: {
                "use_spatial_hash": False,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        self.scene = arcade.Scene.from_tilemap(self.tile_map)


        self.can_blade = True
        self.shoot_timer = 0

        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        self.friend_sprite = Friend()
        self.friend_sprite.center_x = PLAYER_START_X - 140
        self.friend_sprite.center_y = PLAYER_START_Y + 20
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.friend_sprite)

        image_source = "ключ.png"
        self.key_sprite_1 = arcade.Sprite(image_source, 0.1)
        self.key_sprite_1.center_x = -20
        self.key_sprite_1.center_y = -20
        self.scene.add_sprite(LAYER_NAME_KEY, self.key_sprite_1)

        self.key_sprite_2 = arcade.Sprite(image_source, 0.1)
        self.key_sprite_2.center_x = -20
        self.key_sprite_2.center_y = -20
        self.scene.add_sprite(LAYER_NAME_KEY, self.key_sprite_2)

        self.key_sprite_3 = arcade.Sprite("ключ.png", 0.15)
        self.key_sprite_3.center_x = 1200
        self.key_sprite_3.center_y = 50

        self.scene.add_sprite_list_before("Power", LAYER_NAME_PLAYER)
        self.state = arcade.Sprite("в силе.png", CHARACTER_SCALING)
        self.state.center_x = -200
        self.state.center_y = -200
        self.scene.add_sprite(LAYER_NAME_POWER, self.state)

        self.scene.add_sprite_list_before("Window", LAYER_NAME_BACKGROUND)
        self.on_window = arcade.Sprite("за окном.jpg", TILE_SCALING)
        self.on_window.center_x = 5970/4
        self.on_window.center_y = 2128/4
        self.scene.add_sprite(LAYER_NAME_WINDOW, self.on_window)

        self.scene.add_sprite_list_before("Background", LAYER_NAME_PLATFORMS)
        self.walls = arcade.Sprite("стены.png", TILE_SCALING)
        self.walls.center_x = 5970/4
        self.walls.center_y = 2128/4
        self.scene.add_sprite(LAYER_NAME_BACKGROUND, self.walls)

        image_source = "инструкция.png"
        self.rules = arcade.Sprite(image_source, 0.25)
        self.rules.center_x = SCREEN_WIDTH/2 - 230
        self.rules.center_y = SCREEN_HEIGHT/2 + 230



        enemies_layer = self.tile_map.object_lists[LAYER_NAME_ENEMIES]
        for my_object in enemies_layer:
            cartesian = self.tile_map.get_cartesian(
                my_object.shape[0], my_object.shape[1]
            )
            enemy_type = my_object.properties["type"]
            if enemy_type == "male":
                self.enemy_m = MaleEnemy()
                self.enemy_m.center_x = math.floor(
                    cartesian[0] * TILE_SCALING * self.tile_map.tile_width
                )
                self.enemy_m.center_y = math.floor(
                    (cartesian[1] + 1) * (self.tile_map.tile_height * TILE_SCALING)
                )

                if "change_x" in my_object.properties:
                    self.enemy_m.change_x = my_object.properties["change_x"]
                self.scene.add_sprite(LAYER_NAME_ENEMIES, self.enemy_m)

            if enemy_type == "female":
                self.enemy_f = FemaleEnemy()
                self.enemy_f.center_x = math.floor(
                    cartesian[0] * TILE_SCALING * self.tile_map.tile_width
                )
                self.enemy_f.center_y = math.floor(
                    (cartesian[1] + 1) * (self.tile_map.tile_height * TILE_SCALING)
                )

                if "change_x" in my_object.properties:
                    self.enemy_f.change_x = my_object.properties["change_x"]
                self.scene.add_sprite(LAYER_NAME_ENEMIES, self.enemy_f)

        self.scene.add_sprite_list(LAYER_NAME_ENATTACK)
        self.scene.add_sprite_list(LAYER_NAME_BLADE)

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        self.physics_engine = arcade.PhysicsEnginePlatformer(

            self.player_sprite, gravity_constant=GRAVITY, platforms=self.scene["Moving"], walls=self.scene["Platforms"]
        )

    def on_show_view(self):
        self.setup()

    def on_draw(self):

        self.clear()

        self.camera.use()

        self.scene.draw()

        self.gui_camera.use()

        self.key_sprite_3.draw()
        if self.player_sprite.center_x < 460 and len(level) == 1:
            self.rules.draw()

        self.red_bar.draw()
        self.green_bar.draw()

        score_text = f"Х {len(score_1 + score_2 + score_3)}"
        arcade.draw_text(
            score_text,
            1230,
            42,
            arcade.csscolor.WHITE,
            18,
        )

        for i in range(self.player_health):
            self.heart_sprite = arcade.Sprite("heart.png", 0.05)
            self.heart_sprite.center_x = 50 + i * 50
            self.heart_sprite.center_y = 50
            i += 1
            self.heart_sprite.draw()



    def process_keychange(self):

        self.spot = self.player_sprite.center_x
        if self.up_pressed and not self.down_pressed:
            if (
                self.physics_engine.can_jump(y_distance=10)
                and not self.jump_needs_reset
            ):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.friend_sprite.center_y = self.player_sprite.center_y + 50
                arcade.play_sound(self.jump_sound)

        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.friend_sprite.center_x = self.player_sprite.center_x - 170
            self.friend_sprite.center_y = self.player_sprite.center_y + 50
            self.friend_sprite.facing_direction = RIGHT_FACING

        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.friend_sprite.center_x = self.player_sprite.center_x - 170
            self.friend_sprite.center_y = self.player_sprite.center_y + 50
            self.friend_sprite.facing_direction = LEFT_FACING
        else:
            self.player_sprite.change_x = 0
            self.friend_sprite.center_x = self.player_sprite.center_x - 170
            self.friend_sprite.center_y = self.player_sprite.center_y + 50

        if not self.player_sprite.attack_needs_reset and not self.right_pressed and not self.left_pressed and not self.up_pressed:
            self.player_sprite.can_attack = True
        else:
            self.player_sprite.can_attack = False

        if not self.player_sprite.blade_needs_reset and not self.right_pressed and not self.left_pressed and not self.up_pressed:
            self.player_sprite.can_blade = True
        else:
            self.player_sprite.can_blade = False


    def on_key_press(self, key, modifiers):

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        if key == arcade.key.LSHIFT:
            if self.reset_started == 0:
                arcade.play_sound(self.power_give)
                self.reset_started = time.time()
                self.shift_pressed = True
                if self.power_time == 0:
                    self.power_time = time.time()

        if key == arcade.key.R:
            self.attack_pressed = True
            self.player_sprite.attack_needs_reset = False

    def on_key_release(self, key, modifiers):

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        if key == arcade.key.R:
            self.hits = 0
            self.power_pressed = False
            self.attack_pressed = False

        if key == arcade.key.LSHIFT:
            self.shift_pressed = False
            self.player_sprite.blade_needs_reset = True
        self.process_keychange()

    def center_camera_to_player(self, speed=0.2):
        self.screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if self.screen_center_x < 0:
            self.screen_center_x = 0
        if self.screen_center_x > 1600:
            self.screen_center_x = 1600
        if screen_center_y < 0:
            screen_center_y = 0
        if screen_center_y > 262:
            screen_center_y = 262
        player_centered = self.screen_center_x, screen_center_y

        self.camera.move_to(player_centered, speed)

    def on_update(self, delta_time: float = 1/2):

        if self.power_time != 0:
            self.state.center_x = self.player_sprite.center_x+10
            self.state.center_y = self.player_sprite.center_y+30
        else:
            self.state.center_x = -100
            self.state.center_y = -100



        if self.pause_on == False:

            self.physics_engine.update()

            if time.time() - self.power_time < 10:
                if self.attack_pressed:
                    self.power_pressed = True
                    self.player_sprite.blade_needs_reset = False

            if self.power_time != 0:
                if time.time() - self.power_time >= 10:
                    arcade.play_sound(self.power_gone)
                    self.player_sprite.blade_needs_reset = True
                    self.can_blade = False
                    self.bar_grow = True
                    self.power_time = 0
                    self.power_pressed = False

            if (time.time() - self.reset_started) >= 19:
                self.reset_started = 0

            if self.power_time != 0:
                if self.current_health > 0.1:
                    self.current_health -= (time.time() - self.power_time)/150
                    health_ratio = (self.current_health / self.max_health)
                    green_bar_widthb = self.widthb * health_ratio
                    self.green_bar.width = green_bar_widthb
                    self.green_bar.left = 300
                else:
                    self.current_health = 0.01

            if self.bar_grow:
                if self.current_health < 10:
                    self.current_health += (time.time() - self.reset_started)/600
                    health_ratio = (self.current_health / self.max_health)
                    green_bar_widthb = (self.widthb * health_ratio)
                    self.green_bar.width = green_bar_widthb
                    self.green_bar.left = 300
                    if self.green_bar.width >= 200:
                        self.bar_grow = False
                else:
                    self.current_health = 10

            if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
                self.player_sprite.is_on_ladder = True
                self.friend_sprite.is_on_ladder = True
                self.process_keychange()
            else:
                self.player_sprite.is_on_ladder = False
                self.friend_sprite.is_on_ladder = False
                self.process_keychange()

            if self.can_blade and self.blade_needs_reset:
                if self.power_pressed:
                    arcade.play_sound(self.shoot_sound)
                    blade = arcade.Sprite(
                        "blade.png", 0.5
                    )
                    self.can_blade = False
                    self.blade_needs_reset = True
                    self.player_sprite.can_attack = False
                    self.player_sprite.attack_needs_reset = True

                    if self.player_sprite.character_face_direction == RIGHT_FACING:
                        blade.change_x = BLADE_SPEED
                    else:
                        blade.change_x = -BLADE_SPEED

                    blade.center_x = self.player_sprite.center_x
                    blade.center_y = self.player_sprite.center_y+40

                    self.scene.add_sprite(LAYER_NAME_BLADE, blade)

            elif(not self.power_pressed):
                self.shoot_timer += 1
                if self.shoot_timer == SHOOT_SPEED:
                    self.can_blade = True
                    self.shoot_timer = 0


            self.scene.update_animation(
                 [LAYER_NAME_PLAYER, LAYER_NAME_ENEMIES, LAYER_NAME_KEY]
            )

            self.scene.update([LAYER_NAME_KEY, LAYER_NAME_BLADE, LAYER_NAME_ENATTACK, LAYER_NAME_MOVING_PLATFORMS,
                               LAYER_NAME_WINDOW, LAYER_NAME_BACKGROUND, LAYER_NAME_POWER])

            if self.player_sprite.change_x == 0:
                self.on_window.change_x = 0
            elif self.player_sprite.change_x > 0 and self.screen_center_x != 0 and self.screen_center_x != 1600:
                self.on_window.change_x = 1
            elif self.player_sprite.change_x < 0 and self.screen_center_x != 0 and self.screen_center_x != 1600:
                self.on_window.change_x = -1

            if self.enemy_f.enemy_is_dead:
                self.enemy_f.texture = self.enemy_f.dead_texture_pair[0]
                self.key_sprite_1.center_x = self.enemy_f.center_x
                self.key_sprite_1.center_y = self.enemy_f.center_y
                self.enemy_f.center_y = self.enemy_f.dead_spot
            elif self.player_sprite.center_x - self.enemy_f.center_x > -500:
                self.enemy_f.change_x = 0
                if self.player_sprite.center_x < self.enemy_f.center_x:
                    self.enemy_f.facing_direction = LEFT_FACING
                else:
                    self.enemy_f.facing_direction = RIGHT_FACING

            if (self.player_sprite.center_x - self.enemy_f.center_x > -500) and self.enemy_f.enemy_is_dead is False:
                if self.cd_enattack == 0:
                    arcade.play_sound(self.shoot_sound)
                    enattack = arcade.Sprite(
                        "blade.png", 0.5
                    )
                    if self.player_sprite.center_x < self.enemy_f.center_x:
                        enattack.change_x = -BLADE_SPEED
                    else:
                        enattack.change_x = BLADE_SPEED

                    self.scene.add_sprite(LAYER_NAME_ENATTACK, enattack)
                    enattack.center_x = self.enemy_f.center_x
                    enattack.center_y = self.enemy_f.center_y
                    self.cd_enattack = 200
                else:
                    self.cd_enattack -= 1

            if self.enemy_m.enemy_is_dead:
                self.enemy_m.texture = self.enemy_m.dead_texture_pair[0]
                self.key_sprite_2.center_x = self.enemy_m.center_x
                self.key_sprite_2.center_y = self.enemy_m.center_y
                self.enemy_m.center_y = self.enemy_m.dead_spot
            elif self.player_sprite.center_x - self.enemy_m.center_x > -500:
                self.enemy_m.change_x = 0
                if self.player_sprite.center_x < self.enemy_m.center_x:
                    self.enemy_m.facing_direction = LEFT_FACING
                else:
                    self.enemy_m.facing_direction = RIGHT_FACING

            if (self.player_sprite.center_x - self.enemy_m.center_x > -500) and self.enemy_m.enemy_is_dead is False:
                if self.cd_enattack == 0:
                    arcade.play_sound(self.shoot_sound)
                    enattack = arcade.Sprite(
                        "blade.png", 0.5
                    )
                    if self.player_sprite.center_x < self.enemy_m.center_x:
                        enattack.change_x = -BLADE_SPEED
                    else:
                        enattack.change_x = BLADE_SPEED

                    self.scene.add_sprite(LAYER_NAME_ENATTACK, enattack)
                    enattack.center_x = self.enemy_m.center_x
                    enattack.center_y = self.enemy_m.center_y
                    self.cd_enattack = 200
                else:
                    self.cd_enattack -= 1

            for damage in self.scene[LAYER_NAME_ENATTACK]:
                hit_list_en = arcade.check_for_collision_with_lists(
                    damage,
                    [
                        self.scene[LAYER_NAME_PLATFORMS],
                        self.scene[LAYER_NAME_MOVING_PLATFORMS]
                    ],
                )

                if hit_list_en:
                    damage.remove_from_sprite_lists()

            for bullet in self.scene[LAYER_NAME_BLADE]:
                hit_list = arcade.check_for_collision_with_lists(
                    bullet,
                    [
                        self.scene[LAYER_NAME_ENEMIES],
                        self.scene[LAYER_NAME_PLATFORMS],
                    ],
                )

                if hit_list:
                    bullet.remove_from_sprite_lists()

                for collision2 in hit_list:
                    if (
                            collision2 == self.scene[LAYER_NAME_ENEMIES][0]
                            and not self.enemy_f.enemy_is_dead
                    ):
                        self.enemy_f.health -= BLADE_DAMAGE
                        if self.enemy_f.health <= 0:
                            self.enemy_f.enemy_is_dead = True
                            self.enemy_f.dead_spot = self.enemy_f.center_y - 80

                for collision3 in hit_list:
                    if (collision3 == self.scene[LAYER_NAME_ENEMIES][1]
                            and not self.enemy_m.enemy_is_dead
                    ):
                        self.enemy_m.health -= BLADE_DAMAGE
                        if self.enemy_m.health <= 0:
                            self.enemy_m.enemy_is_dead = True
                            self.enemy_m.dead_spot = self.enemy_m.center_y - 80

            player_collision_list = arcade.check_for_collision_with_lists(
                self.player_sprite,
                [
                    self.scene[LAYER_NAME_ENEMIES],
                    self.scene[LAYER_NAME_ENATTACK],
                ],
            )

            for collision in player_collision_list:
                if self.scene[LAYER_NAME_ENEMIES] in collision.sprite_lists and self.player_sprite.can_attack  and  self.player_sprite.attack_needs_reset\
                        and not self.enemy_f.enemy_is_dead and self.hits < 1\
                        and collision == self.scene[LAYER_NAME_ENEMIES][0]:
                    self.enemy_f.health -= attack_DAMAGE
                    self.hits += 1
                    if self.enemy_f.health <= 0:
                        self.enemy_f.enemy_is_dead = True
                        self.enemy_f.dead_spot = self.enemy_f.center_y - 80
                    arcade.play_sound(self.sword)
                    self.player_sprite.can_attack = False

                if self.scene[LAYER_NAME_ENEMIES] in collision.sprite_lists and self.player_sprite.can_attack \
                        and not self.enemy_m.enemy_is_dead and self.hits < 1\
                        and collision == self.scene[LAYER_NAME_ENEMIES][1]:
                    self.enemy_m.health -= 2
                    self.hits += 1
                    if self.enemy_m.health <= 0:
                        self.enemy_m.enemy_is_dead = True
                        self.enemy_m.dead_spot = self.enemy_m.center_y - 80
                    arcade.play_sound(self.sword)
                    self.player_sprite.can_attack = False


                if self.scene[LAYER_NAME_ENATTACK] in collision.sprite_lists:
                    self.player_health -= 1
                    collision.remove_from_sprite_lists()
                    if self.player_health == 0:
                        self.player.pause()
                        game_view = GameOverView()
                        self.window.show_view(game_view)
                        return

            if self.player_sprite.center_x >= self.end_of_map:
                if self.level == 1:
                    self.player.pause()
                    game_view = Dialog()
                    game_view.on_update_dialog(14)
                if self.level == 2:
                    self.player.pause()
                    game_view = Dialog()
                    game_view.on_update_dialog(21)
                if self.level == 3:
                    self.player.pause()
                    game_view = Dialog()
                    game_view.on_update_dialog(29)

                self.window.show_view(game_view)
                return


            key_hit_list = arcade.check_for_collision_with_list(
                self.player_sprite, self.scene["Key"]
            )

            for key in key_hit_list:
                key.remove_from_sprite_lists()
                arcade.play_sound(self.collect_coin_sound)

                if len(level) == 1:
                    score_1.append(1)
                if len(level) == 2:
                    score_2.append(1)
                if len(level) == 3:
                    score_3.append(1)


            self.center_camera_to_player()

class GameOverView(arcade.View):

    def __init__(self):
        # Set up parent class
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.sound = arcade.load_sound("bad_end.mp3")
        self.player = self.sound.play()

        # Render button
        default_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": (21, 19, 21),

            # used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.WHITE,  # also used when hovered
            "font_color_pressed": arcade.color.BLACK,
        }

        red_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": (21, 19, 21),

            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.BLACK,
        }

        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        button_1 = arcade.gui.UIFlatButton(text="Заново", width=200, style=default_style)
        button_2 = arcade.gui.UIFlatButton(text="Выход", width=200, style=red_style)

        button_1.on_click = self.on_button_click
        button_2.on_click = self.exit

        self.v_box.add(button_1)
        self.v_box.add(button_2)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_show_view(self):
        self.player.play()
        arcade.set_background_color(arcade.color.SAPPHIRE)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        arcade.draw_text(
            "Вы проиграли",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 1.40,
            arcade.color.WHITE,
            30,
            anchor_x="center")


    def on_button_click(self, event):
        self.manager.disable()
        if len(level) == 1:
            score_1.clear()
        if len(level) == 2:
            score_2.clear()
        if len(level) == 3:
            score_3.clear()

        self.player.pause()
        game_view = MyGame()
        self.window.show_view(game_view)

    def exit(self, event):
        arcade.close_window()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MainMenu()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()
