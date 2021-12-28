import inspect
import os
import sys
import traceback
from time import sleep
from typing import Union, Callable, Optional, Iterable

from msedge.selenium_tools import Edge, EdgeOptions
from msedge.selenium_tools.webdriver import WebDriver
from selenium.common.exceptions import SessionNotCreatedException, InvalidSessionIdException, TimeoutException, \
    WebDriverException, InvalidArgumentException, NoSuchWindowException, StaleElementReferenceException, \
    MoveTargetOutOfBoundsException, ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from urllib3.exceptions import NewConnectionError, MaxRetryError

import Alert
import Classes
from Enum import FIRST
from Seleniums.Selenium import profile_name, check_find_fun, get_element_text
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
        self.driver: WebDriver = None
        self.name: Optional[str] = None
        self.windows_url: list[str] = [""]
        self.set_browser(profile)

    def __str__(self):
        return "{} {} {} {}".format(self.name, self.windows_url, self.point, self.profile)

    def __len__(self):
        return len(self.driver.window_handles)

    def print(self, texts: str | Iterable, tab=True):
        print(
            "{}{} {}\t\t\t{}".format(
                "\t" if tab else "", self.name,
                " ¤ ".join(map(str, texts)) if is_iter(texts) and type(texts) is not str else texts,
                self))

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
            self.print(("set_browser", profile), False)
            self.working_window_num = 0
            self.driver = None
            self.windows_url: list[str] = [""]
            if profile is not None:
                self.profile = profile
            elif profile is None and self.profile is not None:
                pass
            self.name = None if profile is None else profile_name(profile)
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
        url = self.driver.current_url
        self.set_windows_url(url, self.get_current_window_num() + 1)
        return url

    def current_url(self):
        return self.update_windows_url()

    def wait_new_window(self, old_count):
        start = now()
        while len(self) <= old_count:
            sleep(0.1)
            if elapsed_seconds(start) >= 5:
                return False
        return True

    def goto(self, window_num, update_working=True):
        print("len(self)", len(self), window_num)
        if len(self) <= window_num:
            return False
        try:
            self.driver.switch_to.window(self.driver.window_handles[window_num])
        except WebDriverException:
            # selenium.common.exceptions.WebDriverException: Message: unknown error: cannot activate web view
            return False
        self.update_windows_url()
        if update_working:
            self.working_window_num = window_num
        return True

    def goto_main(self):
        return self.goto(FIRST)

    def goto_work(self):
        return self.goto(self.working_window_num)

    def goto_last(self):
        return self.goto(len(self.driver.window_handles) - 1)

    def set_windows_url(self, url, window_num):
        for i in range(window_num):
            if i > len(self.driver.window_handles) - 1:
                self.new_tab()
            if i > len(self.windows_url) - 1:
                self.windows_url.append("")
        self.windows_url[window_num - 1] = url

    def new_page(self, url, window_num=None, tries=0):
        try:
            if tries >= 5:
                return False
            if window_num is None:
                window_num = self.get_current_window_num()
            self.print(("new_page", self, url, window_num, tries), False)
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
            sleep(1)
            self.quit()
            sleep(1)
            # noinspection PyMethodFirstArgAssignment
            self = Browser(self.point, self.profile, self.headless)
            return self.new_page(url, window_num, tries + 1)

    def new_tab(self):
        self.driver.execute_script("window.open('');")
        self.set_windows_url("", self.get_current_window_num() + 1)

    def new_tab_and_go(self):
        self.new_tab()
        self.goto_last()

    def close_current_and_go_main(self):
        self.windows_url[self.get_current_window_num()] = ""
        self.close()
        self.goto_main()

    def refresh(self):
        try:
            self.driver.refresh()
        except NoSuchWindowException:
            "selenium.common.exceptions.NoSuchWindowException: Message: no such window: target window already closed"

    def assert_url(self, wanted_url):
        try:
            if wanted_url not in self.current_url():
                self.print(("url_is_not_good", wanted_url, self.current_url()))
                Alert.say("url is not good")
                self.new_page(wanted_url, self.get_current_window_num())
                return False
            return True
        except NoSuchWindowException:
            #     """NoSuchWindowException: Si la fenetre n'existe plus"""
            #     return None
            self.goto_work()
            return None

    def get_current_window_num(self):
        return self.driver.window_handles.index(self.driver.current_window_handle)

    def get_current_url(self):
        return self.driver.current_url

    def close(self):
        assert self.get_current_window_num() != 0
        self.windows_url[self.get_current_window_num()] = ""
        self.driver.close()

    def quit(self):
        self.windows_url = None
        self.driver.quit()
        self.driver = None

    def get_element(self, selectors: str | list[str], find_element_fun: Callable[[WebDriver], str] = None, debug=False) \
        -> None | WebElement | list[WebElement]:
        if debug is None:
            self.print(("get_element", self, selectors, False))
        if find_element_fun is None:
            find_element_fun = self.driver.find_element_by_xpath
        find_element_fun_name = find_element_fun.__name__
        is_elements = "elements" in find_element_fun_name
        if not is_elements:
            find_element_fun = check_find_fun(self.driver, find_element_fun_name)
        try:
            if type(selectors) is str:
                selectors = [selectors]
            for selector in selectors:
                elements: list[WebElement] = find_element_fun(selector)
                if is_elements:
                    return elements
                elif type(elements) == list and len(elements) > 0:
                    return elements[0]
            return None
        except NoSuchWindowException as err:
            # selenium.common.exceptions.NoSuchWindowException: Message: no such window: target window already closed
            self.print("win dont exist")
            sleep(1)
            return None
        # except Exception or UnboundLocalError or AttributeError or NoSuchElementException or \
        #        StaleElementReferenceException or ElementClickInterceptedException:
        #     print(traceback.format_exc(), file=sys.stderr)
        #     Alert.say("\tget_element None")
        #     sleep(1)
        #     return self.get_element(url, selector, find_element_fun, debug)

    def get_all_tag_that_contains(self, web_element, conditions: list[Callable],
                                  tag="div", doublon=False, alone=False) -> dict[str, WebElement] | None:
        print("get_all_tag_that_contains")
        elements = self.get_element(tag, web_element.find_elements_by_tag_name)
        if elements is None:
            return None
        element_dict = {}
        for element in elements:
            element_text = get_element_text(element)
            if element_text is None:
                return None
            print("\tget_all_tag_that_contains_element_text<|" + str(element_text) + "|>")
            for condition in conditions:
                if condition(element_text):
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

    def wait_element(self, url, selector: str, find_element_fun: Callable[[WebDriver], str] = None,
                     appear=True, refresh: int = None, leave: int = None, debug=False) -> Union[bool, WebElement]:
        self.print(("wait_element", self, url, selector, appear, refresh, leave), False)
        self.assert_url(url)
        if find_element_fun is None:
            find_element_fun = self.driver.find_element_by_xpath
        find_element_fun_name = find_element_fun.__name__
        if "elements" in find_element_fun_name:
            self.print("wait_element_find_element_fun_is_not_a_good_type")
            raise ValueError("wait_element_find_element_fun_is_not_a_good_type")
        start_refresh = now()
        start_leave = now()
        element = None
        if appear:
            # On attend que l'element apparaisse
            element = self.get_element(selector, find_element_fun)
            condition = element is None
        else:
            # On attend que l'element disparaisse
            condition = self.get_element(selector, find_element_fun) is not None
        while condition:
            self.assert_url(url)
            if appear:
                element = self.get_element(selector, find_element_fun)
                condition = element is None
            else:
                condition = self.get_element(selector, find_element_fun) is not None
            if debug:
                self.print((selector, find_element_fun, "url =", url))
            if refresh is not None and (now() - start_refresh).total_seconds() >= refresh:
                if url is not None:
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
                return element if element is not None else False
        if debug:
            self.print("True")
        return element if element is not None else True

    def get_text(self, selector: str, find_element_fun=None, refresh_time=None, leave=None, debug=False) \
        -> Optional[str]:
        if debug is None:
            self.print(("get_text", selector, refresh_time, leave), False)
        if find_element_fun is None:
            find_element_fun = self.driver.find_element_by_xpath
        find_element_fun_name = find_element_fun.__name__
        if "elements" in find_element_fun_name:
            self.print("get_text find_element_fun is not a good type")
            raise ValueError("get_text find_element_fun is not a good type")
        if type(selector) is not str:
            self.print("get_text selector is not a good type")
            raise ValueError("get_text selector is not a good type")
        try:
            if leave is not None:
                if self.wait_element(selector, find_element_fun, leave=leave, debug=debug) is False:
                    if debug:
                        self.print("get_text_2 None")
                    return None
            elif refresh_time is not None:
                self.wait_element(selector, find_element_fun, refresh=refresh_time, debug=debug)
            element = self.get_element(selector, find_element_fun)
            if element is None:
                return None
            return get_element_text(element, debug)
        except StaleElementReferenceException:
            return None
        # except NoSuchWindowException or NoSuchElementException as err:
        #     # ok
        #     self.print(("get_text_4 win dont exist", err))
        #     # Alert.say("\tget_text 5 win dont exist", str(err))
        #     sleep(3)
        #     Alert.say("check check check")
        #     return ""
        # except Exception or UnboundLocalError or AttributeError or StaleElementReferenceException or \
        #        ElementClickInterceptedException as err:
        #     self.print(("error Exception get_text", err))
        #     print(traceback.format_exc(), file=sys.stderr)
        #     print("\tget_text_5 None -1")
        #     Alert.say("get_text None -1")
        #     sleep(5)
        #     return None

    def wait_text(self, url, xpath=None, leave=60, refresh=30, min_txt_len=1, debug=True, find_element_fun=None):
        self.print(("wait_text", leave, refresh, min_txt_len))
        self.assert_url(url)
        start = now()
        while elapsed_seconds(start) < leave:
            if elapsed_seconds(start) >= refresh:
                if url is not None:
                    self.new_page(browser, url)
                else:
                    browser.refresh()
                start = now()
            text = self.get_text(xpath, leave=1, debug=debug, find_element_fun=find_element_fun)
            if text is not None and len(text) >= min_txt_len:
                return text
        return False

    def element_click(self, element: WebElement):
        self.print(("element_click", element), False)
        if element is None:
            self.print("element_click_element_is_None")
            return False
        # try:
        try:
            is_enable = element.is_enabled()
            self.print(("click_check_if_is_enable", element.is_enabled()))
            while not is_enable:
                self.print(("click_check_if_is_enable", element.is_enabled()))
                is_enable = element.is_enabled()
                sleep(0.1)
            self.print(("clickA", element.is_enabled()))
            ActionChains(self.driver).click(element).perform()
            return True
        except AttributeError:
            self.print("error_element_click")
            is_enable = element.is_enabled()
            self.print(("click_check_if_is_enable", element.is_enabled()))
            while not is_enable:
                self.print(("click_check_if_is_enable", element.is_enabled()))
                is_enable = element.is_enabled()
                sleep(0.1)
            element.click()
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

    def click_n_wait_new_window(self, element: WebElement) -> bool:
        old_count = len(self)
        self.element_click(element)
        return self.wait_new_window(old_count)

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
                    sleep(0.1)
                    for key in keys:
                        element.send_keys(key)
                    # element.send_keys(keys)
                except AttributeError as err:
                    print("\terror element_send", err)
                    sleep(0.5)
                    self.element_send(element, keys)
            except StaleElementReferenceException:
                """N'existe plus"""

    def clear_send(self, element):
        for _ in range(10):
            self.element_send(element, Keys.BACK_SPACE)


if __name__ == '__main__':
    s = screen_rect(1000)
    p = Classes.Coord(s.x, s.y)
    # browser = Browser(p)
    # browser = Browser(Classes.Coord(SCREENS["semi_hide"].x, SCREENS["semi_hide"].y))
    browser = Browser(Classes.Coord(SCREENS["semi_hide"].x, SCREENS["semi_hide"].y))
    # r"user-data-dir=C:\Users\alexi_mcstqby\Documents\Bots\AlienWorlds\Profiles\progk")
    browser.new_page('https://www.expressvpn.com/what-is-my-ip')
    input()
