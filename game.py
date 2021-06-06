import arcade
import random
import math
import maps
import points


#Global constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = 'PACMAN'
SPRITE_SCALING = 0.5
PLAYER_MOVEMENT_SPEED = 5
ENEMY_MOVEMENT_SPEED = 1
ENEMY_LIST = ["./images/pink.png", "./images/blue.png", "./images/orange.png", "./images/red.png"]


class MenuView(arcade.View):

    def __init__(self):
        super().__init__()
        self.logo = arcade.load_texture("./images/logo.png")

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(300, 530, 200, 50, self.logo)
        arcade.draw_text('Menu', SCREEN_WIDTH/2, SCREEN_HEIGHT/1.3,
                         arcade.color.YELLOW_ORANGE, font_size=30, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)
        self.window.set_mouse_visible(False)


class Player(arcade.Sprite):
    '''
    Class represents player on screen.
    '''
    def update(self):
        '''
        Function sets appropriate ranges.
        '''
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.top > SCREEN_HEIGHT - 30:
            self.top = SCREEN_HEIGHT - 30
        elif self.bottom < 0:
            self.bottom = 0


class Enemy(arcade.Sprite):
    '''
    Class represents enemies on screen.
    '''

    def follow_sprite(self, player_sprite):
        '''
        The function will move the current sprite in the direction of
        another sprite that is given as a parameter.
        '''
        self.center_x += self.change_x
        self.center_y += self.change_y

        if random.randrange(0, 50) == 0:
            start_x = self.center_x
            start_y = self.center_y

            #Get the player location
            player_x = player_sprite.center_x
            player_y = player_sprite.center_y

            #Calculation the angle between the position of the player and the enemy
            x_diff = player_x - start_x
            y_diff = player_y - start_y
            angle = math.atan2(y_diff, x_diff)

            self.change_x = math.cos(angle) * ENEMY_MOVEMENT_SPEED
            self.change_y = math.sin(angle) * ENEMY_MOVEMENT_SPEED


class GameView(arcade.View):

    def __init__(self):
        super().__init__()

        #Variables that will hold sprite lists
        self.player_list = None
        self.enemy_list = None
        self.wall_list = None
        self.point_list = None

        #Motion control keys
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.player_sprite = None
        self.physics_engine = None
        self.score = 0
        self.level = 1

        #Player lives
        self.player_lives = 3
        self.player_live_image = None

        #Load sounds
        self.collect_points_sound = arcade.load_sound("./sounds/mixkit-game-ball-tap-2073.wav")
        self.kill_sound = arcade.load_sound("./sounds/mixkit-player-losing-or-failing-2042.wav")
        self.next_level_sound = arcade.load_sound("./sounds/mixkit-extra-bonus-in-a-video-game-2045.wav")

    def setup(self):
        '''
        Set up the game and initialize the variables.
        '''
        #Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.point_list = arcade.SpriteList(use_spatial_hash=True)

        #Set up walls
        self.wall_list = maps.level_1()

        #Set up the player
        self.player_sprite = Player("./images/pacman.png", SPRITE_SCALING)
        self.player_sprite.position = (50, 290)
        self.player_list.append(self.player_sprite)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        #Set up enemies
        for enemy_im in ENEMY_LIST:
            enemy = Enemy(enemy_im, SPRITE_SCALING)
            enemy.center_x = 720
            enemy.center_y = random.randint(100, SCREEN_HEIGHT - 100)
            self.enemy_list.append(enemy)

        #Set up points
        self.point_list = points.level_1()

        #Load player live
        self.player_live_image = arcade.load_texture("./images/pacman_live.png")

    def on_key_press(self, key, modifiers):
        '''
        Called when a key is pressed.
        '''
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        '''
        Called when the user releases a key.
        '''
        if key == arcade.key.UP:
            self.up_pressed = False
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN:
            self.down_pressed = False
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT:
            self.left_pressed = False
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        #Player movement
        self.physics_engine.update()

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = - PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = - PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        self.player_list.update()

        #Enemies movement
        for enemy in self.enemy_list:
            enemy.follow_sprite(self.player_sprite)

        #Check collision between enemies and the player
        if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list):
            arcade.play_sound(self.kill_sound)
            self.player_sprite.position = (50, 290)
            self.player_lives -= 1

        if self.player_lives == 0:
            arcade.play_sound(self.kill_sound)
            view = GameOverView()
            self.window.show_view(view)
            self.window.set_mouse_visible(True)

        #Enemies collision with walls
        for enemy in self.enemy_list:
            enemy.center_x += enemy.change_x
            walls_hit = arcade.check_for_collision_with_list(enemy, self.wall_list)
            for wall in walls_hit:
                if enemy.change_x > 0:
                    enemy.right = wall.left
                elif enemy.change_x < 0:
                    enemy.left = wall.right
            if len(walls_hit) > 0:
                enemy.change_x *= -1

            enemy.center_y += enemy.change_y
            walls_hit = arcade.check_for_collision_with_list(enemy, self.wall_list)
            for wall in walls_hit:
                if enemy.change_y > 0:
                    enemy.top = wall.bottom
                elif enemy.change_y < 0:
                    enemy.bottom = wall.top
            if len(walls_hit) > 0:
                enemy.change_y *= -1

        #Score update
        self.point_list.update()
        point_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.point_list)
        for point in point_hit_list:
            point.remove_from_sprite_lists()
            arcade.play_sound(self.collect_points_sound)
            self.score += 1

        #Change level
        self.point_list.update()
        if len(self.point_list) == 0:
            self.level += 1
            arcade.play_sound(self.next_level_sound)
            self.setup()

    def on_show(self):
        #Set the background color
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        self.wall_list.draw()
        self.point_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()

        for y in range(self.player_lives):
            arcade.draw_lrwh_rectangle_textured(5, 15 + 30 * y, 30, 30, self.player_live_image)

        arcade.draw_text(f"Wynik: {self.score}", 10, 570, arcade.color.YELLOW_ORANGE, 18)
        arcade.draw_text(f"Poziom {self.level}", 360, 570, arcade.color.YELLOW_ORANGE, 18)


class GameOverView(arcade.View):

    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Gra skończona", SCREEN_WIDTH / 2, SCREEN_HEIGHT/1.3,
                         arcade.color.YELLOW_ORANGE, font_size=40, anchor_x="center")
        arcade.draw_text("Naciśnij, aby zagrać ponownie.", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.5,
                         arcade.color.YELLOW_ORANGE, font_size=15, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        game_view = GameView()
        self.window.show_view(game_view)
        self.window.set_mouse_visible(False)
        game_view.setup()


def main():
    '''
    Main method
    '''
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.set_location(400, 150)
    start_view = MenuView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()