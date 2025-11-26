import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """A class to manage bullets fired from the ship."""

    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # Create a bullet rect at (0, 0) and then set correct position.
        self.rect = pygame.Rect(0, 0,
                                self.settings.bullet_width,
                                self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        # Store the bullet's position as a float.
        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet up the screen."""
        # Update the exact position of the bullet.
        self.y -= self.settings.bullet_speed
        # Update the rect position.
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)


class AlienBullet(Sprite):
    """外星人发射的子弹（向下飞）。"""

    def __init__(self, ai_game, alien):
        """在当前外星人位置创建一颗子弹。"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.alien_bullet_color

        self.rect = pygame.Rect(0, 0,
                                self.settings.bullet_width,
                                self.settings.bullet_height)
        # 子弹从外星人底部中心发射
        self.rect.midtop = alien.rect.midbottom

        # 使用 float 存储纵坐标
        self.y = float(self.rect.y)

    def update(self):
        """子弹向下移动。"""
        self.y += self.settings.alien_bullet_speed
        self.rect.y = self.y

    def draw_bullet(self):
        """绘制外星人子弹。"""
        pygame.draw.rect(self.screen, self.color, self.rect)
