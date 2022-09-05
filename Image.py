""" import cv2 on Pycharm
PyCharm -> Settings -> Project -> Python Interpreter -> Gear symbol -> Show all -> folder tree -> +
select the folder where the opencv package is located (ctrl+click on cv2) -> done
https://www.delftstack.com/howto/python/python-color-spectrums/
https://pyimagesearch.com/2021/01/19/opencv-bitwise-and-or-xor-and-not/
"""
import _pickle
import copy
import pickle
import sys
import threading
import traceback
from typing import Optional, Callable

import cv2 as cv
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pyqrcode
import pytesseract
import pywhatkit
import win32con
import win32gui
import win32ui
from pyzbar.pyzbar import decode

from Colors import printc
from Files import delete
from Times import now, elapsed_seconds
from Util import COMMON_CHARS, restrict_num, string_encoded_to_bytes

# RGB config most of the time because matplotlib is RGB
EVENT_DICT = {}
RED_ISOLATION = (255, 100, 100)
GREEN_ISOLATION = (100, 255, 100)
BLUE_ISOLATION = (100, 100, 255)

pytesseract.pytesseract.tesseract_cmd = r'B:\Programmes\Tesseract-OCR\tesseract.exe'


def screenshot_fastest(x0: float, y0: float, x1: float, y1: float, dest="out.png"):
    w = x1 - x0
    h = y1 - y0
    hwnd = None
    w_dc = win32gui.GetWindowDC(hwnd)
    dc_obj = win32ui.CreateDCFromHandle(w_dc)
    c_dc = dc_obj.CreateCompatibleDC()
    data_bit_map = win32ui.CreateBitmap()
    data_bit_map.CreateCompatibleBitmap(dc_obj, w, h)
    c_dc.SelectObject(data_bit_map)
    c_dc.BitBlt((0, 0), (w, h), dc_obj, (x0, y0), win32con.SRCCOPY)
    data_bit_map.SaveBitmapFile(c_dc, dest)
    dc_obj.DeleteDC()
    c_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, w_dc)
    win32gui.DeleteObject(data_bit_map.GetHandle())


def create_with_color(shape: tuple[int, int, int], rgb: tuple[int, int, int] = (0, 0, 0)) -> np.array:
    image = np.zeros(shape, np.uint8)
    image[:] = rgb
    return image


"""##### Image modifiers #####"""


def grayscale(image: np.array) -> np.array:
    return cv.cvtColor(image, cv.COLOR_RGB2GRAY)


def median_blur(image: np.array) -> np.array:
    return cv.medianBlur(image, 5)


def dilate(image: np.array) -> np.array:
    kernel = np.ones((5, 5), np.uint8)
    return cv.dilate(image, kernel, iterations=1)


def erode(image: np.array) -> np.array:
    kernel = np.ones((5, 5), np.uint8)
    return cv.erode(image, kernel, iterations=1)


def morphology_ex(image: np.array) -> np.array:
    kernel = np.ones((5, 5), np.uint8)
    return cv.morphologyEx(image, cv.MORPH_OPEN, kernel)


def canny(image: np.array) -> np.array:
    return cv.Canny(image, 100, 200)


def match_template(image: np.array, template):
    return cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)


MODIFIERS_FUNCTION = [lambda x: x, grayscale, median_blur, morphology_ex, erode, dilate, canny]


def isolate_img(image: np.array, rgb_min: tuple, rgb_max: tuple) -> np.array:
    # TODO transparent background
    # No hsv
    mask = cv.inRange(image, np.array(rgb_min), np.array(rgb_max))
    return cv.bitwise_and(image, image, mask=mask)


def filtering_intensity(image: np.array,
                        rgb_min: tuple[int, int, int],
                        rgb_max: tuple[int, int, int],
                        set_color_in=None,
                        set_color_out=None):
    a, b, c = rgb_min
    d, e, f = rgb_max
    filter_in = np.where(
        ((a <= image[:, :, 0]) & (image[:, :, 0] <= d)) |
        ((b <= image[:, :, 1]) & (image[:, :, 1] <= e)) |
        ((c <= image[:, :, 2]) & (image[:, :, 2] <= f))
    )
    filter_out = np.where(
        ((a > image[:, :, 0]) | (image[:, :, 0] > d)) &
        ((b > image[:, :, 1]) | (image[:, :, 1] > e)) &
        ((c > image[:, :, 2]) | (image[:, :, 2] > f))
    )
    new_image = copy.copy(image)
    if set_color_in is not None:
        new_image[filter_in] = set_color_in
    if set_color_out is not None:
        new_image[filter_out] = set_color_out
    return new_image


def filtering_color(image: np.array,
                    rgb_min: tuple[int, int, int],
                    rgb_max: tuple[int, int, int],
                    set_color_in: Optional[tuple[int, int, int]] = None,
                    set_color_out: Optional[tuple[int, int, int]] = None):
    a, b, c = rgb_min
    d, e, f = rgb_max
    filter_in = np.where(
        ((a <= image[:, :, 0]) & (image[:, :, 0] <= d)) &
        ((b <= image[:, :, 1]) & (image[:, :, 1] <= e)) &
        ((c <= image[:, :, 2]) & (image[:, :, 2] <= f))
    )
    filter_out = np.where(
        ((a > image[:, :, 0]) | (image[:, :, 0] > d)) |
        ((b > image[:, :, 1]) | (image[:, :, 1] > e)) |
        ((c > image[:, :, 2]) | (image[:, :, 2] > f))
    )
    new_image = copy.copy(image)
    if set_color_in is not None:
        new_image[filter_in] = set_color_in
    if set_color_out is not None:
        new_image[filter_out] = set_color_out
    return new_image


def filter_pixels(image: np.array,
                  rgb_min: tuple[int, int, int],
                  rgb_max: tuple[int, int, int],
                  set_color: tuple[int, int, int] = (0, 0, 0)) -> np.array:
    """ All pixel that are in range are not changed, other are set to black """
    return filtering_intensity(image, rgb_min, rgb_max, set_color_out=set_color)


def create_mask(image: np.array, rgb_min: tuple[int, int, int], rgb_max: tuple[int, int, int]) -> np.array:
    """ All pixel that are in range are set to white, other are set to black """
    return filtering_intensity(image, rgb_min, rgb_max, set_color_in=(255, 255, 255), set_color_out=(0, 0, 0))


def get_only_white(image: np.array, variation: int = 25) -> np.array:
    rgb_isolation_min = (255 - variation, 255 - variation, 255 - variation)
    rgb_isolation_max = (255, 255, 255)
    return isolate_img(image, rgb_isolation_min, rgb_isolation_max)


def get_only_black(image: np.array, variation: int = 25) -> np.array:
    """ return black color as white color """
    rgb_isolation_min = (0, 0, 0)
    rgb_isolation_max = (variation, variation, variation)
    mask = cv.inRange(image, np.array(rgb_isolation_min), np.array(rgb_isolation_max))
    image = create_with_color(image.shape, (255, 255, 255))
    return cv.bitwise_and(image, image, mask=mask)


def concat_black_n_white(image: np.array, variation: int = 25) -> np.array:
    return add(get_only_white(image, variation), get_only_black(image, variation))


def get_only_colored(image: np.array, variation=25) -> np.array:
    return cv.subtract(image, concat_black_n_white(image, variation))


def add(*args: np.array) -> np.array:
    result = args[0]
    for image in args[1:]:
        result = cv.add(result, image)
    return result


def sub(*args: np.array) -> np.array:
    result = args[0]
    for image in args[1:]:
        result = cv.absdiff(result, image)
    return result


"""########## OCR ############"""


def ocr_image(img: np.ndarray,
              config: str = r"--oem 3 --psm 6",
              whitelist_ocr: str = COMMON_CHARS,
              blacklist_ocr: str = "",
              whitelist_filter: str = COMMON_CHARS,
              blacklist_filter: str = "",
              debug: bool = True) -> tuple[str, np.array]:
    # https://ai-facets.org/tesseract-ocr-best-practices/
    config += " -c tessedit_char_whitelist={} -c tessedit_char_blacklist={}".format(whitelist_ocr, blacklist_ocr)
    img_to_str = pytesseract.image_to_string(img, config=config)
    img_to_str = "".join([char for char in img_to_str if char in whitelist_filter and char not in blacklist_filter])
    if len(img_to_str) and img_to_str[-1] == "\n":
        img_to_str = img_to_str[:-1]
    if debug:
        printc(img_to_str, background_color="black")
    return img_to_str, img


"""##### Image viewer #####"""


def reset_event_vars():
    global EVENT_DICT
    EVENT_DICT = {"i_event": 0, "next_i_event": 0, "i_display_images": 0, "arrays": [], "x": 0, "y": 0, "ocr": False,
                  "original_img": False, "exit_display": False, "time": now()}


reset_event_vars()


def events(event):
    global EVENT_DICT
    printc(event.key, background_color="blue")
    space = " "
    if (event.key not in ["q", "left", "right", "up", "down", "enter", "+", "-", space] + list(map(str, range(10)))
            or elapsed_seconds(EVENT_DICT["time"]) < 0.1):
        return
    EVENT_DICT["i_event"] += 1
    EVENT_DICT["next_i_event"] = EVENT_DICT["i_event"]
    len_images = len(EVENT_DICT["arrays"])
    if event.key == 'q':
        plt.close('all')
        EVENT_DICT["exit_display"] = True
    elif event.key == "left":
        EVENT_DICT["i_display_images"] = (EVENT_DICT["i_display_images"] - 1) % len_images
    elif event.key == "right":
        EVENT_DICT["i_display_images"] = (EVENT_DICT["i_display_images"] + 1) % len_images
    elif event.key == "up":
        EVENT_DICT["x"] += 1
    elif event.key == "down":
        EVENT_DICT["x"] -= 1
    elif event.key == "+":
        EVENT_DICT["y"] += 1
    elif event.key == "-":
        EVENT_DICT["y"] -= 1
    elif event.key == "enter":
        EVENT_DICT["ocr"] = not EVENT_DICT["ocr"]
    elif event.key == space:
        EVENT_DICT["original_img"] = not EVENT_DICT["original_img"]
    elif event.key in map(str, range(10)):
        EVENT_DICT["i_display_images"] = int(event.key) % len_images
    EVENT_DICT["time"] = now()
    print(EVENT_DICT["i_display_images"], "ocr", EVENT_DICT["ocr"], "original", EVENT_DICT["original_img"], "\n")


def init_image_viewer(plt, full_screen: bool = False) -> matplotlib.pyplot:
    plt.rcParams['toolbar'] = 'None'
    plt.rcParams['figure.figsize'] = (16, 8)
    if threading.current_thread() == threading.main_thread():
        mpl.use('Qt5Agg')  # pip install PyQt5
    curve_color = "#000000"
    plt.rcParams['axes.facecolor'] = curve_color
    fig: plt.figure = plt.figure()
    fig.patch.set_facecolor(curve_color)
    ax = fig.add_axes([0, 0, 1, 1])
    fig.canvas.mpl_connect('key_press_event', events)
    if full_screen:
        fig.canvas.manager.full_screen_toggle()
    plt.ion()
    plt.show()
    return plt, ax, fig


def get_black_or_white_or_isolate(image: np.array,
                                  rgb_min: tuple[int, int, int],
                                  rgb_max: tuple[int, int, int], ) -> np.array:
    if rgb_min == (0, 0, 0):
        image = get_only_black(image)
    elif rgb_max == (255, 255, 255):
        image = get_only_white(image)
    else:
        image = isolate_img(image, rgb_min, rgb_max)
    return image


def fill_images_array(images: np.array,
                      rgb_min: Optional[tuple[int, int, int]] = None,
                      rgb_max: Optional[tuple[int, int, int]] = None) -> list[np.array]:
    arrays = []
    for i in range(len(images)):
        image = images[i]
        # save(image, dest="temp.jpeg")
        # image = cv.imread("temp.jpeg")
        if rgb_min is not None and rgb_max is not None:
            image = get_black_or_white_or_isolate(image, rgb_min, rgb_max)
        arrays.append(image)
        EVENT_DICT["arrays"].append(image)
    delete("temp.jpeg")
    return arrays


def display_images(images: list[np.ndarray] | np.ndarray,
                   full_screen: bool = False,
                   autorun: float = 0):
    import matplotlib.pyplot as plt

    if type(images) is not list:
        images = [images]
    fill_images_array(images)
    plt, ax, fig = init_image_viewer(plt, full_screen)
    while not EVENT_DICT["exit_display"]:
        i = EVENT_DICT["i_display_images"]
        display_image = EVENT_DICT["arrays"][i]
        plt.imshow(display_image)
        if autorun != 0:
            fig.canvas.start_event_loop(autorun)
            EVENT_DICT["i_display_images"] = (EVENT_DICT["i_display_images"] + 1) % len(images)
        else:
            fig.canvas.start_event_loop(0.2)
            new_action = EVENT_DICT["i_event"] == EVENT_DICT["next_i_event"]
            if new_action:
                EVENT_DICT["next_i_event"] += 1
        plt.cla()
    reset_event_vars()
    plt.close()


def display_images_n_debug(images: list[np.ndarray] | np.ndarray,
                           full_screen: bool = False,
                           ocr: bool = False,
                           rgb_min: Optional[tuple[int, int, int]] = None,
                           rgb_max: Optional[tuple[int, int, int]] | int = None,
                           variation: Optional[int] = None) -> list[np.ndarray]:
    import matplotlib.pyplot as plt

    if type(images) is not list:
        images = [images]
    assert (rgb_min is None) is (rgb_max is None) or ((rgb_min or rgb_max) and variation)
    EVENT_DICT["ocr"] = ocr
    fill_images_array(images, rgb_min, rgb_max)
    plt, ax, fig = init_image_viewer(plt, full_screen)
    while not EVENT_DICT["exit_display"]:
        i = EVENT_DICT["i_display_images"]
        new_action = EVENT_DICT["i_event"] == EVENT_DICT["next_i_event"]
        if new_action:
            display_image = images[i]
            if rgb_min is not None and (rgb_max is not None or variation is not None):
                if variation:
                    rgb_isolation_min = tuple(
                        map(lambda x: int(restrict_num(x - variation + EVENT_DICT["y"], 0, 255)), rgb_min))
                    rgb_isolation_max = tuple(
                        map(lambda x: int(restrict_num(x + variation + EVENT_DICT["x"], 0, 255)), rgb_min))
                else:
                    rgb_isolation_min = tuple(map(lambda x: int(restrict_num(x + EVENT_DICT["y"], 0, 255)), rgb_min))
                    rgb_isolation_max = tuple(map(lambda x: int(restrict_num(x + EVENT_DICT["x"], 0, 255)), rgb_max))
                print(rgb_isolation_min)
                print(rgb_isolation_max)
                only_black = rgb_isolation_min == (0, 0, 0)
                only_white = rgb_isolation_max == (255, 255, 255)
                if not only_black and not only_white and rgb_isolation_min and rgb_isolation_max:
                    display_image = isolate_img(display_image, rgb_isolation_min, rgb_isolation_max)
                if only_black and only_white:
                    display_image = concat_black_n_white(display_image)
                elif only_black:
                    display_image = get_only_black(display_image)
                elif only_white:
                    display_image = get_only_white(display_image)
            if EVENT_DICT["ocr"]:
                ocr_text, display_image = ocr_image(display_image)
            EVENT_DICT["arrays"][i] = display_image
            EVENT_DICT["next_i_event"] += 1
        if EVENT_DICT["original_img"]:
            display_image = images[i]
        else:
            display_image = EVENT_DICT["arrays"][i]
        plt.imshow(display_image)
        fig.canvas.start_event_loop(0.2)
        plt.cla()
    plt.close()

    images = EVENT_DICT["arrays"]
    reset_event_vars()
    return images


def image_modifier(image,
                   functions: list[Callable[[np.array], np.array]] = None,
                   rgb_isolation_min: Optional[tuple[int, int, int]] = None,
                   rgb_isolation_max: Optional[tuple[int, int, int]] = None,
                   variation: Optional[int] = None,
                   rgb_min: tuple[int, int, int] = (0, 0, 0),
                   rgb_max: tuple[int, int, int] = (255, 255, 255)) -> list[np.ndarray]:
    if functions is not None:
        for function in functions:
            image = function(image)
    if rgb_isolation_min is not None:
        if variation is not None:
            rgb_isolation_max = rgb_isolation_min
            rgb_isolation_min = tuple(map(lambda x: int(restrict_num(x - variation, 0, 255)), rgb_isolation_min))
            rgb_isolation_max = tuple(map(lambda x: int(restrict_num(x + variation, 0, 255)), rgb_isolation_max))
        image = get_black_or_white_or_isolate(image, rgb_isolation_min, rgb_isolation_max)
    image = filter_pixels(image, rgb_min, rgb_max)
    return image


def save(img: np.ndarray, dest: str = "out.jpeg", quality: int = 100):
    """ flags: https://docs.opencv.org/4.0.1/d4/da8/group__imgcodecs.html#ga292d81be8d76901bff7988d18d2b42ac"""
    cv.imwrite(dest, img, [cv.IMWRITE_JPEG_QUALITY, quality])


def image_to_ascii_art(file_name: str, dest: str = "out"):
    """ Don't put add .txt extension on the dest name"""
    pywhatkit.image_to_ascii_art(file_name, dest)


def create_qrcode(data: str | object, dest="out", scale=5) -> bool:
    if type(data) is not str:
        data = pickle.dumps(data)
    try:
        qrcode = pyqrcode.create(data, encoding="unicode_escape")  # utf-8 isn't working
    except ValueError:
        print(traceback.format_exc(), file=sys.stderr)
        printc("The data is too big to be stored through a QRCode", background_color="red")
        return False
    qrcode.png("{}.png".format(dest), scale=scale)
    qrcode.svg("{}.svg".format(dest), scale=scale)
    return True


def decode_qrcode(file_name="out.png"):
    # TODO svg to png
    assert ".svg" not in file_name, "convert svg to another format"
    # import cairosvg
    # cairosvg.svg2pdf(url='image.svg', write_to='image.pdf')
    qrcode = cv.imread(file_name)
    qrdecode = decode(qrcode)[0]  # utf-8 encoding, cannot change
    text_utf8 = qrdecode.data
    str_encoded_raw = text_utf8.decode(encoding='utf-8')
    text_unicode_escape = string_encoded_to_bytes(str_encoded_raw)
    try:
        value = pickle.loads(text_unicode_escape, encoding='unicode_escape')
    except _pickle.UnpicklingError:
        value = str_encoded_raw
    return value


if __name__ == '__main__':
    create_qrcode({"ee": 56, (1, 2, 3): "486"})
    print(decode_qrcode())

    # image_files = get_files_from_path(get_current_path() + "\\images\\", recursive=True)
    image_files = ["images/spectrum.jpeg"]
    images = list(map(lambda x: cv.cvtColor(cv.imread(x), cv.COLOR_BGR2RGB), image_files))

    # images_modified = [fun(image) for image in images for fun in MODIFIERS_FUNCTION]
    # display_images_n_debug(images_modified, ocr=True)

    image = images[0]
    # by color
    white_filter = get_only_white(image)
    yellow_filter = image_modifier(image, rgb_isolation_min=(0xFE, 0xC2, 0x00), variation=20)
    result = add(white_filter, yellow_filter)
    display_images(result)
    ocr_image(result)

    # # by intensity
    high_colors = filter_pixels(image, rgb_min=(240, 240, 240), rgb_max=(255, 255, 255))
    display_images(high_colors)
    ocr_image(high_colors)

    colored_filter = get_only_colored(image)
    display_images([image, colored_filter, sub(image, colored_filter)])
