class Shield:
    """Encapsulate shield logic: charges, cooldown, duration, and hit consumption."""

    def __init__(self, max_charges=2, cooldown_ms=30000, duration_ms=15000, initial_charges=1):
        """
        :param max_charges: 护盾最多可累计使用次数
        :param cooldown_ms: 每次自动回复 1 点护盾次数的冷却时间（毫秒）
        :param duration_ms: 护盾激活后持续时间（毫秒）
        :param initial_charges: 初始护盾次数
        """
        self.max_charges = max_charges
        self.cooldown_ms = cooldown_ms
        self.duration_ms = duration_ms

        self.charges = initial_charges     # 当前剩余次数
        self.active = False                # 当前是否正在生效
        self.start_time = None             # 当前这一次护盾启动时间
        self.last_refresh_time = None      # 上一次获得护盾次数的时间

    def update(self, now_ms: int):
        """用当前时间（毫秒）更新护盾持续时间和冷却."""
        # 第一次调用时初始化冷却计时点
        if self.last_refresh_time is None:
            self.last_refresh_time = now_ms

        # 1. 持续时间：超过 duration_ms 自动关闭
        if self.active and self.start_time is not None:
            if now_ms - self.start_time >= self.duration_ms:
                self.active = False
                self.start_time = None

        # 2. 冷却：每 cooldown_ms 自动 +1 次数，直到 max_charges
        if self.charges < self.max_charges:
            if now_ms - self.last_refresh_time >= self.cooldown_ms:
                self.charges += 1
                self.last_refresh_time = now_ms

    def activate(self, now_ms: int):
        """尝试激活护盾：需要有剩余次数且当前未激活。"""
        if (not self.active) and self.charges > 0:
            self.active = True
            self.charges -= 1
            self.start_time = now_ms

    def consume_if_active(self) -> bool:
        """
        让护盾“吃掉”这次伤害（比如外星子弹或外星人碰撞）。
        如果护盾正在生效，则关闭护盾并返回 True；否则返回 False。
        """
        if self.active:
            self.active = False
            self.start_time = None
            return True
        return False

    @property
    def is_active(self) -> bool:
        """是否处于激活状态的只读属性."""
        return self.active
