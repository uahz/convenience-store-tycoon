"""存档：版本化 JSON、迁移链、原子写入、槽位管理。

- 序列化走各模型的显式 to_save/from_save（字段改名不会静默破坏旧档）。
- format_version 更高 → 拒绝读取（不猜测兼容）。
- 写入 = 临时文件 + os.replace 原子替换，避免半写损坏。
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict

from config import APP_VERSION
from core.rng import GameRNG
from core.state import GameState

FORMAT_VERSION = 1
# {旧版本号: 迁移函数(dict)->dict}；升级存档时沿链逐级执行
MIGRATIONS: Dict[int, Callable[[dict], dict]] = {}


def _app_dir() -> Path:
    """应用根目录：源码运行 = 项目根；打包(frozen) = exe 所在目录，
    保证存档不会落到 PyInstaller 的临时解压目录里。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


_SAVES_DIR = _app_dir() / "saves"


class SaveError(Exception):
    pass


def slot_path(name: str = "autosave") -> Path:
    return _SAVES_DIR / f"{name}.json"


def has_save(name: str = "autosave") -> bool:
    return slot_path(name).exists()


def delete_save(name: str = "autosave") -> None:
    path = slot_path(name)
    if path.exists():
        path.unlink()


def save(game, name: str = "autosave") -> Path:
    """game: core.game.Game（鸭子类型：需要 .rng 与 .state）。"""
    if game.state is None:
        raise SaveError("尚未开始游戏，无法保存")
    _SAVES_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "format_version": FORMAT_VERSION,
        "app_version": APP_VERSION,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "rng_state": game.rng.to_save(),
        "game": game.state.to_save(),
    }
    path = slot_path(name)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    os.replace(tmp, path)
    return path


def load(game, name: str = "autosave") -> dict:
    """读档并填充 game（.state/.rng）。返回存档元信息 dict。"""
    path = slot_path(name)
    if not path.exists():
        raise SaveError("存档不存在")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SaveError(f"存档损坏：{exc}") from exc

    version = int(data.get("format_version", 0))
    if version > FORMAT_VERSION:
        raise SaveError(f"存档版本 v{version} 高于当前游戏 v{FORMAT_VERSION}，"
                        "请升级游戏后再读取")
    while version < FORMAT_VERSION:
        if version not in MIGRATIONS:
            raise SaveError(f"缺少从 v{version} 到下一版本的迁移路径")
        data = MIGRATIONS[version](data)
        version = int(data["format_version"])

    game.state = GameState.from_save(data["game"])
    game.rng = GameRNG.from_save(data["rng_state"])
    game.last_daylog = None
    game.last_report = None
    game.pending_spoilage_cost = 0.0
    game.pending_spoilage_items = []
    return {"created_at": data.get("created_at", "?"),
            "app_version": data.get("app_version", "?"),
            "day": game.state.day, "cash": game.state.cash,
            "reputation": game.state.reputation}
