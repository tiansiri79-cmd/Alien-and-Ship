import sys
import pygame
import os
import random

from settings import Settings
from ship import Ship
from bullet import Bullet, AlienBullet
from alien import Alien
from game_stats import GameStats
from shield import Shield   # 独立护盾类


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")

        # 统计信息
        self.stats = GameStats(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()       # 玩家子弹
        self.aliens = pygame.sprite.Group()        # 外星人
        self.alien_bullets = pygame.sprite.Group() # 外星人子弹

        # 游戏开始时间（用来计算经过的秒数）
        self.start_time = pygame.time.get_ticks()

        # ---------- 护盾：由 Shield 类管理 ----------
        self.shield = Shield(
            max_charges=2,      # 最多 2 次
            cooldown_ms=30_000, # 每 30 秒恢复一次
            duration_ms=15_000, # 持续 15 秒
            initial_charges=1,  # 初始 1 次
        )

        # 字体用于显示分数 / 最高分 / 生命 / 护盾状态
        self.font = pygame.font.SysFont(None, 36)

        # 初始化声音
        self._init_sounds()

        # 初始生成一些随机外星人
        self._create_initial_aliens()

    # ---------- 声音相关 ----------

    def _init_sounds(self):
        sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')
        laser_path = os.path.join(sounds_dir, 'laser.wav')
        explosion_path = os.path.join(sounds_dir, 'explosion.wav')

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            self.laser_sound = None
            self.explosion_sound = None
            print("Warning: pygame.mixer 初始化失败，已禁用音效。")
            return

        def _load(path):
            if os.path.exists(path):
                try:
                    return pygame.mixer.Sound(path)
                except pygame.error:
                    print(f"Warning: 无法加载音效文件：{path}")
                    return None
            else:
                print(f"Warning: 未找到音效文件：{path}")
                return None

        self.laser_sound = _load(laser_path)
        self.explosion_sound = _load(explosion_path)

    # ---------- 主循环 ----------

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullets()

                # 每帧更新时间并交给 Shield 管理护盾
                now = pygame.time.get_ticks()
                self.shield.update(now)

            self._update_screen()
            self.clock.tick(60)

    # ---------- 事件处理 ----------

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_and_quit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key in (pygame.K_RIGHT, pygame.K_d):
            self.ship.moving_right = True
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.ship.moving_left = True
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.ship.moving_up = True
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            self._save_and_quit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_t:
            # 按 T 键激活护盾（交给 Shield 判断次数和冷却）
            if self.stats.game_active:
                now = pygame.time.get_ticks()
                self.shield.activate(now)

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key in (pygame.K_RIGHT, pygame.K_d):
            self.ship.moving_right = False
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.ship.moving_left = False
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.ship.moving_up = False
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.ship.moving_down = False

    def _save_and_quit(self):
        """退出游戏前保存最高分。"""
        self.stats.save_high_score()
        sys.exit()

    # ---------- 玩家子弹相关 ----------

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed and self.stats.game_active:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

            if getattr(self, "laser_sound", None):
                self.laser_sound.play()

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)

            if getattr(self, "explosion_sound", None):
                self.explosion_sound.play()

            if self.stats.score > self.stats.high_score:
                self.stats.high_score = self.stats.score

    # ---------- 外星人相关 ----------

    def _create_initial_aliens(self):
        """初始生成一些随机外星人。"""
        for _ in range(5):
            self._create_random_alien()

    def _create_random_alien(self):
        """Create an alien and place it randomly."""
        new_alien = Alien(self)
        self.aliens.add(new_alien)

    def _update_aliens(self):
        """Update the positions of all aliens，随机生成并检测碰撞。"""
        self.aliens.update()

        # 随机刷怪
        if len(self.aliens) < self.settings.max_aliens:
            if random.random() < self.settings.alien_spawn_chance:
                self._create_random_alien()

        # 只在“碰到飞船”时才可能扣命；到达底部不再扣命
        self._check_aliens_bottom_or_hit_ship()

        # 外星人从一开始就会发射子弹
        elapsed_seconds = (pygame.time.get_ticks() - self.start_time) / 1000
        self._alien_fire_bullets(elapsed_seconds)

    def _check_aliens_bottom_or_hit_ship(self):
        """
        检查外星人是否撞到飞船或到达屏幕底部。

        修改点：
        - 撞到飞船：先让护盾尝试吃掉伤害，只在护盾失败时扣命。
        - 到达屏幕底部：只删除外星人，不再调用 _ship_hit() 扣命。
        """
        screen_rect = self.screen.get_rect()

        # 与飞船碰撞
        colliding_aliens = pygame.sprite.spritecollide(self.ship, self.aliens, True)
        if colliding_aliens:
            # 先尝试让护盾吃掉伤害（成功则不扣命）
            if not self.shield.consume_if_active():
                self._ship_hit()

        # 到达底部：只删除外星人，不扣命
        for alien in self.aliens.copy():
            if alien.rect.bottom >= screen_rect.bottom:
                self.aliens.remove(alien)

    # ---------- 外星人子弹相关 ----------

    def _alien_fire_bullets(self, elapsed_seconds):
        """外星人随机发射子弹：从一开始就会射击。"""
        if len(self.alien_bullets) >= self.settings.alien_bullets_allowed:
            return

        for alien in self.aliens.sprites():
            if random.random() < self.settings.alien_fire_chance:
                bullet = AlienBullet(self, alien)
                self.alien_bullets.add(bullet)

    def _update_alien_bullets(self):
        """更新外星人子弹位置并检测与飞船的碰撞。"""
        self.alien_bullets.update()

        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)

        colliding_bullets = pygame.sprite.spritecollide(
            self.ship, self.alien_bullets, True
        )
        if colliding_bullets:
            # 先尝试让护盾吃掉伤害；若护盾不存在，则真正扣命
            if not self.shield.consume_if_active():
                self._ship_hit()

    # ---------- 飞船被击中 / GAME OVER ----------

    def _ship_hit(self):
        """
        处理飞船被外星人或子弹击中（生命值 -1，生命为 0 则游戏结束并提示 Game Over）。
        注意：这里已经确保是“护盾没挡住”的真正伤害。
        """
        if not self.stats.game_active:
            return

        if self.stats.ships_left > 1:
            self.stats.ships_left -= 1

            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()

            self._create_initial_aliens()
            self.ship.center_ship()

            pygame.time.delay(500)
        else:
            self.stats.ships_left = 0
            self.stats.game_active = False
            self.stats.save_high_score()

    # ---------- 绘制屏幕 ----------

    def _draw_scoreboard(self):
        """在屏幕上绘制分数、最高分、生命值和护盾状态。"""
        text_color = (30, 30, 30)
        bg_color = self.settings.bg_color

        score_str = f"Score: {self.stats.score}"
        high_score_str = f"High Score: {self.stats.high_score}"
        lives_str = f"Lives: {self.stats.ships_left}"

        shield_status = "ON" if self.shield.is_active else "OFF"
        shield_str = f"Shield: {self.shield.charges} ({shield_status})"

        score_img = self.font.render(score_str, True, text_color, bg_color)
        high_score_img = self.font.render(high_score_str, True, text_color, bg_color)
        lives_img = self.font.render(lives_str, True, text_color, bg_color)
        shield_img = self.font.render(shield_str, True, text_color, bg_color)

        score_rect = score_img.get_rect()
        high_score_rect = high_score_img.get_rect()
        lives_rect = lives_img.get_rect()
        shield_rect = shield_img.get_rect()

        score_rect.left = 20
        score_rect.top = 10

        shield_rect.left = 20
        shield_rect.top = score_rect.bottom + 5

        high_score_rect.centerx = self.settings.screen_width // 2
        high_score_rect.top = 10

        lives_rect.right = self.settings.screen_width - 20
        lives_rect.top = 10

        self.screen.blit(score_img, score_rect)
        self.screen.blit(high_score_img, high_score_rect)
        self.screen.blit(lives_img, lives_rect)
        self.screen.blit(shield_img, shield_rect)

    def _draw_game_over(self):
        """生命值归零时在屏幕中间显示 Game Over 提示。"""
        if self.stats.game_active:
            return

        big_font = pygame.font.SysFont(None, 72)
        game_over_str = "GAME OVER"
        tip_str = "Press Q to quit"

        game_over_img = big_font.render(
            game_over_str, True, (255, 0, 0), self.settings.bg_color
        )
        tip_img = self.font.render(
            tip_str, True, (30, 30, 30), self.settings.bg_color
        )

        game_over_rect = game_over_img.get_rect()
        tip_rect = tip_img.get_rect()

        game_over_rect.centerx = self.settings.screen_width // 2
        game_over_rect.centery = self.settings.screen_height // 2 - 30

        tip_rect.centerx = self.settings.screen_width // 2
        tip_rect.top = game_over_rect.bottom + 10

        self.screen.blit(game_over_img, game_over_rect)
        self.screen.blit(tip_img, tip_rect)

    def _draw_shield_circle(self):
        """
        如果护盾激活，在飞船外画一个圆把飞船包住。
        圆只是一种视觉表现，真正的判定仍然用精灵碰撞。
        """
        if not self.shield.is_active:
            return

        # 以飞船中心为圆心，半径略大于飞船
        cx, cy = self.ship.rect.center
        radius = max(self.ship.rect.width, self.ship.rect.height) // 2 + 10
        # 画一个浅蓝色的圆环（只描边）
        color = (0, 200, 255)
        pygame.draw.circle(self.screen, color, (cx, cy), radius, 3)

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.aliens.draw(self.screen)
        self.ship.blitme()

        # 护盾可视化：画一个圆包裹飞船
        self._draw_shield_circle()

        for bullet in self.alien_bullets.sprites():
            bullet.draw_bullet()

        self._draw_scoreboard()

        if not self.stats.game_active and self.stats.ships_left == 0:
            self._draw_game_over()

        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
