import arcade
import random
import math
import time

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Космическая Аркада - Яндекс Лицей"

PLAYER_SPEED = 7
BULLET_SPEED = 12
ENEMY_SPEED_MIN = 2
ENEMY_SPEED_MAX = 4
ASTEROID_SPEED_MIN = 1
ASTEROID_SPEED_MAX = 3
PLANET_SPEED_MIN = 0.5
PLANET_SPEED_MAX = 1.5

PLAYER_START_HEALTH = 150
ENEMY_HEALTH = 40
ASTEROID_HEALTH = 30
PLANET_HEALTH = 100

UPGRADE_COST_SHIELD = 150
UPGRADE_COST_SPEED = 200
UPGRADE_COST_DAMAGE = 250
UPGRADE_COST_EXPLOSIVE = 300
UPGRADE_COST_TELEPORT = 400
UPGRADE_COST_MAGNET = 350
UPGRADE_COST_SHIELD_BASH = 250
UPGRADE_COST_TIME_WARP = 500


class Explosion:
    def __init__(self, x, y, radius=50):
        self.center_x = x
        self.center_y = y
        self.radius = radius
        self.max_radius = radius
        self.current_radius = 5
        self.growth_speed = 15
        self.active = True
        self.damage = 30

    def update(self, delta_time):
        self.current_radius += self.growth_speed
        if self.current_radius >= self.max_radius:
            self.active = False

    def draw(self):
        if self.active:
            alpha = 200 - (self.current_radius / self.max_radius * 150)
            color = (255, 100, 0, int(alpha))
            arcade.draw_circle_filled(
                self.center_x, self.center_y,
                self.current_radius, color
            )
            arcade.draw_circle_outline(
                self.center_x, self.center_y,
                self.current_radius, (255, 200, 0, int(alpha / 2)), 3
            )


class PowerUp:
    def __init__(self, x, y, power_type):
        self.center_x = x
        self.center_y = y
        self.power_type = power_type
        self.radius = 15
        self.speed = 2
        self.active = True
        self.float_timer = 0

        if power_type == "health":
            self.color = arcade.color.GREEN
        elif power_type == "shield":
            self.color = arcade.color.BLUE
        elif power_type == "damage":
            self.color = arcade.color.RED
        elif power_type == "speed":
            self.color = arcade.color.YELLOW
        else:
            self.color = arcade.color.PURPLE

    def update(self, delta_time):
        self.center_y -= self.speed
        self.float_timer += delta_time * 5
        self.center_x += math.sin(self.float_timer) * 0.5

        if self.center_y < -50:
            self.active = False

    def draw(self):
        if self.active:
            arcade.draw_circle_filled(
                self.center_x, self.center_y,
                self.radius, self.color
            )
            if self.power_type == "health":
                arcade.draw_text("+", self.center_x, self.center_y - 4,
                                 arcade.color.WHITE, 12, anchor_x="center")
            elif self.power_type == "shield":
                arcade.draw_text("S", self.center_x, self.center_y - 4,
                                 arcade.color.WHITE, 12, anchor_x="center")
            elif self.power_type == "damage":
                arcade.draw_text("D", self.center_x, self.center_y - 4,
                                 arcade.color.WHITE, 12, anchor_x="center")
            elif self.power_type == "speed":
                arcade.draw_text("V", self.center_x, self.center_y - 4,
                                 arcade.color.WHITE, 12, anchor_x="center")


class Player:
    def __init__(self, is_3d=False):
        self.is_3d = is_3d
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 4
        self.width = 50 if not is_3d else 60
        self.height = 50 if not is_3d else 60
        self.health = PLAYER_START_HEALTH
        self.max_health = PLAYER_START_HEALTH
        self.speed = PLAYER_SPEED
        self.damage = 15
        self.shield = 0
        self.max_shield = 0
        self.score = 0
        self.bullet_cooldown = 0
        self.bullet_cooldown_max = 8
        self.bullet_type = "normal"

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False
        self.shooting = False

        self.engine_particles = []
        self.last_particle_time = time.time()

        self.explosive_bullets = False
        self.teleport_cooldown = 0
        self.teleport_max_cooldown = 180
        self.teleport_distance = 200

        self.magnet_active = False
        self.magnet_radius = 150
        self.magnet_duration = 0
        self.magnet_max_duration = 600

        self.shield_bash = False
        self.shield_bash_cooldown = 0
        self.shield_bash_max_cooldown = 300

        self.time_warp_active = False
        self.time_warp_duration = 0
        self.time_warp_max_duration = 300
        self.time_slow_factor = 0.5

        self.double_shot = False
        self.triple_shot = False

    @property
    def left(self):
        return self.center_x - self.width / 2

    @property
    def right(self):
        return self.center_x + self.width / 2

    @property
    def bottom(self):
        return self.center_y - self.height / 2

    @property
    def top(self):
        return self.center_y + self.height / 2

    def update(self, delta_time=1 / 60):
        if self.move_up:
            self.center_y += self.speed
        if self.move_down:
            self.center_y -= self.speed
        if self.move_left:
            self.center_x -= self.speed
        if self.move_right:
            self.center_x += self.speed

        if self.left < 20:
            self.center_x = 20 + self.width / 2
        if self.right > SCREEN_WIDTH - 20:
            self.center_x = SCREEN_WIDTH - 20 - self.width / 2
        if self.bottom < 20:
            self.center_y = 20 + self.height / 2
        if self.top > SCREEN_HEIGHT - 20:
            self.center_y = SCREEN_HEIGHT - 20 - self.height / 2

        if self.shield < self.max_shield:
            self.shield += 0.1

        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1

        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1

        if self.shield_bash_cooldown > 0:
            self.shield_bash_cooldown -= 1

        if self.magnet_active and self.magnet_duration > 0:
            self.magnet_duration -= 1
            if self.magnet_duration <= 0:
                self.magnet_active = False

        if self.time_warp_active and self.time_warp_duration > 0:
            self.time_warp_duration -= 1
            if self.time_warp_duration <= 0:
                self.time_warp_active = False

        if self.is_3d:
            current_time = time.time()
            if current_time - self.last_particle_time > 0.05:
                colors = [arcade.color.RED, arcade.color.GREEN, arcade.color.BLUE,
                          arcade.color.YELLOW, arcade.color.PURPLE, arcade.color.CYAN]
                self.engine_particles.append({
                    'x': self.center_x - 25,
                    'y': self.center_y - 40,
                    'size': random.randint(5, 15),
                    'color': random.choice(colors),
                    'life': 1.0
                })
                self.last_particle_time = current_time

            for particle in self.engine_particles[:]:
                particle['life'] -= 0.05
                particle['y'] -= 5
                if particle['life'] <= 0:
                    self.engine_particles.remove(particle)

    def teleport(self, direction):
        if self.teleport_cooldown <= 0:
            if direction == "up":
                self.center_y += self.teleport_distance
            elif direction == "down":
                self.center_y -= self.teleport_distance
            elif direction == "left":
                self.center_x -= self.teleport_distance
            elif direction == "right":
                self.center_x += self.teleport_distance

            if self.left < 20:
                self.center_x = 20 + self.width / 2
            if self.right > SCREEN_WIDTH - 20:
                self.center_x = SCREEN_WIDTH - 20 - self.width / 2
            if self.bottom < 20:
                self.center_y = 20 + self.height / 2
            if self.top > SCREEN_HEIGHT - 20:
                self.center_y = SCREEN_HEIGHT - 20 - self.height / 2

            self.teleport_cooldown = self.teleport_max_cooldown
            return True
        return False

    def activate_shield_bash(self):
        if self.shield > 50 and self.shield_bash_cooldown <= 0:
            self.shield -= 50
            self.shield_bash_cooldown = self.shield_bash_max_cooldown
            return True
        return False

    def activate_time_warp(self):
        if not self.time_warp_active:
            self.time_warp_active = True
            self.time_warp_duration = self.time_warp_max_duration
            return True
        return False

    def draw(self):
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2

        arcade.draw_lrbt_rectangle_filled(
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            color=arcade.color.GREEN
        )

        if self.is_3d:
            arcade.draw_circle_filled(
                center_x=self.center_x,
                center_y=self.center_y + 10,
                radius=self.width // 4,
                color=arcade.color.CYAN
            )

            wing_width = 20
            wing_height = 10
            wing_left = self.center_x - 35 - wing_width / 2
            wing_right = self.center_x - 35 + wing_width / 2
            wing_bottom = self.center_y - 10 - wing_height / 2
            wing_top = self.center_y - 10 + wing_height / 2

            arcade.draw_lrbt_rectangle_filled(
                left=wing_left,
                right=wing_right,
                bottom=wing_bottom,
                top=wing_top,
                color=arcade.color.DARK_GREEN
            )

            wing_left = self.center_x + 35 - wing_width / 2
            wing_right = self.center_x + 35 + wing_width / 2

            arcade.draw_lrbt_rectangle_filled(
                left=wing_left,
                right=wing_right,
                bottom=wing_bottom,
                top=wing_top,
                color=arcade.color.DARK_GREEN
            )
        else:
            detail_width = self.width // 2
            detail_height = 10
            detail_left = self.center_x - detail_width / 2
            detail_right = self.center_x + detail_width / 2
            detail_bottom = self.center_y + 15 - detail_height / 2
            detail_top = self.center_y + 15 + detail_height / 2

            arcade.draw_lrbt_rectangle_filled(
                left=detail_left,
                right=detail_right,
                bottom=detail_bottom,
                top=detail_top,
                color=arcade.color.LIGHT_GREEN
            )

        if self.magnet_active:
            arcade.draw_circle_outline(
                self.center_x, self.center_y,
                self.magnet_radius, (0, 255, 255, 100), 2
            )

        if self.time_warp_active:
            arcade.draw_circle_outline(
                self.center_x, self.center_y,
                self.width, (255, 255, 0, 150), 3
            )

    def draw_effects(self):
        if self.is_3d:
            for particle in self.engine_particles:
                alpha = int(particle['life'] * 255)
                color_with_alpha = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)
                arcade.draw_circle_filled(
                    center_x=particle['x'],
                    center_y=particle['y'],
                    radius=particle['size'],
                    color=color_with_alpha
                )


class Enemy:
    def __init__(self, is_3d=False):
        self.is_3d = is_3d
        self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = SCREEN_HEIGHT + 100
        self.width = 40 if not is_3d else 50
        self.height = 40 if not is_3d else 50
        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.original_speed = self.speed
        self.health = ENEMY_HEALTH
        self.bullet_cooldown = random.randint(30, 90)
        self.slowed = False
        self.slow_timer = 0

        if is_3d:
            self.colors = [arcade.color.RED, arcade.color.GREEN, arcade.color.BLUE]
            self.color = random.choice(self.colors)
        else:
            self.color = arcade.color.RED

    def update(self, delta_time=1 / 60):
        if self.slowed:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.slowed = False
                self.speed = self.original_speed

        self.center_y -= self.speed

    def draw(self):
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2

        arcade.draw_lrbt_rectangle_filled(
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            color=self.color
        )

        if self.is_3d:
            arcade.draw_circle_filled(
                center_x=self.center_x,
                center_y=self.center_y,
                radius=self.width // 4,
                color=arcade.color.BLACK
            )

        if self.slowed:
            arcade.draw_circle_outline(
                self.center_x, self.center_y,
                self.width // 2, (0, 150, 255, 150), 2
            )

    def slow_down(self, duration=180, factor=0.5):
        if not self.slowed:
            self.original_speed = self.speed
            self.speed *= factor
            self.slowed = True
            self.slow_timer = duration


class Planet:
    def __init__(self, is_3d=False):
        self.is_3d = is_3d
        self.colors = [arcade.color.BLUE, arcade.color.RED, arcade.color.GREEN,
                       arcade.color.PURPLE, arcade.color.ORANGE, arcade.color.YELLOW]
        self.color = random.choice(self.colors)
        self.radius = random.randint(30, 60)
        self.has_aliens = random.choice([True, True, False])
        self.center_x = random.randint(100, SCREEN_WIDTH - 100)
        self.center_y = SCREEN_HEIGHT + 150
        self.speed = random.uniform(PLANET_SPEED_MIN, PLANET_SPEED_MAX)
        self.health = PLANET_HEALTH
        self.rotation_speed = random.uniform(-1, 1)
        self.points = 150 if self.has_aliens else 75
        self.angle = 0

    def update(self, delta_time=1 / 60):
        self.center_y -= self.speed
        self.angle += self.rotation_speed

    def draw(self):
        arcade.draw_circle_filled(
            center_x=self.center_x,
            center_y=self.center_y,
            radius=self.radius,
            color=self.color
        )

        if self.is_3d:
            if self.color in [arcade.color.BLUE, arcade.color.PURPLE]:
                arcade.draw_ellipse_outline(
                    center_x=self.center_x,
                    center_y=self.center_y,
                    width=self.radius * 2.5,
                    height=self.radius * 0.5,
                    color=arcade.color.LIGHT_GRAY,
                    tilt_angle=self.angle
                )

            arcade.draw_circle_filled(
                center_x=self.center_x - self.radius // 3,
                center_y=self.center_y + self.radius // 4,
                radius=self.radius // 4,
                color=(self.color[0] // 2, self.color[1] // 2, self.color[2] // 2)
            )
            arcade.draw_circle_filled(
                center_x=self.center_x + self.radius // 3,
                center_y=self.center_y - self.radius // 4,
                radius=self.radius // 4,
                color=(self.color[0] // 3, self.color[1] // 3, self.color[2] // 3)
            )

        if self.has_aliens:
            for i in range(3):
                offset = i * 20 - 20
                arcade.draw_ellipse_filled(
                    center_x=self.center_x + offset,
                    center_y=self.center_y + self.radius + 15,
                    width=15,
                    height=8,
                    color=arcade.color.SILVER,
                    tilt_angle=self.angle * 2
                )
                arcade.draw_circle_filled(
                    center_x=self.center_x + offset,
                    center_y=self.center_y + self.radius + 20,
                    radius=5,
                    color=arcade.color.RED
                )

        arcade.draw_circle_outline(
            center_x=self.center_x,
            center_y=self.center_y,
            radius=self.radius,
            color=(255, 255, 255, 100),
            border_width=2
        )


class Asteroid:
    def __init__(self, is_3d=False):
        self.is_3d = is_3d
        self.radius = random.randint(15, 30)
        self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = SCREEN_HEIGHT + 100
        self.speed = random.uniform(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)
        self.health = ASTEROID_HEALTH
        self.rotation_speed = random.uniform(-2, 2)
        self.points = int(self.radius)
        self.angle = 0

        if is_3d:
            self.colors = [arcade.color.GRAY, arcade.color.DARK_GRAY, arcade.color.LIGHT_GRAY]
            self.color = random.choice(self.colors)
        else:
            self.colors = [arcade.color.GRAY, arcade.color.DARK_GRAY]
            self.color = random.choice(self.colors)

    def update(self, delta_time=1 / 60):
        self.center_y -= self.speed
        self.angle += self.rotation_speed

    def draw(self):
        arcade.draw_circle_filled(
            center_x=self.center_x,
            center_y=self.center_y,
            radius=self.radius,
            color=self.color
        )

        for i in range(3):
            angle = i * 120 + self.angle
            crater_x = self.center_x + math.cos(math.radians(angle)) * (self.radius * 0.6)
            crater_y = self.center_y + math.sin(math.radians(angle)) * (self.radius * 0.6)
            arcade.draw_circle_filled(
                center_x=crater_x,
                center_y=crater_y,
                radius=self.radius // 4,
                color=(self.color[0] // 2, self.color[1] // 2, self.color[2] // 2)
            )

        if self.is_3d:
            arcade.draw_circle_outline(
                center_x=self.center_x,
                center_y=self.center_y,
                radius=self.radius,
                color=arcade.color.BLACK,
                border_width=2
            )


class EnhancedBullet:
    def __init__(self, x, y, angle, damage, is_player=True, is_3d=False, bullet_type="normal", explosive=False):
        self.is_3d = is_3d
        self.is_player = is_player
        self.bullet_type = bullet_type
        self.center_x = x
        self.center_y = y
        self.angle = angle
        self.damage = damage
        self.radius = 5
        self.explosive = explosive
        self.explosion_radius = 60 if explosive else 0
        self.homing = False
        self.homing_target = None
        self.homing_strength = 0.1
        self.piercing = False
        self.pierced_targets = []
        self.lifetime = 180
        self.age = 0

        if bullet_type == "laser":
            self.color = arcade.color.CYAN if is_player else arcade.color.PINK
            self.speed = BULLET_SPEED * 1.5
            self.damage *= 1.5
            self.radius = 7
        elif bullet_type == "rocket":
            self.color = arcade.color.ORANGE if is_player else arcade.color.PURPLE
            self.speed = BULLET_SPEED * 0.8
            self.damage *= 2.0
            self.radius = 8
        elif bullet_type == "lightsaber":
            self.color = arcade.color.RED
            self.speed = BULLET_SPEED * 1.2
            self.damage *= 1.5
            self.radius = 8
        elif bullet_type == "beam":
            self.color = (255, 0, 0)
            self.speed = BULLET_SPEED * 0.5
            self.damage *= 3.0
            self.radius = 15
            self.piercing = True
        else:
            self.color = arcade.color.YELLOW if is_player else arcade.color.RED
            self.speed = BULLET_SPEED
            if is_3d:
                self.radius = 6

        if explosive:
            self.color = (255, 165, 0)

        angle_rad = math.radians(angle)
        self.change_x = math.cos(angle_rad) * self.speed
        self.change_y = math.sin(angle_rad) * self.speed

    def update(self, delta_time=1 / 60):
        if self.homing and self.homing_target:
            dx = self.homing_target.center_x - self.center_x
            dy = self.homing_target.center_y - self.center_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                target_angle = math.degrees(math.atan2(dy, dx))
                angle_diff = (target_angle - self.angle + 180) % 360 - 180
                self.angle += angle_diff * self.homing_strength

                angle_rad = math.radians(self.angle)
                self.change_x = math.cos(angle_rad) * self.speed
                self.change_y = math.sin(angle_rad) * self.speed

        self.center_x += self.change_x
        self.center_y += self.change_y
        self.age += 1

        return self.age < self.lifetime

    def draw(self):
        arcade.draw_circle_filled(
            center_x=self.center_x,
            center_y=self.center_y,
            radius=self.radius,
            color=self.color
        )

        if self.explosive:
            arcade.draw_circle_outline(
                self.center_x, self.center_y,
                self.radius + 2, (255, 100, 0), 1
            )

        if self.is_3d and self.bullet_type != "normal":
            glow_color = (self.color[0], self.color[1], self.color[2], 100)
            arcade.draw_circle_filled(
                center_x=self.center_x,
                center_y=self.center_y,
                radius=self.radius + 2,
                color=glow_color
            )


class DarthVader:
    def __init__(self, is_3d=False):
        self.is_3d = is_3d
        self.max_health = 1000
        self.health = self.max_health
        self.speed = 2
        self.direction = 1
        self.attack_cooldown = 40
        self.attack_timer = 0
        self.move_timer = 0
        self.move_duration = 120
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT - 100
        self.width = 100
        self.height = 100
        self.phase = 1
        self.force_power = 100
        self.max_force_power = 100
        self.lightsaber_active = False
        self.lightsaber_length = 80
        self.lightsaber_angle = 0
        self.lightsaber_speed = 5
        self.force_lightning_active = False
        self.force_lightning_target = None
        self.force_lightning_particles = []
        self.target_x = SCREEN_WIDTH // 2
        self.target_y = SCREEN_HEIGHT // 2
        self.rage_mode = False
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.attack_patterns = [
            self.basic_shot_attack,
            self.triple_shot_attack,
            self.spread_shot_attack,
            self.lightsaber_throw_attack,
            self.force_lightning_attack,
            self.cross_shot_attack,
            self.spiral_shot_attack,
            self.homing_shot_attack,
            self.rage_shot_attack,
            self.death_star_beam_attack
        ]
        self.current_attack = 0
        self.special_attack_cooldown = 0

    def update(self, delta_time=1 / 60, player=None):
        self.move_timer += 1
        if self.move_timer > self.move_duration:
            self.direction *= -1
            self.move_timer = 0

        self.center_x += self.speed * self.direction * (1.5 if self.rage_mode else 1)

        if self.center_x < 150:
            self.center_x = 150
            self.direction = 1
        if self.center_x > SCREEN_WIDTH - 150:
            self.center_x = SCREEN_WIDTH - 150
            self.direction = -1

        self.attack_timer += 1
        if self.attack_timer >= self.attack_cooldown:
            if player:
                self.execute_attack(player)
            self.attack_timer = 0

        if self.lightsaber_active:
            self.lightsaber_angle += self.lightsaber_speed
            if self.lightsaber_angle >= 360:
                self.lightsaber_angle = 0

        if self.force_power < self.max_force_power:
            self.force_power += 0.4
            if self.rage_mode:
                self.force_power += 0.4

        if self.force_lightning_active and self.force_lightning_target and player:
            self.update_force_lightning(player)

        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown -= 1

        health_percent = self.health / self.max_health
        if health_percent <= 0.7 and self.phase == 1:
            self.phase = 2
            self.invulnerable = True
            self.invulnerable_timer = 120
            self.attack_cooldown = 30
        elif health_percent <= 0.4 and self.phase == 2:
            self.phase = 3
            self.invulnerable = True
            self.invulnerable_timer = 120
            self.attack_cooldown = 25
        elif health_percent <= 0.2 and not self.rage_mode:
            self.rage_mode = True
            self.speed *= 1.8
            self.attack_cooldown = 20

    def execute_attack(self, player):
        if not player:
            return []

        available_attacks = []
        if self.phase == 1:
            available_attacks = self.attack_patterns[:3]
        elif self.phase == 2:
            available_attacks = self.attack_patterns[:7]
        else:
            available_attacks = self.attack_patterns

        if self.rage_mode:
            available_attacks = self.attack_patterns[-2:] + available_attacks

        attack = random.choice(available_attacks)
        bullets = attack(player)
        return bullets

    def basic_shot_attack(self, player):
        bullets = []
        dx = player.center_x - self.center_x
        dy = player.center_y - (self.center_y - 40)
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            angle = math.degrees(math.atan2(dy, dx))
            bullet = EnhancedBullet(
                self.center_x,
                self.center_y - 40,
                angle, 25, False, self.is_3d, "normal"
            )
            bullet.speed = BULLET_SPEED * 1.2
            bullets.append(bullet)
        return bullets

    def triple_shot_attack(self, player):
        bullets = []
        dx = player.center_x - self.center_x
        dy = player.center_y - (self.center_y - 40)
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            base_angle = math.degrees(math.atan2(dy, dx))
            for offset in [-20, 0, 20]:
                bullet = EnhancedBullet(
                    self.center_x,
                    self.center_y - 40,
                    base_angle + offset, 20, False, self.is_3d, "normal"
                )
                bullets.append(bullet)
        return bullets

    def spread_shot_attack(self, player):
        bullets = []
        dx = player.center_x - self.center_x
        dy = player.center_y - (self.center_y - 40)
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            base_angle = math.degrees(math.atan2(dy, dx))
            for i in range(7):
                angle = base_angle + (i - 3) * 12
                bullet = EnhancedBullet(
                    self.center_x,
                    self.center_y - 40,
                    angle, 15, False, self.is_3d, "normal"
                )
                bullets.append(bullet)
        return bullets

    def lightsaber_throw_attack(self, player):
        if self.force_power >= 25 and self.special_attack_cooldown <= 0:
            self.force_power -= 25
            self.lightsaber_active = True
            self.special_attack_cooldown = 90
            bullets = []
            dx = player.center_x - self.center_x
            dy = player.center_y - (self.center_y - 40)
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                base_angle = math.degrees(math.atan2(dy, dx))
                for i in range(3):
                    bullet = EnhancedBullet(
                        self.center_x,
                        self.center_y - 40,
                        base_angle + i * 15 - 15, 35, False, self.is_3d, "lightsaber"
                    )
                    bullets.append(bullet)
            return bullets
        return self.basic_shot_attack(player)

    def force_lightning_attack(self, player):
        if self.force_power >= 35 and self.special_attack_cooldown <= 0:
            self.force_power -= 35
            self.force_lightning_active = True
            self.force_lightning_target = (player.center_x, player.center_y)
            self.special_attack_cooldown = 120

            self.force_lightning_particles = []
            for _ in range(20):
                self.force_lightning_particles.append({
                    'x': self.center_x,
                    'y': self.center_y - 40,
                    'vx': random.uniform(-8, 8),
                    'vy': random.uniform(-8, 8),
                    'life': 50
                })
        return []

    def update_force_lightning(self, player):
        for particle in self.force_lightning_particles[:]:
            dx = self.force_lightning_target[0] - particle['x']
            dy = self.force_lightning_target[1] - particle['y']
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0:
                particle['x'] += dx / distance * 15
                particle['y'] += dy / distance * 15

            particle['life'] -= 1

            if particle['life'] <= 0:
                self.force_lightning_particles.remove(particle)

        if len(self.force_lightning_particles) == 0:
            self.force_lightning_active = False

    def cross_shot_attack(self, player):
        bullets = []
        for angle in [0, 90, 180, 270]:
            bullet = EnhancedBullet(
                self.center_x,
                self.center_y - 40,
                angle, 22, False, self.is_3d, "normal"
            )
            bullets.append(bullet)
        return bullets

    def spiral_shot_attack(self, player):
        bullets = []
        self.lightsaber_angle += 15
        for i in range(8):
            angle = self.lightsaber_angle + i * 45
            bullet = EnhancedBullet(
                self.center_x,
                self.center_y - 40,
                angle, 18, False, self.is_3d, "normal"
            )
            bullets.append(bullet)
        return bullets

    def homing_shot_attack(self, player):
        bullets = []
        for i in range(4):
            angle = random.uniform(0, 360)
            bullet = EnhancedBullet(
                self.center_x,
                self.center_y - 40,
                angle, 20, False, self.is_3d, "normal"
            )
            bullet.homing = True
            bullet.homing_target = player
            bullet.homing_strength = 0.08
            bullet.color = arcade.color.ORANGE
            bullets.append(bullet)
        return bullets

    def rage_shot_attack(self, player):
        bullets = []
        dx = player.center_x - self.center_x
        dy = player.center_y - (self.center_y - 40)
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            base_angle = math.degrees(math.atan2(dy, dx))
            for i in range(11):
                angle = base_angle + (i - 5) * 6
                bullet = EnhancedBullet(
                    self.center_x,
                    self.center_y - 40,
                    angle, 30, False, self.is_3d, "normal"
                )
                bullet.speed = BULLET_SPEED * 1.6
                bullet.color = (200, 0, 0)
                bullets.append(bullet)
        return bullets

    def death_star_beam_attack(self, player):
        if self.force_power >= 60 and self.special_attack_cooldown <= 0:
            self.force_power -= 60
            self.special_attack_cooldown = 180
            bullets = []
            dx = player.center_x - self.center_x
            dy = player.center_y - (self.center_y - 40)
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                angle = math.degrees(math.atan2(dy, dx))
                bullet = EnhancedBullet(
                    self.center_x,
                    self.center_y - 40,
                    angle, 80, False, self.is_3d, "beam"
                )
                bullet.color = (255, 50, 50)
                bullets.append(bullet)
            return bullets
        return self.rage_shot_attack(player)

    def draw(self):
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2

        body_color = arcade.color.BLACK if not self.rage_mode else (50, 0, 0)
        arcade.draw_lrbt_rectangle_filled(
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            color=body_color
        )

        mask_color = arcade.color.DARK_GRAY if not self.rage_mode else (80, 80, 80)
        mask_width = self.width - 20
        mask_height = self.height - 60
        mask_left = self.center_x - mask_width / 2
        mask_right = self.center_x + mask_width / 2
        mask_bottom = self.center_y + 20 - mask_height / 2
        mask_top = self.center_y + 20 + mask_height / 2

        arcade.draw_lrbt_rectangle_filled(
            left=mask_left,
            right=mask_right,
            bottom=mask_bottom,
            top=mask_top,
            color=mask_color
        )

        eye_color = arcade.color.RED if not self.rage_mode else (255, 100, 100)
        arcade.draw_circle_filled(
            center_x=self.center_x - 20,
            center_y=self.center_y + 25,
            radius=10,
            color=eye_color
        )
        arcade.draw_circle_filled(
            center_x=self.center_x + 20,
            center_y=self.center_y + 25,
            radius=10,
            color=eye_color
        )

        if self.lightsaber_active:
            saber_x = self.center_x + math.cos(math.radians(self.lightsaber_angle)) * 60
            saber_y = self.center_y - 40 + math.sin(math.radians(self.lightsaber_angle)) * 60
            arcade.draw_line(
                self.center_x, self.center_y - 40,
                saber_x, saber_y,
                arcade.color.RED, 6
            )

        if self.force_lightning_active:
            for particle in self.force_lightning_particles:
                alpha = int(255 * (particle['life'] / 50))
                arcade.draw_circle_filled(
                    particle['x'], particle['y'],
                    4, (255, 255, 200, alpha)
                )

        if self.is_3d:
            border_color = arcade.color.WHITE if not self.rage_mode else (255, 100, 100)
            arcade.draw_lrbt_rectangle_outline(
                left=left,
                right=right,
                bottom=bottom,
                top=top,
                color=border_color,
                border_width=3
            )

        if self.rage_mode:
            arcade.draw_circle_outline(
                self.center_x, self.center_y,
                self.width * 1.3, (255, 50, 50, 200), 6
            )

        if self.invulnerable:
            alpha = int(128 + 127 * math.sin(self.invulnerable_timer * 0.1))
            arcade.draw_circle_outline(
                self.center_x, self.center_y,
                self.width * 1.5, (255, 255, 255, alpha), 4
            )

        phase_color = arcade.color.RED if self.phase == 1 else arcade.color.ORANGE if self.phase == 2 else arcade.color.PURPLE
        arcade.draw_text(
            f"ФАЗА {self.phase}",
            self.center_x, self.center_y - 80,
            phase_color, 16,
            anchor_x="center", bold=True
        )


class SpaceGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.is_3d = False
        self.current_screen = "menu"
        self.player = None
        self.enemies = []
        self.asteroids = []
        self.planets = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.darth_vader = None
        self.game_over = False
        self.wave = 1
        self.enemies_killed = 0
        self.spawn_timer = 0
        self.boss_active = False
        self.show_credits = False
        self.credits_timer = 0
        self.credits_y = SCREEN_HEIGHT + 50

        self.explosions = []
        self.power_ups = []

        self.stars = []
        for _ in range(100):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(1, 3)
            })

        self.update_rate = 1 / 60

    def setup_game(self):
        self.player = Player(self.is_3d)
        self.enemies = []
        self.asteroids = []
        self.planets = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.darth_vader = None
        self.game_over = False
        self.wave = 1
        self.enemies_killed = 0
        self.spawn_timer = 0
        self.boss_active = False
        self.show_credits = False
        self.credits_timer = 0
        self.credits_y = SCREEN_HEIGHT + 50
        self.explosions = []
        self.power_ups = []
        self.current_screen = "game"

    def on_draw(self):
        self.clear()

        if self.current_screen == "menu":
            self.draw_menu()
        elif self.current_screen == "game":
            self.draw_game()
        elif self.current_screen == "game_over":
            self.draw_game_over()
        elif self.current_screen == "credits":
            self.draw_credits()

    def draw_menu(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)

        for star in self.stars:
            arcade.draw_circle_filled(
                center_x=star['x'],
                center_y=star['y'],
                radius=star['size'],
                color=arcade.color.WHITE
            )

        arcade.draw_text(
            "КОСМИЧЕСКАЯ АРКАДА",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
            arcade.color.YELLOW, 48,
            anchor_x="center", bold=True
        )

        arcade.draw_text(
            "Яндекс Лицей Проект",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 220,
            arcade.color.CYAN, 28,
            anchor_x="center"
        )

        arcade.draw_text(
            "ВЫБЕРИТЕ РЕЖИМ ИГРЫ:",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 300,
            arcade.color.WHITE, 32,
            anchor_x="center"
        )

        button_left = SCREEN_WIDTH // 2 - 200
        button_right = SCREEN_WIDTH // 2 + 200
        button_3d_top = SCREEN_HEIGHT - 360
        button_3d_bottom = SCREEN_HEIGHT - 440
        button_2d_top = SCREEN_HEIGHT - 480
        button_2d_bottom = SCREEN_HEIGHT - 560

        button_3d_color = (50, 150, 255) if self.is_3d else (100, 200, 255)
        arcade.draw_lrbt_rectangle_filled(
            left=button_left,
            right=button_right,
            bottom=button_3d_bottom,
            top=button_3d_top,
            color=button_3d_color
        )
        arcade.draw_text(
            "3D РЕЖИМ (для мощных ПК)",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 400,
            arcade.color.WHITE, 24,
            anchor_x="center"
        )

        button_2d_color = (150, 50, 255) if not self.is_3d else (200, 100, 255)
        arcade.draw_lrbt_rectangle_filled(
            left=button_left,
            right=button_right,
            bottom=button_2d_bottom,
            top=button_2d_top,
            color=button_2d_color
        )
        arcade.draw_text(
            "2D РЕЖИМ (для слабых ПК)",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 520,
            arcade.color.WHITE, 24,
            anchor_x="center"
        )

        arcade.draw_text(
            "Используйте мышь для выбора режима",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 620,
            arcade.color.LIGHT_GRAY, 18,
            anchor_x="center"
        )

        arcade.draw_text(
            "Нажмите ПРОБЕЛ для старта",
            SCREEN_WIDTH // 2, 100,
            arcade.color.YELLOW, 22,
            anchor_x="center"
        )

    def draw_game(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)

        for star in self.stars:
            arcade.draw_circle_filled(
                center_x=star['x'],
                center_y=star['y'],
                radius=star['size'],
                color=arcade.color.WHITE
            )

        for planet in self.planets:
            planet.draw()

        for asteroid in self.asteroids:
            asteroid.draw()

        for enemy in self.enemies:
            enemy.draw()

        if self.boss_active and self.darth_vader:
            self.darth_vader.draw()

        for bullet in self.enemy_bullets:
            bullet.draw()

        for bullet in self.player_bullets:
            bullet.draw()

        for explosion in self.explosions:
            explosion.draw()

        for power_up in self.power_ups:
            power_up.draw()

        if self.player:
            self.player.draw()

            if self.is_3d:
                self.player.draw_effects()

        self.draw_ui()

    def draw_game_over(self):
        arcade.draw_lrbt_rectangle_filled(
            left=0,
            right=SCREEN_WIDTH,
            bottom=0,
            top=SCREEN_HEIGHT,
            color=(0, 0, 0, 200)
        )

        player_score = self.player.score if self.player else 0
        enemies_killed = self.enemies_killed if self.player else 0
        wave = self.wave if self.player else 1

        arcade.draw_text(
            "ИГРА ОКОНЧЕНА",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
            arcade.color.RED, 60,
            anchor_x="center", bold=True
        )

        arcade.draw_text(
            f"Ваш счет: {player_score}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            arcade.color.YELLOW, 40,
            anchor_x="center"
        )

        arcade.draw_text(
            f"Уничтожено врагов: {enemies_killed}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60,
            arcade.color.WHITE, 28,
            anchor_x="center"
        )

        arcade.draw_text(
            f"Волна: {wave}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
            arcade.color.WHITE, 28,
            anchor_x="center"
        )

        if self.boss_active and self.darth_vader and self.darth_vader.health <= 0:
            arcade.draw_text(
                "ВЫ ПОБЕДИЛИ ДАРТ ВЕЙДЕРА!",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200,
                arcade.color.GOLD, 36,
                anchor_x="center"
            )

            arcade.draw_text(
                "Нажмите ПРОБЕЛ для просмотра титров",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 280,
                arcade.color.CYAN, 24,
                anchor_x="center"
            )
        else:
            arcade.draw_text(
                "Нажмите ПРОБЕЛ для возврата в меню",
                SCREEN_WIDTH // 2, 150,
                arcade.color.CYAN, 24,
                anchor_x="center"
            )

    def draw_credits(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)

        for star in self.stars:
            arcade.draw_circle_filled(
                center_x=star['x'],
                center_y=star['y'],
                radius=star['size'],
                color=arcade.color.WHITE
            )

        current_y = self.credits_y

        arcade.draw_text(
            "ТИТРЫ",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.GOLD, 60,
            anchor_x="center", anchor_y="center", bold=True
        )
        current_y -= 100

        arcade.draw_text(
            "СОЗДАТЕЛИ:",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.YELLOW, 40,
            anchor_x="center", anchor_y="center", bold=True
        )
        current_y -= 80

        arcade.draw_text(
            "ВЛАДИСЛАВ",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.WHITE, 32,
            anchor_x="center", anchor_y="center"
        )
        current_y -= 60

        arcade.draw_text(
            "ФЁДОР",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.WHITE, 32,
            anchor_x="center", anchor_y="center"
        )
        current_y -= 60

        arcade.draw_text(
            "АННА",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.WHITE, 32,
            anchor_x="center", anchor_y="center"
        )
        current_y -= 100

        current_y -= 50

        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH // 2 - 50,
            right=SCREEN_WIDTH // 2 + 50,
            bottom=current_y - 150,
            top=current_y,
            color=(255, 192, 203)
        )

        arcade.draw_circle_filled(
            center_x=SCREEN_WIDTH // 2 - 25,
            center_y=current_y - 40,
            radius=25,
            color=(255, 182, 193)
        )
        arcade.draw_circle_filled(
            center_x=SCREEN_WIDTH // 2 + 25,
            center_y=current_y - 40,
            radius=25,
            color=(255, 182, 193)
        )

        arcade.draw_circle_filled(
            center_x=SCREEN_WIDTH // 2,
            center_y=current_y + 40,
            radius=40,
            color=(255, 218, 185)
        )

        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH // 2 - 50,
            right=SCREEN_WIDTH // 2 + 50,
            bottom=current_y + 40,
            top=current_y + 120,
            color=(139, 69, 19)
        )

        arcade.draw_circle_filled(
            center_x=SCREEN_WIDTH // 2 - 15,
            center_y=current_y + 50,
            radius=8,
            color=arcade.color.BLACK
        )
        arcade.draw_circle_filled(
            center_x=SCREEN_WIDTH // 2 + 15,
            center_y=current_y + 50,
            radius=8,
            color=arcade.color.BLACK
        )

        arcade.draw_arc_outline(
            center_x=SCREEN_WIDTH // 2,
            center_y=current_y + 20,
            width=30,
            height=20,
            color=arcade.color.RED,
            start_angle=190,
            end_angle=350,
            border_width=3
        )

        leg_width = 30
        leg_height = 120
        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH // 2 - 40 - leg_width / 2,
            right=SCREEN_WIDTH // 2 - 40 + leg_width / 2,
            bottom=current_y - 150 - leg_height,
            top=current_y - 150,
            color=(255, 192, 203)
        )
        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH // 2 + 40 - leg_width / 2,
            right=SCREEN_WIDTH // 2 + 40 + leg_width / 2,
            bottom=current_y - 150 - leg_height,
            top=current_y - 150,
            color=(255, 192, 203)
        )

        underwear_color = (255, 105, 180)
        underwear_width = 100
        underwear_height = 40
        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH // 2 - underwear_width / 2,
            right=SCREEN_WIDTH // 2 + underwear_width / 2,
            bottom=current_y - 150,
            top=current_y - 150 + underwear_height,
            color=underwear_color
        )

        arcade.draw_circle_filled(
            center_x=SCREEN_WIDTH // 2 - 30,
            center_y=current_y - 130,
            radius=10,
            color=arcade.color.WHITE
        )
        arcade.draw_circle_filled(
            center_x=SCREEN_WIDTH // 2,
            center_y=current_y - 130,
            radius=10,
            color=arcade.color.WHITE
        )
        arcade.draw_circle_filled(
            center_x=SCREEN_WIDTH // 2 + 30,
            center_y=current_y - 130,
            radius=10,
            color=arcade.color.WHITE
        )

        current_y -= 300

        arcade.draw_text(
            "ИДЕЯ ОДНОГО ИЗ СОЗДАТЕЛЕЙ",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.YELLOW, 28,
            anchor_x="center", anchor_y="center", bold=True
        )
        current_y -= 50
        arcade.draw_text(
            "FEODAL",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.CYAN, 36,
            anchor_x="center", anchor_y="center", bold=True
        )
        current_y -= 100

        arcade.draw_text(
            "СПАСИБО ЗА ИГРУ!",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.GOLD, 40,
            anchor_x="center", anchor_y="center", bold=True
        )
        current_y -= 80

        arcade.draw_text(
            "ЯНДЕКС ЛИЦЕЙ",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.RED, 32,
            anchor_x="center", anchor_y="center"
        )
        current_y -= 60

        arcade.draw_text(
            "2024",
            SCREEN_WIDTH // 2, current_y,
            arcade.color.WHITE, 28,
            anchor_x="center", anchor_y="center"
        )
        current_y -= 100

        current_y -= 400

        arcade.draw_text(
            "Нажмите ПРОБЕЛ для возврата в меню",
            SCREEN_WIDTH // 2, 100,
            arcade.color.CYAN, 24,
            anchor_x="center"
        )

    def draw_ui(self):
        if not self.player:
            return

        health_width = 300
        health_fill = 300 * (self.player.health / self.player.max_health)
        arcade.draw_lrbt_rectangle_filled(
            left=20,
            right=20 + health_width,
            bottom=SCREEN_HEIGHT - 70,
            top=SCREEN_HEIGHT - 30,
            color=(100, 0, 0)
        )
        arcade.draw_lrbt_rectangle_filled(
            left=20,
            right=20 + health_fill,
            bottom=SCREEN_HEIGHT - 70,
            top=SCREEN_HEIGHT - 30,
            color=arcade.color.GREEN
        )
        arcade.draw_text(f"ЗДОРОВЬЕ: {int(self.player.health)}/{self.player.max_health}",
                         30, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16, bold=True)

        if self.player.max_shield > 0:
            shield_width = 300
            shield_fill = 300 * (self.player.shield / self.player.max_shield)
            arcade.draw_lrbt_rectangle_filled(
                left=20,
                right=20 + shield_width,
                bottom=SCREEN_HEIGHT - 120,
                top=SCREEN_HEIGHT - 80,
                color=(0, 0, 100)
            )
            arcade.draw_lrbt_rectangle_filled(
                left=20,
                right=20 + shield_fill,
                bottom=SCREEN_HEIGHT - 120,
                top=SCREEN_HEIGHT - 80,
                color=arcade.color.BLUE
            )
            arcade.draw_text(f"ЩИТ: {int(self.player.shield)}/{self.player.max_shield}",
                             30, SCREEN_HEIGHT - 110, arcade.color.WHITE, 16, bold=True)

        arcade.draw_text(f"ОЧКИ: {self.player.score}", 20, SCREEN_HEIGHT - 150, arcade.color.YELLOW, 20, bold=True)
        arcade.draw_text(f"ВОЛНА: {self.wave}", 20, SCREEN_HEIGHT - 190, arcade.color.CYAN, 20, bold=True)

        boss_progress = min(self.player.score / 1000, 1.0)
        boss_width = 400 * boss_progress
        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH - 450,
            right=SCREEN_WIDTH - 50,
            bottom=SCREEN_HEIGHT - 70,
            top=SCREEN_HEIGHT - 30,
            color=(50, 50, 50)
        )
        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH - 450,
            right=SCREEN_WIDTH - 450 + boss_width,
            bottom=SCREEN_HEIGHT - 70,
            top=SCREEN_HEIGHT - 30,
            color=arcade.color.RED
        )
        arcade.draw_text(f"ДАРТ ВЕЙДЕР: {int(boss_progress * 100)}%",
                         SCREEN_WIDTH - 440, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16, bold=True)

        arcade.draw_text("УПРАВЛЕНИЕ: WASD - движение, ПРОБЕЛ - стрельба, Q/E - смена оружия",
                         SCREEN_WIDTH // 2, 30, arcade.color.LIGHT_GRAY, 16, anchor_x="center")

        arcade.draw_text("ТЕЛЕПОРТ: Z/X/C/V (вверх/вниз/влево/вправо)",
                         SCREEN_WIDTH // 2, 10, arcade.color.LIGHT_GRAY, 12, anchor_x="center")

        self.draw_upgrades()

        if self.boss_active and self.darth_vader:
            boss_health_width = 600 * (self.darth_vader.health / self.darth_vader.max_health)
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - 300,
                right=SCREEN_WIDTH // 2 + 300,
                bottom=SCREEN_HEIGHT - 180,
                top=SCREEN_HEIGHT - 140,
                color=(100, 0, 0)
            )
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - 300,
                right=SCREEN_WIDTH // 2 - 300 + boss_health_width,
                bottom=SCREEN_HEIGHT - 180,
                top=SCREEN_HEIGHT - 140,
                color=arcade.color.RED
            )
            arcade.draw_text(f"ДАРТ ВЕЙДЕР: {int(self.darth_vader.health)}/{self.darth_vader.max_health}",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT - 170,
                             arcade.color.WHITE, 24, anchor_x="center", bold=True)

            phase_text = "ФАЗА 1" if self.darth_vader.phase == 1 else "ФАЗА 2" if self.darth_vader.phase == 2 else "ФАЗА 3"
            phase_color = arcade.color.RED if self.darth_vader.phase == 1 else arcade.color.ORANGE if self.darth_vader.phase == 2 else arcade.color.PURPLE
            arcade.draw_text(f"{phase_text} {'(ЯРОСТЬ)' if self.darth_vader.rage_mode else ''}",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200,
                             phase_color, 20, anchor_x="center", bold=True)

        if self.player.teleport_cooldown > 0:
            teleport_progress = self.player.teleport_cooldown / self.player.teleport_max_cooldown
            arcade.draw_text(f"ТЕЛЕПОРТ: {int(teleport_progress * 100)}%",
                             SCREEN_WIDTH - 200, 50, arcade.color.CYAN, 14)

        if self.player.shield_bash_cooldown > 0:
            bash_progress = self.player.shield_bash_cooldown / self.player.shield_bash_max_cooldown
            arcade.draw_text(f"ЩИТОВОЙ УДАР: {int(bash_progress * 100)}%",
                             SCREEN_WIDTH - 200, 70, arcade.color.BLUE, 14)

        if self.player.magnet_active:
            arcade.draw_text(f"МАГНИТ: {self.player.magnet_duration // 60}с",
                             SCREEN_WIDTH - 200, 90, arcade.color.GREEN, 14)

        if self.player.time_warp_active:
            arcade.draw_text(f"ЗАМЕДЛЕНИЕ: {self.player.time_warp_duration // 60}с",
                             SCREEN_WIDTH - 200, 110, arcade.color.PURPLE, 14)

    def draw_upgrades(self):
        if not self.player:
            return

        upgrade_y = SCREEN_HEIGHT - 220
        arcade.draw_lrbt_rectangle_filled(
            left=20,
            right=500,
            bottom=upgrade_y - 160,
            top=upgrade_y + 40,
            color=(30, 30, 30, 200)
        )

        arcade.draw_text("УЛУЧШЕНИЯ:", 40, upgrade_y + 20, arcade.color.YELLOW, 18, bold=True)

        y_offset = upgrade_y - 10
        shield_color = arcade.color.GREEN if self.player.score >= UPGRADE_COST_SHIELD else arcade.color.RED
        arcade.draw_text(f"1. ЩИТ (+75): {UPGRADE_COST_SHIELD} очков", 40, y_offset, shield_color, 14)
        y_offset -= 25

        speed_color = arcade.color.GREEN if self.player.score >= UPGRADE_COST_SPEED else arcade.color.RED
        arcade.draw_text(f"2. СКОРОСТЬ (+1.5): {UPGRADE_COST_SPEED} очков", 40, y_offset, speed_color, 14)
        y_offset -= 25

        damage_color = arcade.color.GREEN if self.player.score >= UPGRADE_COST_DAMAGE else arcade.color.RED
        arcade.draw_text(f"3. УРОН (+10): {UPGRADE_COST_DAMAGE} очков", 40, y_offset, damage_color, 14)
        y_offset -= 25

        explosive_color = arcade.color.GREEN if self.player.score >= UPGRADE_COST_EXPLOSIVE else arcade.color.RED
        arcade.draw_text(f"4. ВЗРЫВНЫЕ ПУЛИ: {UPGRADE_COST_EXPLOSIVE} очков", 40, y_offset, explosive_color, 14)
        y_offset -= 25

        teleport_color = arcade.color.GREEN if self.player.score >= UPGRADE_COST_TELEPORT else arcade.color.RED
        arcade.draw_text(f"5. ТЕЛЕПОРТ: {UPGRADE_COST_TELEPORT} очков", 40, y_offset, teleport_color, 14)
        y_offset -= 25

        magnet_color = arcade.color.GREEN if self.player.score >= UPGRADE_COST_MAGNET else arcade.color.RED
        arcade.draw_text(f"6. МАГНИТ: {UPGRADE_COST_MAGNET} очков", 40, y_offset, magnet_color, 14)
        y_offset -= 25

        bash_color = arcade.color.GREEN if self.player.score >= UPGRADE_COST_SHIELD_BASH else arcade.color.RED
        arcade.draw_text(f"7. ЩИТОВОЙ УДАР: {UPGRADE_COST_SHIELD_BASH} очков", 40, y_offset, bash_color, 14)
        y_offset -= 25

        warp_color = arcade.color.GREEN if self.player.score >= UPGRADE_COST_TIME_WARP else arcade.color.RED
        arcade.draw_text(f"8. ЗАМЕДЛЕНИЕ ВРЕМЕНИ: {UPGRADE_COST_TIME_WARP} очков", 40, y_offset, warp_color, 14)

    def on_update(self, delta_time):
        if self.current_screen == "menu":
            for star in self.stars:
                star['y'] -= 0.5
                if star['y'] < 0:
                    star['y'] = SCREEN_HEIGHT
                    star['x'] = random.randint(0, SCREEN_WIDTH)

        elif self.current_screen == "credits":
            self.credits_y -= 0.8

            if self.credits_y < -2000:
                self.current_screen = "menu"
                self.credits_y = SCREEN_HEIGHT + 50

            for star in self.stars:
                star['y'] -= 0.3
                if star['y'] < 0:
                    star['y'] = SCREEN_HEIGHT
                    star['x'] = random.randint(0, SCREEN_WIDTH)

        elif self.current_screen == "game":
            if self.game_over or not self.player:
                return

            self.player.update(delta_time)

            if self.player.shooting and self.player.bullet_cooldown <= 0:
                angles = [90]
                if self.player.double_shot:
                    angles = [80, 100]
                elif self.player.triple_shot:
                    angles = [70, 90, 110]

                for angle in angles:
                    bullet = EnhancedBullet(
                        self.player.center_x,
                        self.player.top,
                        angle,
                        self.player.damage,
                        True,
                        self.is_3d,
                        self.player.bullet_type,
                        self.player.explosive_bullets
                    )
                    self.player_bullets.append(bullet)
                self.player.bullet_cooldown = self.player.bullet_cooldown_max

            if self.player.score >= 1000 and not self.boss_active:
                self.boss_active = True
                self.darth_vader = DarthVader(self.is_3d)
                self.enemies.clear()
                self.asteroids.clear()
                self.planets.clear()

            if self.boss_active and self.darth_vader:
                self.darth_vader.update(delta_time, self.player)

                if self.darth_vader.attack_timer == 0:
                    bullets = self.darth_vader.execute_attack(self.player)
                    for bullet in bullets:
                        self.enemy_bullets.append(bullet)

                for particle in self.darth_vader.force_lightning_particles:
                    if self.player and abs(particle['x'] - self.player.center_x) < self.player.width / 2 and \
                            abs(particle['y'] - self.player.center_y) < self.player.height / 2:
                        self.player.health -= 3
                        if self.player.health <= 0:
                            self.player.health = 0
                            self.game_over = True
                            self.current_screen = "game_over"

                if self.darth_vader.lightsaber_active:
                    saber_angle = math.radians(self.darth_vader.lightsaber_angle)
                    saber_x = self.darth_vader.center_x + math.cos(saber_angle) * 60
                    saber_y = self.darth_vader.center_y - 40 + math.sin(saber_angle) * 60

                    distance = math.sqrt(
                        (saber_x - self.player.center_x) ** 2 +
                        (saber_y - self.player.center_y) ** 2
                    )
                    if distance < (30 + self.player.width / 2):
                        self.player.health -= 8
                        if self.player.health <= 0:
                            self.player.health = 0
                            self.game_over = True
                            self.current_screen = "game_over"

                for bullet in self.player_bullets[:]:
                    if (self.darth_vader and
                            not self.darth_vader.invulnerable and
                            abs(bullet.center_x - self.darth_vader.center_x) < self.darth_vader.width / 2 and
                            abs(bullet.center_y - self.darth_vader.center_y) < self.darth_vader.height / 2):
                        self.darth_vader.health -= bullet.damage
                        if not bullet.piercing:
                            self.player_bullets.remove(bullet)

                        if bullet.explosive:
                            explosion = Explosion(bullet.center_x, bullet.center_y)
                            self.explosions.append(explosion)

                        if self.darth_vader.health <= 0:
                            self.player.score += 500
                            self.game_over = True
                            self.current_screen = "game_over"

                if (self.darth_vader and
                        abs(self.player.center_x - self.darth_vader.center_x) < (
                                self.player.width / 2 + self.darth_vader.width / 2) and
                        abs(self.player.center_y - self.darth_vader.center_y) < (
                                self.player.height / 2 + self.darth_vader.height / 2)):
                    self.player.health -= 15
                    if self.player.health <= 0:
                        self.player.health = 0
                        self.game_over = True
                        self.current_screen = "game_over"

            if not self.boss_active:
                for enemy in self.enemies[:]:
                    if self.player.time_warp_active:
                        enemy.update(delta_time * self.player.time_slow_factor)
                    else:
                        enemy.update(delta_time)

                    if enemy.center_y < -50:
                        self.enemies.remove(enemy)
                        continue

                    if enemy.bullet_cooldown > 0:
                        enemy.bullet_cooldown -= 1
                    else:
                        dx = self.player.center_x - enemy.center_x
                        dy = self.player.center_y - enemy.center_y
                        angle = math.degrees(math.atan2(dy, dx))
                        bullet = EnhancedBullet(enemy.center_x, enemy.center_y, angle, 8, False, self.is_3d)
                        self.enemy_bullets.append(bullet)
                        enemy.bullet_cooldown = random.randint(60, 120)

            for asteroid in self.asteroids[:]:
                if self.player.time_warp_active:
                    asteroid.update(delta_time * self.player.time_slow_factor)
                else:
                    asteroid.update(delta_time)
                if asteroid.center_y < -50:
                    self.asteroids.remove(asteroid)

            for planet in self.planets[:]:
                if self.player.time_warp_active:
                    planet.update(delta_time * self.player.time_slow_factor)
                else:
                    planet.update(delta_time)
                if planet.center_y < -50:
                    self.planets.remove(planet)

            for explosion in self.explosions[:]:
                explosion.update(delta_time)
                if not explosion.active:
                    self.explosions.remove(explosion)
                else:
                    if self.boss_active and self.darth_vader and not self.darth_vader.invulnerable:
                        distance = math.sqrt((explosion.center_x - self.darth_vader.center_x) ** 2 +
                                             (explosion.center_y - self.darth_vader.center_y) ** 2)
                        if distance < explosion.current_radius + self.darth_vader.width / 2:
                            self.darth_vader.health -= explosion.damage * (
                                        1 - distance / (explosion.max_radius + self.darth_vader.width / 2))
                            if self.darth_vader.health <= 0:
                                self.player.score += 500
                                self.game_over = True
                                self.current_screen = "game_over"

            for power_up in self.power_ups[:]:
                power_up.update(delta_time)
                if not power_up.active:
                    self.power_ups.remove(power_up)
                elif self.player.magnet_active:
                    distance = math.sqrt((power_up.center_x - self.player.center_x) ** 2 +
                                         (power_up.center_y - self.player.center_y) ** 2)
                    if distance < self.player.magnet_radius:
                        dx = self.player.center_x - power_up.center_x
                        dy = self.player.center_y - power_up.center_y
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist > 0:
                            power_up.center_x += dx / dist * 10
                            power_up.center_y += dy / dist * 10

            for bullet in self.player_bullets[:]:
                if isinstance(bullet, EnhancedBullet):
                    if not bullet.update(delta_time):
                        self.player_bullets.remove(bullet)
                else:
                    bullet.update(delta_time)

                if (bullet.center_x < -50 or bullet.center_x > SCREEN_WIDTH + 50 or
                        bullet.center_y < -50 or bullet.center_y > SCREEN_HEIGHT + 50):
                    self.player_bullets.remove(bullet)

            for bullet in self.enemy_bullets[:]:
                if isinstance(bullet, EnhancedBullet):
                    if not bullet.update(delta_time):
                        self.enemy_bullets.remove(bullet)
                else:
                    bullet.update(delta_time)

                if (bullet.center_x < -50 or bullet.center_x > SCREEN_WIDTH + 50 or
                        bullet.center_y < -50 or bullet.center_y > SCREEN_HEIGHT + 50):
                    self.enemy_bullets.remove(bullet)

            for bullet in self.player_bullets[:]:
                if self.boss_active and self.darth_vader and not self.darth_vader.invulnerable:
                    distance = math.sqrt(
                        (bullet.center_x - self.darth_vader.center_x) ** 2 +
                        (bullet.center_y - self.darth_vader.center_y) ** 2
                    )
                    if distance < (bullet.radius + self.darth_vader.width / 2):
                        self.darth_vader.health -= bullet.damage
                        if not bullet.piercing:
                            self.player_bullets.remove(bullet)
                            if bullet.explosive:
                                explosion = Explosion(bullet.center_x, bullet.center_y)
                                self.explosions.append(explosion)

                        if self.darth_vader.health <= 0:
                            self.player.score += 500
                            self.game_over = True
                            self.current_screen = "game_over"

                for enemy in self.enemies[:]:
                    distance = math.sqrt(
                        (bullet.center_x - enemy.center_x) ** 2 +
                        (bullet.center_y - enemy.center_y) ** 2
                    )
                    if distance < (bullet.radius + enemy.width / 2):
                        enemy.health -= bullet.damage
                        if bullet in self.player_bullets:
                            self.player_bullets.remove(bullet)
                            if bullet.explosive:
                                explosion = Explosion(bullet.center_x, bullet.center_y)
                                self.explosions.append(explosion)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.player.score += 50
                            self.enemies_killed += 1

                            if random.random() < 0.2:
                                power_types = ["health", "shield", "damage", "speed"]
                                power_up = PowerUp(enemy.center_x, enemy.center_y, random.choice(power_types))
                                self.power_ups.append(power_up)
                        break

                for asteroid in self.asteroids[:]:
                    distance = math.sqrt(
                        (bullet.center_x - asteroid.center_x) ** 2 +
                        (bullet.center_y - asteroid.center_y) ** 2
                    )
                    if distance < (bullet.radius + asteroid.radius):
                        asteroid.health -= bullet.damage
                        if bullet in self.player_bullets:
                            self.player_bullets.remove(bullet)
                            if bullet.explosive:
                                explosion = Explosion(bullet.center_x, bullet.center_y)
                                self.explosions.append(explosion)
                        if asteroid.health <= 0:
                            self.asteroids.remove(asteroid)
                            self.player.score += asteroid.points

                            if random.random() < 0.15:
                                power_types = ["health", "shield", "damage", "speed"]
                                power_up = PowerUp(asteroid.center_x, asteroid.center_y, random.choice(power_types))
                                self.power_ups.append(power_up)
                        break

                for planet in self.planets[:]:
                    distance = math.sqrt(
                        (bullet.center_x - planet.center_x) ** 2 +
                        (bullet.center_y - planet.center_y) ** 2
                    )
                    if distance < (bullet.radius + planet.radius):
                        planet.health -= bullet.damage
                        if bullet in self.player_bullets:
                            self.player_bullets.remove(bullet)
                            if bullet.explosive:
                                explosion = Explosion(bullet.center_x, bullet.center_y)
                                self.explosions.append(explosion)
                        if planet.health <= 0:
                            self.planets.remove(planet)
                            self.player.score += planet.points

                            if random.random() < 0.25:
                                power_types = ["health", "shield", "damage", "speed"]
                                power_up = PowerUp(planet.center_x, planet.center_y, random.choice(power_types))
                                self.power_ups.append(power_up)
                        break

            for bullet in self.enemy_bullets[:]:
                distance = math.sqrt(
                    (bullet.center_x - self.player.center_x) ** 2 +
                    (bullet.center_y - self.player.center_y) ** 2
                )
                if distance < (bullet.radius + self.player.width / 2):
                    if self.player.shield > 0:
                        self.player.shield -= bullet.damage
                        if self.player.shield < 0:
                            self.player.health += self.player.shield
                            self.player.shield = 0
                    else:
                        self.player.health -= bullet.damage

                    if not bullet.piercing:
                        self.enemy_bullets.remove(bullet)

                    if self.player.health <= 0:
                        self.player.health = 0
                        self.game_over = True
                        self.current_screen = "game_over"

            for enemy in self.enemies[:]:
                distance = math.sqrt(
                    (self.player.center_x - enemy.center_x) ** 2 +
                    (self.player.center_y - enemy.center_y) ** 2
                )
                if distance < (self.player.width / 2 + enemy.width / 2):
                    if self.player.shield_bash:
                        enemy.health -= 25
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.player.score += 50
                            self.enemies_killed += 1
                        dx = enemy.center_x - self.player.center_x
                        dy = enemy.center_y - self.player.center_y
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist > 0:
                            enemy.center_x += dx / dist * 80
                            enemy.center_y += dy / dist * 80
                    else:
                        self.player.health -= 15
                        self.enemies.remove(enemy)

                    if self.player.health <= 0:
                        self.player.health = 0
                        self.game_over = True
                        self.current_screen = "game_over"

            for asteroid in self.asteroids[:]:
                distance = math.sqrt(
                    (self.player.center_x - asteroid.center_x) ** 2 +
                    (self.player.center_y - asteroid.center_y) ** 2
                )
                if distance < (self.player.width / 2 + asteroid.radius):
                    self.player.health -= 25
                    self.asteroids.remove(asteroid)

                    if self.player.health <= 0:
                        self.player.health = 0
                        self.game_over = True
                        self.current_screen = "game_over"

            for planet in self.planets[:]:
                distance = math.sqrt(
                    (self.player.center_x - planet.center_x) ** 2 +
                    (self.player.center_y - planet.center_y) ** 2
                )
                if distance < (self.player.width / 2 + planet.radius):
                    self.player.health -= 40
                    self.planets.remove(planet)

                    if self.player.health <= 0:
                        self.player.health = 0
                        self.game_over = True
                        self.current_screen = "game_over"

            if not self.boss_active:
                self.spawn_timer += delta_time * 60
                spawn_interval = max(20, 50 - self.wave * 4)

                if self.spawn_timer >= spawn_interval:
                    if random.random() < 0.5:
                        enemy = Enemy(self.is_3d)
                        enemy.speed += self.wave * 0.15
                        self.enemies.append(enemy)

                    if random.random() < 0.3:
                        asteroid = Asteroid(self.is_3d)
                        self.asteroids.append(asteroid)

                    if random.random() < 0.2:
                        planet = Planet(self.is_3d)
                        self.planets.append(planet)

                    self.spawn_timer = 0

                if self.enemies_killed >= 15 + self.wave * 3:
                    self.wave += 1
                    self.enemies_killed = 0
                    self.player.health = min(self.player.max_health, self.player.health + 30)

                    if self.wave % 3 == 0:
                        self.player.double_shot = not self.player.double_shot
                        if self.player.double_shot:
                            self.player.triple_shot = False
                    elif self.wave % 5 == 0:
                        self.player.triple_shot = True
                        self.player.double_shot = False

            for star in self.stars:
                star['y'] -= 0.5
                if star['y'] < 0:
                    star['y'] = SCREEN_HEIGHT
                    star['x'] = random.randint(0, SCREEN_WIDTH)

    def on_key_press(self, key, modifiers):
        if self.current_screen == "menu":
            if key == arcade.key.SPACE:
                self.setup_game()
            elif key == arcade.key.UP or key == arcade.key.DOWN:
                self.is_3d = not self.is_3d

        elif self.current_screen == "game_over":
            if key == arcade.key.SPACE:
                if self.boss_active and self.darth_vader and self.darth_vader.health <= 0:
                    self.current_screen = "credits"
                    self.credits_y = SCREEN_HEIGHT + 50
                else:
                    self.current_screen = "menu"

        elif self.current_screen == "credits":
            if key == arcade.key.SPACE:
                self.current_screen = "menu"
                self.credits_y = SCREEN_HEIGHT + 50

        elif self.current_screen == "game":
            if self.game_over or not self.player:
                return

            if key == arcade.key.W:
                self.player.move_up = True
            elif key == arcade.key.S:
                self.player.move_down = True
            elif key == arcade.key.A:
                self.player.move_left = True
            elif key == arcade.key.D:
                self.player.move_right = True

            elif key == arcade.key.SPACE:
                self.player.shooting = True
                if self.player.bullet_cooldown <= 0:
                    angles = [90]
                    if self.player.double_shot:
                        angles = [80, 100]
                    elif self.player.triple_shot:
                        angles = [70, 90, 110]

                    for angle in angles:
                        bullet = EnhancedBullet(
                            self.player.center_x,
                            self.player.top,
                            angle,
                            self.player.damage,
                            True,
                            self.is_3d,
                            self.player.bullet_type,
                            self.player.explosive_bullets
                        )
                        self.player_bullets.append(bullet)
                    self.player.bullet_cooldown = self.player.bullet_cooldown_max

            elif key == arcade.key.Z:
                self.player.teleport("up")
            elif key == arcade.key.X:
                self.player.teleport("down")
            elif key == arcade.key.C:
                self.player.teleport("left")
            elif key == arcade.key.V:
                self.player.teleport("right")
            elif key == arcade.key.B:
                if self.player.activate_shield_bash():
                    for enemy in self.enemies[:]:
                        distance = math.sqrt(
                            (self.player.center_x - enemy.center_x) ** 2 +
                            (self.player.center_y - enemy.center_y) ** 2
                        )
                        if distance < 100:
                            enemy.health -= 25
                            dx = enemy.center_x - self.player.center_x
                            dy = enemy.center_y - self.player.center_y
                            dist = math.sqrt(dx * dx + dy * dy)
                            if dist > 0:
                                enemy.center_x += dx / dist * 80
                                enemy.center_y += dy / dist * 80
            elif key == arcade.key.T:
                self.player.activate_time_warp()
                if self.player.time_warp_active:
                    for enemy in self.enemies:
                        enemy.slow_down(180, 0.5)

            elif key == arcade.key.Q:
                weapons = ["normal", "laser", "rocket"]
                current_idx = weapons.index(self.player.bullet_type)
                self.player.bullet_type = weapons[(current_idx - 1) % len(weapons)]
            elif key == arcade.key.E:
                weapons = ["normal", "laser", "rocket"]
                current_idx = weapons.index(self.player.bullet_type)
                self.player.bullet_type = weapons[(current_idx + 1) % len(weapons)]

            elif key == arcade.key.KEY_1 or key == arcade.key.NUM_1:
                if self.player.score >= UPGRADE_COST_SHIELD:
                    self.player.score -= UPGRADE_COST_SHIELD
                    self.player.max_shield += 75
                    self.player.shield = self.player.max_shield

            elif key == arcade.key.KEY_2 or key == arcade.key.NUM_2:
                if self.player.score >= UPGRADE_COST_SPEED:
                    self.player.score -= UPGRADE_COST_SPEED
                    self.player.speed += 1.5

            elif key == arcade.key.KEY_3 or key == arcade.key.NUM_3:
                if self.player.score >= UPGRADE_COST_DAMAGE:
                    self.player.score -= UPGRADE_COST_DAMAGE
                    self.player.damage += 10

            elif key == arcade.key.KEY_4 or key == arcade.key.NUM_4:
                if self.player.score >= UPGRADE_COST_EXPLOSIVE:
                    self.player.score -= UPGRADE_COST_EXPLOSIVE
                    self.player.explosive_bullets = True

            elif key == arcade.key.KEY_5 or key == arcade.key.NUM_5:
                if self.player.score >= UPGRADE_COST_TELEPORT:
                    self.player.score -= UPGRADE_COST_TELEPORT
                    self.player.teleport_distance = 250
                    self.player.teleport_max_cooldown = 120

            elif key == arcade.key.KEY_6 or key == arcade.key.NUM_6:
                if self.player.score >= UPGRADE_COST_MAGNET:
                    self.player.score -= UPGRADE_COST_MAGNET
                    self.player.magnet_active = True
                    self.player.magnet_duration = self.player.magnet_max_duration
                    self.player.magnet_radius = 200

            elif key == arcade.key.KEY_7 or key == arcade.key.NUM_7:
                if self.player.score >= UPGRADE_COST_SHIELD_BASH:
                    self.player.score -= UPGRADE_COST_SHIELD_BASH
                    self.player.shield_bash = True
                    self.player.shield_bash_max_cooldown = 200

            elif key == arcade.key.KEY_8 or key == arcade.key.NUM_8:
                if self.player.score >= UPGRADE_COST_TIME_WARP:
                    self.player.score -= UPGRADE_COST_TIME_WARP
                    self.player.time_warp_max_duration = 400
                    self.player.time_slow_factor = 0.3

    def on_key_release(self, key, modifiers):
        if self.current_screen == "game" and self.player:
            if key == arcade.key.W:
                self.player.move_up = False
            elif key == arcade.key.S:
                self.player.move_down = False
            elif key == arcade.key.A:
                self.player.move_left = False
            elif key == arcade.key.D:
                self.player.move_right = False

            elif key == arcade.key.SPACE:
                self.player.shooting = False

    def on_mouse_motion(self, x, y, dx, dy):
        if self.current_screen == "menu":
            button_left = SCREEN_WIDTH // 2 - 200
            button_right = SCREEN_WIDTH // 2 + 200
            button_3d_top = SCREEN_HEIGHT - 360
            button_3d_bottom = SCREEN_HEIGHT - 440
            button_2d_top = SCREEN_HEIGHT - 480
            button_2d_bottom = SCREEN_HEIGHT - 560

            if (button_left <= x <= button_right and
                    button_3d_bottom <= y <= button_3d_top):
                self.is_3d = True
            elif (button_left <= x <= button_right and
                  button_2d_bottom <= y <= button_2d_top):
                self.is_3d = False

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_screen == "menu" and button == arcade.MOUSE_BUTTON_LEFT:
            button_left = SCREEN_WIDTH // 2 - 200
            button_right = SCREEN_WIDTH // 2 + 200
            button_3d_top = SCREEN_HEIGHT - 360
            button_3d_bottom = SCREEN_HEIGHT - 440
            button_2d_top = SCREEN_HEIGHT - 480
            button_2d_bottom = SCREEN_HEIGHT - 560

            if (button_left <= x <= button_right and
                    button_3d_bottom <= y <= button_3d_top):
                self.is_3d = True
                self.setup_game()
            elif (button_left <= x <= button_right and
                  button_2d_bottom <= y <= button_2d_top):
                self.is_3d = False
                self.setup_game()


def main():
    game = SpaceGame()
    arcade.run()


if __name__ == "__main__":
    main()