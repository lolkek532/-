import arcade
from arcade.gui import UIManager, UITextureButton
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SPEED = 2


class Player(arcade.Sprite):
    def __init__(self, n):
        super().__init__()
        self.hero = n

        # Загрузка текстур для разных персонажей
        self.heros = [
            # 0 - Pink Worm
            [
                arcade.load_texture(":resources:images/enemies/wormPink.png"),
                arcade.load_texture(":resources:images/enemies/slimePurple.png")  # можно заменить на анимацию
            ],
            # 1 - Green Worm
            [
                arcade.load_texture(":resources:images/enemies/wormGreen.png"),
                arcade.load_texture(":resources:images/enemies/wormGreen_move.png")
            ],
            # 2 - Frog
            [
                arcade.load_texture(":resources:images/enemies/frog.png"),
                arcade.load_texture(":resources:images/enemies/frog_move.png")
            ]
        ]

        self.animation_timer = 0
        self.current_texture = 0

    def update(self, delta_time):
        # Обновление позиции
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Анимация ходьбы
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_timer = 0
            self.current_texture = 1 - self.current_texture
            self.texture = self.heros[self.hero][self.current_texture]


class MyGUIWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.GRAY)

        # UI Manager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()

        # Layout'ы
        self.anchor_layout = UIAnchorLayout(y=self.height // 3)
        self.box_layout = UIBoxLayout(vertical=False, space_between=10)

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

        # Список всех спрайтов
        self.all_sprites = arcade.SpriteList()

    def setup_widgets(self):
        # Здесь добавим все виджеты — по порядку!
        texture_normal = arcade.load_texture("resources/gui/basic_assets/button/red_normal.png")
        texture_hovered = arcade.load_texture("resources/gui/basic_assets/button/red_hover.png")
        texture_pressed = arcade.load_texture("resources/gui/basic_assets/button/red_press.png")

        # Кнопка Pink Worm
        texture_button = arcade.gui.UITextureButton(text="Pink Worm",
                                                    texture=texture_normal,
                                                    texture_hovered=texture_hovered,
                                                    texture_pressed=texture_pressed,
                                                    scale=1.0)
        texture_button.on_click = self.change_hero
        self.box_layout.add(texture_button)

        # Кнопка Green Worm
        texture_button1 = arcade.gui.UITextureButton(text="Green Worm",
                                                     texture=texture_normal,
                                                     texture_hovered=texture_hovered,
                                                     texture_pressed=texture_pressed,
                                                     scale=1.0)
        texture_button1.on_click = self.change_hero1
        self.box_layout.add(texture_button1)

        # Кнопка Frog
        texture_button2 = arcade.gui.UITextureButton(text="Frog",
                                                     texture=texture_normal,
                                                     texture_hovered=texture_hovered,
                                                     texture_pressed=texture_pressed,
                                                     scale=1.0)
        texture_button2.on_click = self.change_hero2
        self.box_layout.add(texture_button2)

    def setup(self):
        self.player = Player(0)  # по умолчанию Pink Worm
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.all_sprites.append(self.player)

    def change_hero(self, event):
        self.player.hero = 0

    def change_hero1(self, event):
        self.player.hero = 1

    def change_hero2(self, event):
        self.player.hero = 2

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.all_sprites.draw()

    def on_update(self, delta_time: float) -> bool | None:
        self.all_sprites.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.change_y = SPEED
        if key == arcade.key.DOWN:
            self.player.change_y = -SPEED
        if key == arcade.key.RIGHT:
            self.player.change_x = SPEED
        if key == arcade.key.LEFT:
            self.player.change_x = -SPEED

    def on_key_release(self, key, modifiers):

        if key in [arcade.key.UP, arcade.key.DOWN]:
            self.player.change_y = 0
        if key in [arcade.key.RIGHT, arcade.key.LEFT]:
            self.player.change_x = 0

    def setup_game(width=800, height=600, title="Pink Worm And Others"):
        game = MyGUIWindow(width, height, title)
        game.setup()
        return game

    def main():
        setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.run()

    if __name__ == "__main__":
        main()
