""" import cv2 on Pycharm
PyCharm -> Settings -> Project -> Python Interpreter -> Gear symbol -> Show all -> folder tree -> +
select the folder where the opencv package is located (ctrl+click on cv2) -> done
https://www.delftstack.com/howto/python/python-color-spectrums/
"""
import threading
from typing import Optional

import cv2 as cv
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytesseract

from Colors import printc
from Files import delete, get_files_from_path, get_current_path
from Util import COMMON_CHARS, restrict_num

EVENT_DICT = {}
RED_ISOLATION = (255, 100, 100)
GREEN_ISOLATION = (100, 255, 100)
BLUE_ISOLATION = (100, 100, 255)

pytesseract.pytesseract.tesseract_cmd = r'B:\Programmes\Tesseract-OCR\tesseract.exe'


def create_with_color(shape: tuple[int, int, int], bgr: tuple[int, int, int] = (0, 0, 0)) -> np.array:
    image = np.zeros(shape, np.uint8)
    image[:] = bgr
    return image


"""##### Image modifiers #####"""


def grayscale(image: np.array) -> np.array:
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


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


MODIFIERS_FUNCTION = [grayscale, median_blur, morphology_ex, erode, dilate, canny]


def isolate_img(image: np.array, rgb_isolation: tuple[int, int, int], variation: int) -> np.array:
    # TODO transparent background
    # No hsv
    rgb_isolation_min = list(map(lambda x: int(restrict_num(x + variation + EVENT_DICT["y"], 0, 255)), (0, 0, 0)))
    rgb_isolation_max = list(map(lambda x: int(restrict_num(x + variation + EVENT_DICT["x"], 0, 255)), rgb_isolation))
    print("isolate_img")
    print(rgb_isolation_min)
    print(rgb_isolation_max)
    mask = cv.inRange(image, np.array(rgb_isolation_min), np.array(rgb_isolation_max))
    image = cv.bitwise_and(image, image, mask=mask)
    return image


def get_only_white(image: np.array, variation: int = 50) -> np.array:
    rgb_isolation_min = (255 - variation, 255 - variation, 255 - variation)
    rgb_isolation_max = (255, 255, 255)
    mask = cv.inRange(image, np.array(rgb_isolation_min), np.array(rgb_isolation_max))
    return cv.bitwise_and(image, image, mask=mask)


def get_only_black(image, variation: int = 100) -> np.array:
    """ return black color as white color """
    rgb_isolation_min = (0, 0, 0)
    rgb_isolation_max = (variation, variation, variation)
    mask = cv.inRange(image, np.array(rgb_isolation_min), np.array(rgb_isolation_max))
    image = create_with_color(image.shape, (255, 255, 255))
    return cv.bitwise_and(image, image, mask=mask)


def add(*args: list[np.array]) -> np.array:
    """
    >>> a = get_only_white(img)
    >>> b = get_only_black(img)
    >>> c = add(a, b)
    >>> display_images([img, a, b, c])
    """
    result = args[0]
    for img in args[1:]:
        result = cv.add(result, img)
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
                  "original_img": False, "exit_display": False}


reset_event_vars()


def events(event):
    global EVENT_DICT
    printc(event.key, background_color="blue")
    space = " "
    if event.key not in ["q", "left", "right", "up", "down", "enter", "+", "-", space] + list(map(str, range(10))):
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


def get_isolate_or_black_or_white(image: np.array, rgb_isolation: tuple[int, int, int], variation: int = -1) -> np.array:
    only_white = rgb_isolation == (255, 255, 255)
    only_black = rgb_isolation == (0, 0, 0)
    if only_white:
        image = get_only_white(image) if variation == -1 else get_only_white(image, variation)
    elif only_black:
        image = get_only_black(image) if variation == -1 else get_only_black(image, variation)
    else:
        image = isolate_img(image, rgb_isolation, 0 if variation == -1 else variation)
    return image


def fill_images_array(images: np.array, rgb_isolation: Optional[tuple[int, int, int]] = None, variation: int = -1) -> \
        list[np.array]:
    # TODO why with matplotlib i have to save images to a temp file and get it to have correct arrays
    arrays = []
    for i in range(len(images)):
        image = images[i]
        save(image, dest="temp.jpeg")
        image_correct = cv.imread("temp.jpeg")
        if rgb_isolation is not None:
            image_correct = get_isolate_or_black_or_white(image_correct, rgb_isolation, variation)
        arrays.append(image_correct)
        EVENT_DICT["arrays"].append(image_correct)
        # EVENT_DICT["arrays"].append(img)  # ?
    delete("temp.jpeg")
    return arrays


def display_images(images: list[np.ndarray],
                   full_screen: bool = False,
                   autorun: float = 0):
    import matplotlib.pyplot as plt

    fill_images_array(images)
    plt, ax, fig = init_image_viewer(plt, full_screen)
    while not EVENT_DICT["exit_display"]:
        i = EVENT_DICT["i_display_images"]
        display_image = EVENT_DICT["arrays"][i]
        plt.imshow(display_image)
        plt.show()
        if autorun != 0:
            plt.pause(autorun)
            EVENT_DICT["i_display_images"] = (EVENT_DICT["i_display_images"] + 1) % len(images)
        else:
            plt.pause(0.2)
            new_action = EVENT_DICT["i_event"] == EVENT_DICT["next_i_event"]
            if new_action:
                EVENT_DICT["next_i_event"] += 1
        plt.cla()
    reset_event_vars()
    plt.close()


def display_images_n_debug(images: list[np.ndarray],
                           full_screen: bool = False,
                           ocr=False,
                           rgb_isolation: Optional[tuple[int, int, int]] = None,
                           variation: int = -1) -> list[np.ndarray]:
    import matplotlib.pyplot as plt

    EVENT_DICT["ocr"] = ocr
    EVENT_DICT["arrays"] = fill_images_array(images, rgb_isolation, variation)
    if rgb_isolation == (0, 0, 0):
        rgb_isolation = (255, 255, 255)
    plt, ax, fig = init_image_viewer(plt, full_screen)
    while not EVENT_DICT["exit_display"]:
        i = EVENT_DICT["i_display_images"]
        if EVENT_DICT["original_img"]:
            display_image = images[i]
        else:
            display_image = EVENT_DICT["arrays"][i]
        new_action = EVENT_DICT["i_event"] == EVENT_DICT["next_i_event"]
        if new_action:
            if rgb_isolation is not None:
                display_image = isolate_img(display_image, rgb_isolation, 0 if variation == -1 else variation)
            if EVENT_DICT["ocr"]:
                ocr_text, display_image = ocr_image(display_image)
            EVENT_DICT["arrays"][EVENT_DICT["i_display_images"]] = display_image
            EVENT_DICT["next_i_event"] += 1
        plt.imshow(display_image)
        plt.show()
        plt.pause(0.2)
        plt.cla()
    plt.close()
    reset_event_vars()
    return EVENT_DICT["arrays"]


def save(img: np.ndarray, dest: str = "out.jpeg", quality: int = 100):
    """ flags: https://docs.opencv.org/4.0.1/d4/da8/group__imgcodecs.html#ga292d81be8d76901bff7988d18d2b42ac"""
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    cv.imwrite(dest, img, [cv.IMWRITE_JPEG_QUALITY, quality])


if __name__ == '__main__':
    images = get_files_from_path(get_current_path() + "\\images\\", recursive=True)
    images = list(map(lambda x: cv.imread(x), images))
    # outputs = [] + [fun(images[0]) for fun in MODIFIERS_FUNCTION]
    # display_images(images, rgb_isolation=(255, 255, 255))
    # display_images(outputs, autorun=0.2)
    outputs = display_images_n_debug(images, rgb_isolation=(255, 255, 255), ocr=True)
    # display_images(outputs)
