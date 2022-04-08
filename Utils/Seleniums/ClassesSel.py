import inspect
import os
import sys
import traceback
from time import sleep
from typing import Callable, Optional, Iterable

from msedge.selenium_tools import Edge, EdgeOptions
from msedge.selenium_tools.webdriver import WebDriver
from selenium.common.exceptions import SessionNotCreatedException, InvalidSessionIdException, TimeoutException, \
    WebDriverException, InvalidArgumentException, NoSuchWindowException, StaleElementReferenceException, \
    MoveTargetOutOfBoundsException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from urllib3.exceptions import NewConnectionError, MaxRetryError

import Alert
import Classes
from Colors import printc
from Enum import FIRST
from Introspection import current_lines
from Seleniums.Selenium import profile_name, check_find_fun, get_element_text, get_element_class
from Sysconf import screen_rect, SCREENS
from Times import now, elapsed_seconds
from Util import is_iter

last_browser_set = now()


class Browser:
    # noinspection PyTypeChecker
    def __init__(self, point, profile=None, headless=False):
        # self.point: Coord = point
        self.point = point
        self.profile: str = profile
        self.headless: bool = headless
        self.working_window_num: int = 0
        self.current_window_num: int = 0
        self.windows_url: list[str] = [""]
        self.driver: WebDriver = None
        self.name: Optional[str] = None
        self.set_browser(profile)

    def __str__(self):
        return "{} {} {} {}".format(self.name, self.windows_url, self.point, self.profile)

    def __len__(self):
        try:
            return len(self.driver.window_handles)
        except WebDriverException:
            # selenium.common.exceptions.WebDriverException: Message: chrome not reachable
            sleep(1)
            try:
                return len(self.driver.window_handles)
            except WebDriverException:
                return 0

    def print(self, texts: str | Iterable, tab=True):
        """ Prend cerrtaines ms, a eviter si on veut optimiser la vitesse"""

        def aux():
            # print(frameinfo(1))
            # print(frameinfo(2))
            # print(frameinfo(3))
            # print(frameinfo(4))
            # print(frameinfo(5))
            print("{}{} {}\t\t\t{} {}".format(
                "\t" if tab else "",
                self.name,
                " ¤ ".join(map(str, texts)) if is_iter(texts) and type(texts) is not str else texts,
                self,
                current_lines(start_depth=4)))

        # run(aux)
        aux()

    def printc(self, texts: str | Iterable, color="green", background_color=None, attributes: Optional[list] = None,
               tab=True):
        printc("{}{} {}\t\t\t{} {}".format(
            "\t" if tab else "",
            self.name,
            " ¤ ".join(map(str, texts)) if is_iter(texts) and type(texts) is not str else texts,
            self,
            current_lines(start_depth=3)),
            color=color,
            background_color=background_color,
            attributes=attributes)

    def set_browser(self, profile=None):
        global last_browser_set
        # Uniquement pour Edge
        """ Download drivers
            # https://pypi.org/project/selenium/
            # https://developer.microsoft.com/fr-fr/microsoft-edge/tools/webdriver/
            # https://sites.google.com/a/chromium.org/chromebrowser/downloads
            # https://github.com/operasoftware/operachromiumdriver/releases
        """
        try:
            self.working_window_num = 0
            self.current_window_num = 0
            self.driver = None
            self.windows_url: list[str] = [""]
            if profile is not None:
                self.profile = profile
            elif profile is None and self.profile is not None:
                pass
            self.name = None if self.profile is None else profile_name(self.profile)
            options = EdgeOptions()
            options.use_chromium = True
            if self.headless:
                options.add_argument("headless")
            if self.profile is not None:
                options.add_argument(self.profile)
            # req_proxy = RequestProxy()  # you may get different number of proxy when  you run this at each time
            # proxies = req_proxy.get_proxy_list()  # this will create proxy list
            # PROXY = proxies[0].get_address()
            # print(proxies)
            # webdriver.DesiredCapabilities.EDGE['proxy'] = {
            #     "httpProxy": PROXY,
            #     "ftpProxy": PROXY,
            #     "sslProxy": PROXY,
            #     "proxyType": "MANUAL",
            # }
            # print(
            #     r"{}{}..{}Drivers{}msedgedriver.exe"
            #         .format(inspect.currentframe().f_code.co_filename, os.path.sep, os.path.sep, os.path.sep))
            while elapsed_seconds(last_browser_set) < 0.1:
                sleep(0.1)
            last_browser_set = now()
            driver = Edge(
                options=options,
                executable_path=r"{}{}..{}Drivers{}msedgedriver.exe"
                    .format(inspect.currentframe().f_code.co_filename, os.path.sep, os.path.sep, os.path.sep))
            driver.set_window_position(self.point.x, self.point.y)
            driver.set_window_size(1920, 1080)
            self.driver = driver
            self.print("set_browser", False)
        except SessionNotCreatedException:
            while True:
                Alert.say("Have to download new browser driver version")
                sleep(3)
        except InvalidArgumentException:
            raise InvalidSessionIdException("profile is already open")

    def update_windows_url(self):
        try:
            url = self.driver.current_url
        except NoSuchWindowException:
            url = ""
        except MaxRetryError:
            url = ""
        self.set_windows_url(url, self.get_current_window_num() + 1)
        return url

    def current_url(self):
        try:
            url = self.update_windows_url()
            # print(14)
            # num = self.get_current_window_num()
        except NoSuchWindowException:
            url = ""
            self.decr_current_window_num()
        # except MaxRetryError:
        #     print(142)
        #     url = ""
        #     num = 0
        # print(143)
        # self.set_windows_url(url, num + 1)
        return url

    def decr_current_window_num(self):
        del self.windows_url[self.current_window_num]
        self.current_window_num -= 1
        self.updateinfos_current_page()

    def wait_new_created_window(self, old_count=None):
        if old_count is None:
            old_count = len(self)
        start = now()
        while len(self) <= old_count:
            sleep(0.1)
            if elapsed_seconds(start) >= 5:
                return False
        return True

    def updateinfos_current_page(self):
        # try:
        self.driver.switch_to.window(self.driver.window_handles[self.get_current_window_num()])
        self.update_windows_url()
        # except IndexError:
        #     self.decr_current_window_num()
        #     return self.updateinfos_current_page()

    def goto(self, window_num, update_working=True) -> bool:
        if window_num >= len(self.driver.window_handles):
            return False
        try:
            self.current_window_num = window_num
            self.driver.switch_to.window(self.driver.window_handles[window_num])
            self.update_windows_url()
        except WebDriverException:
            printc("goto WebDriverException", color="black", background_color="red")
            # selenium.common.exceptions.WebDriverException: Message: unknown error: cannot activate web view
            return False
        except IndexError:
            printc("goto IndexError", color="black", background_color="red")
            # selenium.common.exceptions.WebDriverException: Message: unknown error: cannot activate web view
            return False
        if update_working:
            self.working_window_num = window_num
        return True

    def goto_main(self):
        return self.goto(FIRST)

    def goto_last(self):
        return self.goto(len(self) - 1)

    def goto_work(self):
        """ Selon le browser """
        return self.goto(self.working_window_num)

    def goto_next(self):
        return self.goto((self.get_current_index_window() + 1) % len(browser))

    # ne peut pas faire cette methode car après un clique qui change de page, le driver n'est pas actualisé est l'ancienne page reste celle active
    # def goto_current_active_page(self):
    def goto_current_working_page(self):
        """ Selon le driver """
        return self.goto(self.get_current_index_window())

    def get_current_active_window(self) -> str:
        return self.driver.current_window_handle

    def get_current_index_window(self) -> int:
        return self.driver.window_handles.index(self.get_current_active_window())

    def set_windows_url(self, url, window_num):
        for i in range(window_num):
            if i >= len(self):
                self.new_tab()
            if i >= len(self.windows_url):
                self.windows_url.append("")
        self.windows_url[window_num - 1] = url

    def new_page(self, url, window_num=None, tries=0):
        try:
            if tries >= 5:
                return False
            if window_num is None:
                window_num = self.get_current_window_num()
            self.print(("new_page", url, window_num, tries), False)
            self.goto(window_num)
            self.driver.get(url)
            print("\t", "loaded new_page", self)
            self.update_windows_url()
        except InvalidSessionIdException as err:
            print("\terror new_page InvalidSessionIdException", str(err))
            Alert.say("error new_page InvalidSessionIdException")
            print(traceback.format_exc(), file=sys.stderr)
            return self.new_page(url, window_num, tries + 1)
        except TimeoutException as err:
            print("\terror new_page TimeoutException", str(err))
            Alert.say("error new_page TimeoutException")
            print(traceback.format_exc(), file=sys.stderr)
            return self.new_page(url, window_num, tries + 1)
        except WebDriverException or MaxRetryError or ConnectionRefusedError or NewConnectionError as err:
            print(
                "\terror new_page WebDriverException MaxRetryError ConnectionRefusedError NewConnectionError",
                str(err))
            Alert.say("critical error new_page")
            print(traceback.format_exc(), file=sys.stderr)
            self.relaunch()
            return self.new_page(url, window_num, tries + 1)

    def new_tab(self):
        self.updateinfos_current_page()
        self.driver.execute_script("window.open('');")
        self.set_windows_url("", self.get_current_window_num() + 1)

    def new_tab_and_go(self):
        self.goto_last()
        self.new_tab()
        self.goto_last()

    def new_url_tab(self, url):
        self.new_tab_and_go()
        self.new_page(url)

    def close_current_and_go_main(self):
        self.windows_url[self.get_current_window_num()] = ""
        self.close()
        self.goto_main()

    def refresh(self):
        try:
            self.driver.refresh()
        except NoSuchWindowException:
            "selenium.common.exceptions.NoSuchWindowException: Message: no such window: target window already closed"

    def relaunch(self):
        self.quit()
        self.printc("relaunch|" + str(self.profile) + "|", color="red")
        self.set_browser()

    def assert_url(self, wanted_url):
        try:
            if wanted_url not in self.current_url():
                self.print(("url_is_not_good", wanted_url, self.current_url()))
                # Alert.say("url is not good")
                self.new_page(wanted_url, self.get_current_window_num())
                return False
            return True
        except NoSuchWindowException:
            #     """NoSuchWindowException: Si la fenetre n'existe plus"""
            #     return None
            self.goto_work()
            return None

    def get_current_window_num(self):
        try:
            return self.driver.window_handles.index(self.driver.current_window_handle)
        except NoSuchWindowException:
            return self.current_window_num

    def get_current_url(self):
        return self.driver.current_url

    def close(self):
        # assert self.get_current_window_num() != 0
        self.decr_current_window_num()
        self.driver.close()
        self.goto(self.current_window_num)

    def quit(self):
        self.windows_url = None
        self.driver.quit()
        self.driver = None

    def get_width(self) -> Optional[float]:
        try:
            return self.driver.get_window_size()["width"]
        except WebDriverException:
            return None

    def get_element(self,
                    selectors: str | list[str],
                    find_element_fun: Callable[[WebDriver], str] = None,
                    debug=False,
                    all_windows=False) \
            -> None | WebElement | list[WebElement]:
        if debug is None:
            self.print(("get_element", selectors), False)
        if find_element_fun is None:
            find_element_fun = self.driver.find_element_by_xpath
        find_element_fun_name = find_element_fun.__name__
        is_elements = "elements" in find_element_fun_name
        if not is_elements:
            find_element_fun = check_find_fun(self.driver, find_element_fun_name)
        for i in range(len(self)):
            if i != 0:
                self.goto_next()
            try:
                if type(selectors) is str:
                    selectors = [selectors]
                for selector in selectors:
                    elements: list[WebElement] = find_element_fun(selector)
                    if is_elements:
                        return elements
                    elif type(elements) == list and len(elements) > 0:
                        return elements[0]
                if all_windows:
                    continue
                return None
            except NoSuchWindowException or WebDriverException as err:
                # selenium.common.exceptions.NoSuchWindowException: Message: no such window: target window already closed
                # self.print("win dont exist")
                # sleep(1)
                if all_windows:
                    continue
                return None
            # except Exception or UnboundLocalError or AttributeError or NoSuchElementException or \
            #        StaleElementReferenceException or ElementClickInterceptedException:
            #     print(traceback.format_exc(), file=sys.stderr)
            #     Alert.say("\tget_element None")
            #     sleep(1)
            #     return self.get_element(url, selector, find_element_fun, debug)

    def get_class(self, selector: str, find_element_fun: Callable[[WebDriver], str] = None, debug: bool = False) \
            -> Optional[WebElement]:
        if debug is None:
            self.print(("get_class", selector), False)
        return get_element_class(self.get_element(selector, find_element_fun=find_element_fun))

    def get_all_tag_that_contains(self, web_element, predicats_on_text: list[Callable],
                                  tag="div", doublon=False, alone=False) -> dict[str, WebElement] | None:
        print("get_all_tag_that_contains")
        if web_element is None:
            return None
        elements = self.get_element(tag, web_element.find_elements_by_tag_name)
        if elements is None:
            return None
        element_dict = {}
        for element in elements:
            element_text = get_element_text(element)
            if element_text is None:
                return None
            print("\tget_all_tag_that_contains_element_text<|" + str(element_text) + "|>")
            for predicat in predicats_on_text:
                if predicat(element_text):
                    if alone:
                        element_dict[element_text] = element
                        return element_dict
                    elif not doublon:
                        element_dict[element_text] = element
                    else:
                        if element_text not in element_dict:
                            element_dict[element_text] = []
                        element_dict[element_text].append(element)
        print("\t\n...\n".join(element_dict))
        print(len(element_dict), element_dict)
        return element_dict

    def wait_element(self,
                     url,
                     selectors: str | list[str],
                     find_element_fun: Callable[[WebDriver], str] = None,
                     appear=True,
                     refresh: int = None,
                     leave: int = 60,
                     debug=False) -> WebElement | bool:
        """ Attend qu'un ou plusieurs element apparaissent ou disparaissent"""
        self.print(("wait_element", url, selectors, appear, refresh, leave), False)
        self.assert_url(url)
        start_refresh = now()
        start_leave = now()
        # if appear:
        #     # On attend que l'element apparaisse
        #     element = self.get_element(selector, find_element_fun)
        #     condition_satisfy = element is not None
        # else:
        #     # On attend que l'element disparaisse
        #     condition_satisfy = self.get_element(selector, find_element_fun) is None
        condition_satisfy = False
        while not condition_satisfy:
            self.assert_url(url)
            if appear:
                element = self.get_element(selectors, find_element_fun)
                condition_satisfy = element is not None
                if condition_satisfy:
                    return element
            elif not appear:
                condition_satisfy = self.get_element(selectors, find_element_fun) is None
                if condition_satisfy:
                    return True
            if debug:
                self.print((selectors, find_element_fun, "url =", url))
            if refresh is not None and (now() - start_refresh).total_seconds() >= refresh:
                if url is not None and url != "":
                    self.new_page(url)
                else:
                    self.refresh()
                sleep(1)
                start_refresh = now()
            if debug:
                self.print(
                    ("r", refresh, (now() - start_refresh).total_seconds(),
                     "l", leave, (now() - start_leave).total_seconds(), "url =", url))
            if leave is not None and (now() - start_leave).total_seconds() >= leave:
                return False

    def big_wait_element(self,
                         url: str,
                         selector: str,
                         find_element_fun: Callable[[WebDriver], str] = None,
                         text: str = None,
                         class_text: str = None,
                         refresh: int = None,
                         leave: int = 60,
                         debug=False) -> WebElement | bool:
        """ Attend qu'un element apparaisse avec plusieurs critere restrictif"""
        self.print(("big_wait_element", url, selector, text, class_text, refresh, leave), False)
        self.assert_url(url)
        if find_element_fun is None:
            find_element_fun = self.driver.find_element_by_xpath
        if "elements" in find_element_fun.__name__:
            self.print("wait_element_find_element_fun_is_not_a_good_type")
            raise ValueError("wait_element_find_element_fun_is_not_a_good_type")
        start_refresh = now()
        start_leave = now()
        while leave is None or elapsed_seconds(start_leave) < leave:
            if refresh is not None and elapsed_seconds(start_refresh) < refresh:
                self.refresh()
                start_refresh = now()
            element = self.get_element(selector, find_element_fun)
            if element is not None:
                satisfy_text, satisfy_class = True, True
                if text is not None:
                    element_text = get_element_text(element, debug)
                    if element_text is None or text not in element_text:
                        satisfy_text = False
                if class_text is not None:
                    element_class = get_element_class(element, debug)
                    if element_class is None or class_text not in element_class:
                        satisfy_class = False
                if satisfy_text and satisfy_class:
                    return element
        return False

    def clicking_big_wait_element(self,
                                  url: str,
                                  selector: str,
                                  find_element_fun: Callable[[WebDriver], str] = None,
                                  text: str = None,
                                  class_text: str = None,
                                  element_to_click: WebElement = None,
                                  refresh: int = None,
                                  leave: int = 60,
                                  sleep_click: int = 1,
                                  debug=False) -> WebElement | bool:
        """ Attend qu'un element apparaisse avec plusieurs critere restrictif"""
        self.print(("clicking_big_wait_element", url, selector, text, class_text, sleep_click, refresh, leave), False)
        self.assert_url(url)
        if find_element_fun is None:
            find_element_fun = self.driver.find_element_by_xpath
        if "elements" in find_element_fun.__name__:
            self.print("wait_element_find_element_fun_is_not_a_good_type")
            raise ValueError("wait_element_find_element_fun_is_not_a_good_type")
        start_refresh = now()
        start_leave = now()
        last_click = now()
        while leave is None or elapsed_seconds(start_leave) < leave:
            if refresh is not None and elapsed_seconds(start_refresh) < refresh:
                self.refresh()
                start_refresh = now()
            element = self.get_element(selector, find_element_fun)
            if element is not None:
                if elapsed_seconds(last_click) >= sleep_click:
                    if element_to_click is None:
                        self.element_click(element)
                    else:
                        self.element_click(element_to_click)
                    last_click = now()
                satisfy_text, satisfy_class = True, True
                if text is not None:
                    element_text = get_element_text(element, debug)
                    if element_text is None or text not in element_text:
                        satisfy_text = False
                if class_text is not None:
                    element_class = get_element_class(element, debug)
                    if element_class is None or class_text not in element_class:
                        satisfy_class = False
                if satisfy_text and satisfy_class:
                    return element
        return False

    def get_text(self, url, selector: str, find_element_fun=None, refresh=None, leave=None, debug=False) \
            -> Optional[str]:
        """ Retourne le texte d'un element """
        if debug is None:
            self.print(("get_text", selector, refresh, leave), False)
        self.assert_url(url)
        if find_element_fun is None:
            find_element_fun = self.driver.find_element_by_xpath
        if "elements" in find_element_fun.__name__:
            self.print("wait_element_find_element_fun_is_not_a_good_type")
            raise ValueError("wait_element_find_element_fun_is_not_a_good_type")
        if "elements" in find_element_fun.__name__:
            self.print("wait_element_find_element_fun_is_not_a_good_type")
            raise ValueError("wait_element_find_element_fun_is_not_a_good_type")
        try:
            if leave is not None:
                if not self.wait_element(url, selector, find_element_fun, leave=leave, debug=debug):
                    if debug:
                        self.print("get_text_2 None")
                    return None
            elif refresh is not None:
                self.wait_element(url, selector, find_element_fun, refresh=refresh, debug=debug)
            element = self.get_element(selector, find_element_fun)
            if element is None:
                return None
            return get_element_text(element, debug)
        except StaleElementReferenceException:
            return None

    def wait_text(self, url: str, selectors: Optional[str] | Optional[list[str]] = None,
                  leave=60, refresh=22, min_txt_len=1, debug=True, find_element_fun=None) -> Optional[str]:
        """ Retourne le texte d'un premier element trouvé"""
        self.print(("wait_text", leave, refresh, min_txt_len))
        self.assert_url(url)
        start, start_refresh = now(), now()
        while elapsed_seconds(start) < leave:
            if refresh is not None and elapsed_seconds(start_refresh) >= refresh:
                if url is not None:
                    self.new_page(url)
                else:
                    browser.refresh()
                start_refresh = now()
            if is_iter(selectors):
                for selector in selectors:
                    text = self.get_text(url, selector, leave=1, debug=debug, find_element_fun=find_element_fun)
                    if text is not None and len(text) >= min_txt_len:
                        return text
            else:
                text = self.get_text(url, selectors, leave=1, debug=debug, find_element_fun=find_element_fun)
                if text is not None and len(text) >= min_txt_len:
                    return text
        return None

    def element_click(self, element: WebElement, actionchain=False, debug=False, leave=15) -> bool:
        self.print(("element_click", element), False)
        if element is None:
            if debug:
                self.print("element_click_element_is_None")
            return False
        try:
            if debug:
                self.print(("click_check_if_is_enable0", element.is_enabled()))
            start = now()
            while not element.is_enabled():
                if debug:
                    self.print(("click_check_if_is_enable1", element.is_enabled()))
                if elapsed_seconds(start) <= leave:
                    return False
            if debug:
                self.print(("clickA", element.is_enabled()))
            if actionchain:
                ActionChains(self.driver).click(element).perform()
            else:
                element.click()  # 5x plus rapide que ActionChains(self.driver).click(element).perform()
            return True
        except AttributeError:
            if debug:
                self.print("error_element_click")
                self.print(("click_check_if_is_enable2", element.is_enabled()))
            start = now()
            while not element.is_enabled():
                if debug:
                    self.print(("click_check_if_is_enable3", element.is_enabled()))
                if elapsed_seconds(start) <= leave:
                    return False
            if actionchain:
                element.click()
            else:
                ActionChains(self.driver).click(element).perform()
            if debug:
                self.print(("clickB", element.text))
            return True
        except StaleElementReferenceException:
            """N'existe plus"""
            return False
        except MoveTargetOutOfBoundsException:
            """N'est plus dans le champs cliquable"""
            return False
        except ElementNotInteractableException:
            """N'est plus dans le champs cliquable"""
            return False
        except ElementClickInterceptedException:
            """selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: 
            Element <img src="https://mypinata.cloud/ipfs/QmVy4xphMjDCYGmzQR6FhU8E6gHEaMpKbzf39wKFyqNBVV" alt="1" 
            class="carousel__img--item"> is not clickable at point (653, 377). Other element would receive the click"""
            return False

    def get_element_n_click(self, selector, find_element_fun=None) -> bool:
        element = self.get_element(selector, find_element_fun)
        return self.element_click(element)

    def wait_element_n_click(self, url, selector, find_element_fun=None, refresh=None) -> bool:
        element = self.wait_element(url, selector, find_element_fun, refresh=refresh)
        if element is bool:
            return False
        return self.element_click(element)

    def click_n_wait_new_created_window(self, element: WebElement) -> bool:
        old_count_window = len(self)
        self.element_click(element)
        return self.wait_new_created_window(old_count_window)

    def element_send(self, element: WebElement, *keys):
        self.print(("element_send", keys), False)
        if element is None:
            self.print("element_send_is_None")
            return
        try:
            keys = list(map(str, keys))
            actions = ActionChains(element)
            for key in keys:
                actions.send_keys(key)
            actions.perform()
        except AttributeError:
            try:
                ActionChains(element).send_keys_to_element(keys)
            except AttributeError:
                try:
                    # sleep(0.1)
                    for key in keys:
                        element.send_keys(key)
                    # element.send_keys(keys)
                except AttributeError as err:
                    print("\terror element_send", err)
                    # sleep(0.5)
                    self.element_send(element, keys)
            except StaleElementReferenceException:
                """N'existe plus"""

    def clear_send(self, element):
        for _ in range(10):
            self.element_send(element, Keys.BACK_SPACE)

    def wait_url(self, url, leave=5, strict=False):
        start = now()
        while not ((strict and url == self.current_url()) or (not strict and url in self.current_url())):
            sleep(0.01)
            if elapsed_seconds(start) >= leave:
                return False
        return True


if __name__ == '__main__':
    s = screen_rect(1000)
    p = Classes.Coord(s.x, s.y)
    # browser = Browser(p)
    # browser = Browser(Classes.Coord(SCREENS["semi_hide"].x, SCREENS["semi_hide"].y))
    browser = Browser(Classes.Coord(SCREENS["semi_hide"].x, SCREENS["semi_hide"].y))
    # r"user-data-dir=C:\Users\alexi_mcstqby\Documents\Bots\AlienWorlds\Profiles\progk")
    browser.new_page('https://www.expressvpn.com/what-is-my-ip')
    input()
