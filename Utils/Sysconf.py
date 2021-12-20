from screeninfo import get_monitors, Monitor

from Classes import Coord


def monitor_1080p(x, y):
    return Monitor(
        x=x,
        y=y,
        width=1920,
        height=1080,
        name="hide",
        is_primary=False,
    )


def screen_rect(x):
    return monitor_1080p((start_offset + x) / ratio, x / ratio)


MONITORS = get_monitors()
SCREENS = dict(zip(range(1, len(MONITORS) + 1), MONITORS))
FULL_SIZE = [min((monitor.x for monitor in MONITORS)),
             min((monitor.y for monitor in MONITORS)),
             max((monitor.x + monitor.width for monitor in MONITORS)),
             max((monitor.y + monitor.height for monitor in MONITORS))]
is_4k = False
for monitor in MONITORS:
    if not monitor.is_primary:
        continue
    is_4k = monitor.width == 3840 and monitor.height == 2160
ratio = 1
if is_4k:
    ratio = 1.5
start_offset = -11
SCREENS["hide"] = monitor_1080p((start_offset + FULL_SIZE[2] - 1920) / ratio, (FULL_SIZE[3] + 100) / ratio)
SCREENS["semi_hide_move"] = monitor_1080p((start_offset + FULL_SIZE[2] - 1920) / ratio, (FULL_SIZE[3] - 300) / ratio)
SCREENS["semi_hide"] = monitor_1080p((start_offset + FULL_SIZE[2] - 1920) / ratio, (FULL_SIZE[3] - 100) / ratio)
# print(MONITORS)
# print(FULL_SIZE)
# print(SCREENS)
