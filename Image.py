""" import cv2 on Pycharm
PyCharm -> Settings -> Python Interpreter -> Gear symbol -> Show all -> folder tree -> +
select the folder where the opencv package is located (ctrl+click on cv2) -> done
"""
import threading
from typing import Optional

import cv2 as cv
import numpy as np
import pytesseract

from Colors import printc
from Files import delete, get_files_from_path, get_current_path
from Util import COMMON_CHARS, restrict_num

event_dict = {"i_event": 0, "next_i_event": 0, "i_display_images": 0, "arrays": [], "x": 0, "ocr": False, "exit_display": False}
red_isolation = (255, 130, 130)
green_isolation = (130, 255, 130)
blue_isolation = (130, 130, 255)

pytesseract.pytesseract.tesseract_cmd = r'B:\Programmes\Tesseract-OCR\tesseract.exe'

"""##### Image modifiers #####"""


def grayscale(image):
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def median_blur(image):
    return cv.medianBlur(image, 5)


def dilate(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv.dilate(image, kernel, iterations=1)


def erode(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv.erode(image, kernel, iterations=1)


def morphology_ex(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv.morphologyEx(image, cv.MORPH_OPEN, kernel)


def canny(image):
    return cv.Canny(image, 100, 200)


def match_template(image, template):
    return cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)


"""###########################"""


def create_with_color(shape: tuple[int, int, int], bgr: tuple[int, int, int] = (0, 0, 0)):
    image = np.zeros(shape, np.uint8)
    image[:] = bgr
    return image


def isolate_img(img, rgb_isolation, variation):
    # No hsv
    rgb_isolation_min = (0, 0, 0)
    rgb_isolation_max = list(
        map(lambda x: int(restrict_num(x + variation + event_dict["x"], 0, 255)), rgb_isolation))
    print(rgb_isolation_min)
    print(rgb_isolation_max)
    mask = cv.inRange(img, np.array(rgb_isolation_min), np.array(rgb_isolation_max))
    img = cv.bitwise_and(img, img, mask=mask)
    return img


def get_only_white(img, variation=50):
    rgb_isolation_min = (255 - variation, 255 - variation, 255 - variation)
    rgb_isolation_max = (255, 255, 255)
    mask = cv.inRange(img, np.array(rgb_isolation_min), np.array(rgb_isolation_max))
    return cv.bitwise_and(img, img, mask=mask)


def get_only_black(img, variation=100):
    """ return black color as white color """
    rgb_isolation_min = (0, 0, 0)
    rgb_isolation_max = (variation, variation, variation)
    mask = cv.inRange(img, np.array(rgb_isolation_min), np.array(rgb_isolation_max))
    img = create_with_color(img.shape, (255, 255, 255))
    return cv.bitwise_and(img, img, mask=mask)


def add(*args):
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


def ocr_image(img: np.ndarray,
              config: str = r"--oem 3 --psm 6",
              whitelist_ocr=COMMON_CHARS,
              blacklist_ocr="",
              whitelist_filter=COMMON_CHARS,
              blacklist_filter="",
              debug=True) -> tuple[str, np.array]:
    config += " -c tessedit_char_whitelist={} -c tessedit_char_blacklist={}".format(whitelist_ocr, blacklist_ocr)
    img_to_str = pytesseract.image_to_string(img, config=config)
    img_to_str = "".join([char for char in img_to_str if char in whitelist_filter and char not in blacklist_filter])
    if debug:
        printc(img_to_str, background_color="black")
    return img_to_str, img


def save(img: np.ndarray, dest="out.jpeg", quality=100):
    """ flags: https://docs.opencv.org/4.0.1/d4/da8/group__imgcodecs.html#ga292d81be8d76901bff7988d18d2b42ac"""
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    cv.imwrite(dest, img, [cv.IMWRITE_JPEG_QUALITY, quality])


def display_images(images: list[np.ndarray],
                   full_screen: bool = False,
                   ocr=False,
                   rgb_isolation: Optional[tuple[int, int, int]] = None,
                   variation: int = 0):
    global event_dict
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    def events(event):
        global event_dict
        print(event.key)
        space = " "
        if event.key not in ["q", "left", "right", "up", "down", space] + list(map(str, range(10))):
            return
        event_dict["i_event"] += 1
        event_dict["next_i_event"] = event_dict["i_event"]
        if event.key == 'q':
            plt.close('all')
            for i in range(len(images)):
                delete("temp%s.jpeg" % (i,))
            event_dict["exit_display"] = True
        elif event.key == "left":
            event_dict["i_display_images"] = (event_dict["i_display_images"] - 1) % len(images)
        elif event.key == "right":
            event_dict["i_display_images"] = (event_dict["i_display_images"] + 1) % len(images)
        elif event.key == "up":
            event_dict["x"] += 1
        elif event.key == "down":
            event_dict["x"] -= 1
        elif event.key == space:
            event_dict["ocr"] = not event_dict["ocr"]
        elif event.key in map(str, range(10)):
            event_dict["i_display_images"] = int(event.key) % len(images)

    def init_gui(plt) -> plt:
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
        return plt, ax, fig

    event_dict["ocr"] = ocr
    only_white = rgb_isolation == (255, 255, 255)
    only_black = rgb_isolation == (0, 0, 0)
    # TODO why after modifying an image i have to save the image to a temp file and get it to have a correct array
    good_arrays = []
    for i in range(len(images)):
        img = images[i]
        if only_white:
            img = get_only_white(img, variation)
        elif only_black:
            img = get_only_black(img, variation)
            rgb_isolation = (255, 255, 255)
        save(img, dest="temp%s.jpeg" % (i,))
        good_arrays.append(cv.imread("temp%s.jpeg" % (i,)))
        event_dict["arrays"].append(cv.imread("temp%s.jpeg" % (i,)))
    plt, ax, fig = init_gui(plt)
    plt.ion()
    plt.show()
    while not event_dict["exit_display"]:
        i = event_dict["i_display_images"]
        display_image = event_dict["arrays"][i]
        plt.imshow(display_image)
        plt.show()
        plt.pause(0.2)
        plt.cla()
        new_action = event_dict["i_event"] == event_dict["next_i_event"]
        if new_action:
            img = good_arrays[event_dict["i_display_images"]]
            if rgb_isolation is not None:
                img = isolate_img(img, rgb_isolation, variation)
            if event_dict["ocr"]:
                ocr_text, img = ocr_image(img)
            event_dict["arrays"][event_dict["i_display_images"]] = img
            event_dict["next_i_event"] += 1
    plt.close()
    event_dict = {"i_event": 0, "next_i_event": 0, "i_display_images": 0, "arrays": [], "x": 0, "ocr": False, "exit_display": False}


if __name__ == '__main__':
    # https://www.delftstack.com/howto/python/python-color-spectrums/
    images = get_files_from_path(get_current_path() + "\\images\\", recursive=True)
    images = list(map(lambda x: cv.imread(x), images))
    funs = [grayscale, median_blur, morphology_ex, erode, dilate, canny]
    outputs = [fun(images[0]) for fun in funs]
    display_images(images, rgb_isolation=(255, 255, 255))
    display_images(outputs)
    # display_images([imga, imgb, imgc, imgd], full_screen=False, ocr=False, rgb_isolation=(255, 255, 255), variation=0)
