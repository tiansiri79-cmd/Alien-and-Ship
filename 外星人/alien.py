import pygame
from pygame.sprite import Sprite
import random


class Alien(Sprite):
    """A class to represent a single alien."""

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the alien image and set its rect attribute.
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        screen_rect = self.screen.get_rect()

        # 随机出现在屏幕上方区域的任意位置（要求 3 的“随机出现”）
        self.rect.x = random.randint(0, screen_rect.width - self.rect.width)
        self.rect.y = random.randint(0, self.rect.height * 2)

        # 使用 float 存储精确位置
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # 随机速度，产生“ 不规则移动 ”效果
        base = self.settings.alien_speed
        self.vx = random.choice([-1, 1]) * random.uniform(0.3 * base, 1.5 * base)
        self.vy = random.uniform(0.2 * base, 1.0 * base)

    def update(self):
        """不规则移动：随机水平/垂直漂移并在边缘反弹。"""
        screen_rect = self.screen.get_rect()

        # 位置更新
        self.x += self.vx
        self.y += self.vy

        # 与左右边缘碰撞就反弹
        if self.x <= 0 or self.x + self.rect.width >= screen_rect.width:
            self.vx *= -1

        # 让外星人始终大致往下走，但偶尔随机改变方向
        if random.random() < 0.01:
            self.vx *= -1
        if random.random() < 0.01:
            self.vy *= random.choice([0.5, 1.0, 1.5])

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def check_edges(self):
        """兼容旧接口，这里简单判断是否在屏幕外。"""
        screen_rect = self.screen.get_rect()
        return (
            self.rect.right < 0
            or self.rect.left > screen_rect.right
            or self.rect.bottom < 0
            or self.rect.top > screen_rect.bottom
        )
