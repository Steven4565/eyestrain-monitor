from typing import Any
import customtkinter

__theme = customtkinter.ThemeManager.theme
__single_color = customtkinter.ThemeManager.single_color
__appearance_tracker = customtkinter.AppearanceModeTracker


def toHex(frame: Any, str: str) -> str:
    '#%02x%02x%02x' % tuple((c//256 for c in frame.winfo_rgb(str)))


text: str
window_bg: str


def __update_colors():
    global text
    text = __single_color(__theme.get("color").get(
        "text"), __appearance_tracker.appearance_mode)
    global window_bg
    window_bg = __single_color(__theme.get("color").get(
        "window_bg_color"), __appearance_tracker.appearance_mode)


__update_colors()

__appearance_tracker.add(__update_colors)
