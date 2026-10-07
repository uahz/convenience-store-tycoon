"""显示主题：颜色开关与字符集（Unicode / ASCII 降级）。"""

import os
import sys

COLOR = True
ASCII = False
BOX: dict = {}

GREEN, RED, YEL, CYAN, DIM, BOLD, MAG = "32", "31", "33", "36", "90", "1", "35"


def init(ascii_mode: bool = False) -> None:
    global COLOR, ASCII, BOX
    ASCII = ascii_mode
    is_tty = getattr(sys.stdout, "isatty", lambda: True)()
    COLOR = (not ascii_mode
             and not os.environ.get("NO_COLOR")
             and is_tty)
    if ASCII:
        BOX = dict(tl="+", tr="+", bl="+", br="+", h="-", v="|",
                   ml="+", mr="+", cross="+", bar="#", star="*", hollow="-")
    else:
        BOX = dict(tl="┌", tr="┐", bl="└", br="┘", h="─", v="│",
                   ml="├", mr="┤", cross="┼", bar="█", star="★", hollow="☆")


def c(text: str, code: str) -> str:
    if not COLOR:
        return text
    return f"\x1b[{code}m{text}\x1b[0m"


def good(text: str) -> str:
    return c(text, GREEN)


def bad(text: str) -> str:
    return c(text, RED)


def warn(text: str) -> str:
    return c(text, YEL)


def info(text: str) -> str:
    return c(text, CYAN)


def dim(text: str) -> str:
    return c(text, DIM)


def strong(text: str) -> str:
    return c(text, BOLD)
