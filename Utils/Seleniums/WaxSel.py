import re
import string
from time import sleep

from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from selenium.webdriver.common.keys import Keys

from Alert import say
from Colors import printc
from Files import file_get_1st_line
from Seleniums.ClassesSel import Browser
from Seleniums.Selenium import get_element_text
from Telegrams import message
from Times import now, elapsed_seconds
from Util import str_to_hashcode
from Wax import WAX_APPROVE_URL
from bot_util import SEED_PATH_1, SEED_PATH_2


def check_wax_approve(browser: Browser, click=True, pre_sleep: int = 1) -> bool:
    sleep(pre_sleep)
    clicked = False
    browser.print(("check_wax_approve", len(browser)), False)
    i = len(browser)
    try:
        while type(i) is int and i > 0:
            browser.goto(i, False)
            width = browser.get_width()
            if width is None:
                end_wax_approve(browser, i)
                return clicked
            start = now()
            while width < 1000 or browser.current_url() == WAX_APPROVE_URL:
                # Approve window
                error_xpath = "/html/body/div/div/section/div[2]/div/div[4]"
                is_error = browser.get_text(WAX_APPROVE_URL, error_xpath)
                if is_error is not None and "Error" in is_error:
                    browser.close()
                    browser.goto_work()
                    return False
                approve_xpath = "/html/body/div/div/section/div[2]/div/div[5]/button"
                approve_text = browser.get_text(WAX_APPROVE_URL, approve_xpath)
                browser.print(("approve_text", approve_text))
                if approve_text == "Approve":
                    approve = browser.get_element(approve_xpath)
                    if approve is not None and click:
                        browser.element_click(approve)
                        sleep(2)  # Attend que la transaction fasse effet
                        clicked = True
                        end_wax_approve(browser, i)
                        return clicked
                else:
                    # Login window
                    login_button_xpath_red = "/html/body/div/div/section/div[2]/div/div/button"
                    white_login_empty_button_xpath = "/html/body/div/div/div/div/div/div[3]/button"
                    login_button_white_xpaths = ["/html/body/div/div/div/div/div[5]/div/div/div/div[4]/button", "/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/div/div/div[4]/button"]
                    red_login_button = browser.get_element(login_button_xpath_red)
                    white_login_empty_button = browser.get_element(white_login_empty_button_xpath)
                    white_login_button = browser.get_element(login_button_white_xpaths)
                    width = browser.get_width()
                    if width is None or elapsed_seconds(start) >= 30:
                        end_wax_approve(browser, i)
                        return clicked
                    while (red_login_button or white_login_empty_button or white_login_button) and width < 1000\
                            or browser.current_url() == WAX_APPROVE_URL:
                        red_login_button = browser.get_element(login_button_xpath_red)
                        white_login_empty_button = browser.get_element(white_login_empty_button_xpath)
                        white_login_button = browser.get_element(login_button_white_xpaths)
                        # login_button_text = get_element_text(red_login_button)
                        # browser.print(i, ("login_button_text", login_button_text))
                        # if login_button_text == "Approve":
                        button = white_login_empty_button or red_login_button
                        if button and click:
                            browser.element_click(button)
                            sleep(1)
                            clicked = True
                            if white_login_empty_button:
                                # browser.goto(i, False)
                                browser.updateinfos_current_page()
                            elif red_login_button:
                                i -= 1
                                browser.goto(i, False)
                            continue
                        elif white_login_button:
                            seed = int(str_to_hashcode(file_get_1st_line(SEED_PATH_1) + file_get_1st_line(SEED_PATH_2), whitelist=string.digits))
                            input = str_to_hashcode(browser.name, seed=seed)
                            email_xpaths = ["/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div[1]/input"]
                            email_input = browser.get_element(email_xpaths)
                            input_xpaths = ["/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div[2]/input"]
                            input_input = browser.get_element(input_xpaths)
                            browser.element_send(email_input, browser.name + "@outlook.com")
                            browser.element_send(input_input, input)
                            browser.element_click(white_login_button)
                            sleep(1)
                            browser.updateinfos_current_page()
                            auth_input_xpath = "/html/body/div[1]/div/section/div[2]/div/div[3]/form/div[1]/div/input"
                            authentified_input_xpath = "/html/body/div/div/div[3]/div[1]/div[3]"
                            browser.wait_element(WAX_APPROVE_URL, [auth_input_xpath, authentified_input_xpath])
                            is_auth = browser.get_element(authentified_input_xpath)
                            if is_auth and get_element_text(is_auth) == "Your Wallet Address":
                                return clicked
                            input = get_login_input(browser)
                            auth_input = browser.get_element(auth_input_xpath)
                            browser.element_send(auth_input, input)
                            browser.element_send(auth_input, Keys.ENTER)
                            input, seed = "13", "37"
                            browser.wait_element(WAX_APPROVE_URL, auth_input_xpath, appear=False)
                            sleep(1)
                            browser.close()
                width = browser.get_width()
                if width is None:
                    end_wax_approve(browser, i)
                    return clicked
            i -= 1
    except NoSuchWindowException or WebDriverException or AttributeError:
        printc("check_wax_approve NoSuchWindowException WebDriverException AttributeError", color="black", background_color="red")
        end_wax_approve(browser, i)
        return clicked
    end_wax_approve(browser, i)
    return clicked


def get_login_input(browser: Browser) -> int | bool:
    outlook_mail_url = "https://outlook.live.com/mail/0/"
    browser.new_url_tab(outlook_mail_url)
    connect_xpath = "/html/body/header/div/aside/div/nav/ul/li[2]/a"
    messages_header_xpath = "/html/body/div[3]/div/div[2]/div[2]/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div/div/div/div"
    popup_close_xpath_1 = "/html/body/div[6]/div/div/div/div[2]/div[2]/div/div[1]/div[2]/button"
    popup_close_xpath_2 = "/html/body/div[7]/div/div/div/div[2]/div[2]/div/div[1]/div[2]/button"
    popup_close_xpaths = [popup_close_xpath_1, popup_close_xpath_2]
    browser.wait_element(outlook_mail_url, [connect_xpath, messages_header_xpath, popup_close_xpath_1, popup_close_xpath_2])
    browser.get_element_n_click(connect_xpath)
    browser.get_element_n_click(popup_close_xpaths)
    browser.wait_element(outlook_mail_url, messages_header_xpath)
    sleep(1)
    popup_close_button = browser.get_element(popup_close_xpaths)
    if popup_close_button:
        sleep(1)
    messages_header = browser.get_element(messages_header_xpath)
    messages = messages_header.find_elements_by_tag_name("div")
    for msg in messages:
        re_verification_code = re.compile("WAX Login Verification Code Login Verification Code ([0-9]{6})")
        print(msg.text)
        if re_verification_code.search(msg.text):
            verification_code = re_verification_code.search(msg.text).group(1)
            browser.close()
            return int(verification_code)
    return False


def end_wax_approve(browser, i):
    browser.print("little window close", False)
    browser.goto_work()
    if i is not None and len(browser.windows_url) > i:
        del browser.windows_url[i]
    browser.goto_work()
