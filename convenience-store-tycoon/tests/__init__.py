"""测试包：把项目根目录加入 sys.path，便于 unittest discover。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
