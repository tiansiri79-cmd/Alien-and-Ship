import os
import json


class GameStats:
    """跟踪游戏统计信息（避免循环导入：不引用 AlienInvasion）。"""

    def __init__(self, ai_game):
        # 只引用传入的 ai_game 的 settings
        self.settings = ai_game.settings

        # 游戏状态
        self.game_active = True

        # 在每局开始时重置的统计信息
        self.reset_stats()

        # 最高分：从文件中加载
        self.high_score = self._load_high_score()

    def reset_stats(self):
        """在每局开始时重置可变统计信息。"""
        # 如果 settings 里没有 ship_limit，就默认 3 条命
        self.ships_left = getattr(self.settings, "ship_limit", 3)
        self.score = 0
        self.level = 1

    # ---------- 最高分持久化 ----------

    def _load_high_score(self):
        """从 high_score.json 加载最高分（不存在或损坏时返回 0）。"""
        path = os.path.join(os.path.dirname(__file__), "high_score.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("high_score", 0))
        except Exception:
            return 0

    def save_high_score(self):
        """将当前最高分写入 high_score.json（失败时静默处理）。"""
        path = os.path.join(os.path.dirname(__file__), "high_score.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass
