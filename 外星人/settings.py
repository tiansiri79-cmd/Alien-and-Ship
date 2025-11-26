# settings.py
class Settings:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Ship settings.
        self.ship_speed = 1.5
        # 飞船初始生命值（要求 2）
        self.ship_limit = 3

        # Bullet settings（玩家子弹）
        self.bullet_speed = 2.5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3

        # Alien settings.
        # 这里的 alien_speed 主要作为随机速度的基准
        self.alien_speed = 1.0

        # NEW: score settings
        self.alien_points = 50

        # ------- 外星人随机生成 / 发射子弹设置 -------

        # 屏幕上最多同时存在的外星人数量
        self.max_aliens = 15
        # 每一帧生成新外星人的概率（建议不要太大）
        self.alien_spawn_chance = 0.02  # 2%

        # 外星人子弹设置
        self.alien_bullet_speed = 1.5
        self.alien_bullet_color = (255, 0, 0)
        # 屏幕上最多同时存在的外星人子弹数量
        self.alien_bullets_allowed = 10
        # 单个外星人在一帧中开火的概率（超过 20 秒后才启用）
        self.alien_fire_chance = 0.01  # 1%
