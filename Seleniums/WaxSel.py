import re
import string
from random import randint
from time import sleep

import selenium
from selenium.common.exceptions import NoSuchWindowException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

from Alert import alert
from Colors import printc
from Files import file_get_1st_line
from Introspection import frameinfo
from Seleniums.ClassesSel import Browser
from Seleniums.Selenium import get_element_text
from Times import now, elapsed_seconds
from utils import str_to_hashcode
from Wax import WAX_APPROVE_URL
from util_bot import SEED_PATH_1, SEED_PATH_2


def check_wax_approve(browser: Browser, pre_sleep: int = 1, refresh_min=None, alert_new_approve=True) -> bool:
    def get_login_input(browser: Browser, fun) -> str | bool:
        outlook_mail_url = "https://outlook.live.com/mail/0/"
        browser.new_url_tab(outlook_mail_url)
        connect_xpath = "/html/body/header/div/aside/div/nav/ul/li[2]/point"
        messages_header_xpath_1 = "/html/body/div[3]/div/div[2]/div[2]/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div/div/div/div"
        messages_header_xpath_2 = "/html/body/div[3]/div/div[2]/div[2]/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div[2]/div/div/div/div/div"
        messages_header_xpath_3 = "/html/body/div[3]/div/div[2]/div[2]/div[2]/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div/div/div/div"
        messages_header_xpath_4 = "/html/body/div[3]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[3]/div/div/div[1]/div[2]/div/div/div/div/div"
        messages_header_xpath_5 = "/html/body/div[2]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[3]/div/div/div[1]/div[2]/div/div/div/div/div"
        messages_header_xpath_6 = "/html/body/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div/div[3]/div/div/div[1]"
        messages_header_xpaths = [messages_header_xpath_1, messages_header_xpath_2, messages_header_xpath_3, messages_header_xpath_5,
                                  messages_header_xpath_4, messages_header_xpath_6][::-1]
        popup_close_xpath_1 = "/html/body/div[6]/div/div/div/div[2]/div[2]/div/div[1]/div[2]/button"
        popup_close_xpath_2 = "/html/body/div[7]/div/div/div/div[2]/div[2]/div/div[1]/div[2]/button"
        connexion_auth_xpath = "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[2]/div[2]/div/input[1]"
        connexion_input_xpath_1 = "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[4]/div/div[2]/input"
        connexion_input_xpath_2 = "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div/div[2]/input"
        popup_close_xpaths = [popup_close_xpath_1, popup_close_xpath_2]
        sleep(10)
        browser.wait_element("", [connexion_input_xpath_1, connexion_input_xpath_2, connexion_auth_xpath,
                                  messages_header_xpath_4, messages_header_xpath_3, messages_header_xpath_5, connect_xpath,
                                  messages_header_xpath_1, messages_header_xpath_2, popup_close_xpath_1, messages_header_xpath_6,
                                  popup_close_xpath_2], refresh=15)
        sleep(1)
        while browser.get_element(connect_xpath):
            browser.get_element_n_click(connect_xpath)
            sleep(1)
        connexion = browser.get_element(connexion_auth_xpath)
        if connexion is not None:
            if browser.name == "jd1.2.c.wam":
                browser.element_send(connexion, "jd1.2.c" + "@outlook.com")
            else:
                browser.element_send(connexion, browser.name + "@outlook.com")
            browser.element_send(connexion, Keys.ENTER)
        sleep(1)
        browser.wait_element("", [connexion_input_xpath_1, connexion_input_xpath_2, connexion_auth_xpath,
                                  messages_header_xpath_4, messages_header_xpath_3, messages_header_xpath_5, connect_xpath, messages_header_xpath_6,
                                  messages_header_xpath_1, messages_header_xpath_2, popup_close_xpath_1,
                                  popup_close_xpath_2], refresh=15)
        connexion_input = browser.get_element([connexion_input_xpath_1, connexion_input_xpath_2])
        ok_xpath = "/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/input"
        if connexion_input:
            aux(browser, connexion_input)
            auth_xpath = "/html/body/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/div/form/div/div[3]/div/div[1]/div[2]/div[4]/input"
            browser.element_send(connexion_input, Keys.ENTER)
            browser.wait_element("", messages_header_xpaths + [ok_xpath] + [auth_xpath])
            while browser.get_element(auth_xpath):
                alert(project_name + " " + browser.name + " sms auth", 1)
            browser.wait_element("", messages_header_xpaths + [ok_xpath])
            ok = browser.get_element(ok_xpath)
            browser.element_click(ok)
        browser.get_element_n_click(popup_close_xpaths)
        start = now()
        while not browser.get_element(messages_header_xpaths):
            browser.get_element_n_click(ok_xpath)
            sleep(1)
            if elapsed_seconds(start) >= 30:
                return get_login_input(browser, fun)
            # alert(PROJECT_NAME + " " + browser.name + "@outlook.com have to login", level=3)
        popup_close_button = browser.get_element(popup_close_xpaths)
        if popup_close_button:
            sleep(1)
        sleep(2)
        messages_header = browser.get_element(messages_header_xpaths)
        messages = messages_header.find_elements_by_tag_name("div")
        verification_code = None
        for msg in messages:
            re_verification_code = re.compile("WAX Login Verification Code Login Verification Code ([0-9]+)")
            msg_text = get_element_text(msg)
            print(msg_text)
            if msg_text is None:
                break
            if re_verification_code.search(msg_text):
                verification_code = re_verification_code.search(msg.text).group(1)
                browser.close()
                return verification_code
        if not verification_code:
            account_bubble_xpath = "/html/body/div[3]/div/div[1]/div/div[1]/div[3]/div[1]/button/div/div[2]/div/div/div/div/div/div[2]"
            disconnect_xpath = "/html/body/div[3]/div/div[1]/div/div[1]/div[3]/div[3]/div/div/div/div/div[1]/point"
            account_bubble = browser.get_element(account_bubble_xpath)
            if account_bubble:
                browser.element_click(account_bubble)
                browser.wait_element_n_click(outlook_mail_url, disconnect_xpath)
                sleep(2)
                return get_login_input(browser, fun)
            alert(browser.name, "have to mail connect")
            input()
        return False

    sleep(pre_sleep)
    clicked = False
    project_name = frameinfo(2)["filename"]
    double_break = False
    browser.print(("check_wax_approve", len(browser)), False)
    save_current_num = browser.get_current_window_num()
    i = len(browser)
    try:
        while type(i) is int and i > 0:
            browser.goto(i)
            width = browser.get_width()
            if width is None:
                end_wax_approve(browser, i, save_current_num)
                return clicked
            start = now()
            while width and width < 1000 or browser.current_url() == WAX_APPROVE_URL:
                if elapsed_seconds(start) >= 30:
                    browser.close()
                    end_wax_approve(browser, i, save_current_num)
                    return clicked
                if double_break:
                    double_break = False
                    break
                # Approve window
                error_xpath = "/html/body/div/div/section/div[2]/div/div[4]"
                is_error = browser.get_text(WAX_APPROVE_URL, error_xpath)
                if is_error is not None and "Error" in is_error:
                    browser.close()
                    end_wax_approve(browser, i, save_current_num)
                    return False
                approve_xpath = "/html/body/div/div/section/div[2]/div/div[5]/button"
                approve = browser.get_element(approve_xpath)
                approve_text = get_element_text(approve)
                browser.print(("approve_text", approve_text))
                if approve_text == "Approve":
                    approve = browser.get_element(approve_xpath)
                    if approve is not None and approve.is_enabled():
                        while alert_new_approve and approve is not None and approve.is_enabled():
                            alert(project_name + " " + browser.name + " ignore new approve")
                            approve = browser.get_element(approve_xpath)
                        browser.element_click(approve)
                        sleep(2)  # Attend que la transaction fasse effet
                        clicked = True
                        end_wax_approve(browser, i, save_current_num)
                        return clicked
                else:
                    # Login window
                    login_button_xpath_red = "/html/body/div/div/section/div[2]/div/div/button"
                    white_login_empty_button_xpath = "/html/body/div/div/div/div/div/div[3]/button"
                    login_button_white_xpaths = ["/html/body/div/div/div/div/div[5]/div/div/div/div[4]/button",
                                                 "/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/div/div/div[4]/button"]
                    red_login_button = browser.get_element(login_button_xpath_red)
                    red_login_button_text = get_element_text(red_login_button)
                    while alert_new_approve and red_login_button_text == "Approve" and alert_new_approve and red_login_button.is_enabled():
                        alert(project_name + " " + browser.name + " ignore new approve", level=1)
                        red_login_button = browser.get_element(login_button_xpath_red)
                        red_login_button_text = get_element_text(red_login_button)
                    white_login_empty_button = browser.get_element(white_login_empty_button_xpath)
                    white_login_button = browser.get_element(login_button_white_xpaths)
                    width = browser.get_width()
                    if (width is None or
                            refresh_min is not None and elapsed_seconds(start) >= randint(refresh_min,
                                                                                          refresh_min + 5)):
                        if width is not None and width < 1000:
                            browser.close()
                        end_wax_approve(browser, i, save_current_num)
                        return clicked
                    if width and not white_login_button and not white_login_empty_button and not red_login_button:
                        sleep(1)
                        width = browser.get_width()
                        agree_1_xpath = "/html/body/div[1]/div/section/div[2]/section/form/label[1]/span[1]/span[1]/input"
                        agree_2_xpath = "/html/body/div[1]/div/section/div[2]/section/form/label[2]/span[1]/span[1]/input"
                        agree_1 = browser.get_element(agree_1_xpath)
                        agree_2 = browser.get_element(agree_2_xpath)
                        if agree_1 and agree_2:
                            browser.element_click(agree_1)
                            browser.element_click(agree_2)
                            agree_button_xpath = "/html/body/div[1]/div/section/div[2]/section/form/div/button/div"
                            browser.get_element_n_click(agree_button_xpath)
                        continue
                    start = now()
                    while (red_login_button or white_login_empty_button or white_login_button) and width < 1000 \
                            or browser.current_url() == WAX_APPROVE_URL:
                        red_login_button = browser.get_element(login_button_xpath_red)
                        white_login_empty_button = browser.get_element(white_login_empty_button_xpath)
                        white_login_button = browser.get_element(login_button_white_xpaths, all_windows=True)
                        button = white_login_empty_button or red_login_button
                        width = browser.get_width()
                        if width and width > 1000 and browser.current_url() != WAX_APPROVE_URL and\
                                (white_login_button or button):
                            return clicked
                        if white_login_button:
                            seed = int(str_to_hashcode(file_get_1st_line(SEED_PATH_1) + file_get_1st_line(SEED_PATH_2),
                                                       whitelist=string.digits))
                            input_txt = str_to_hashcode(browser.name, seed=seed)
                            email_xpaths = [
                                "/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div[1]/input",
                                "/html/body/div[1]/div/div/div/div[5]/div/div/div/div[1]/div[1]/input"]
                            email_input = browser.get_element(email_xpaths)
                            auth_input_xpaths = [
                                "/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div[2]/input",
                                "/html/body/div[1]/div/div/div/div[5]/div/div/div/div[1]/div[2]/input"]
                            auth_input = browser.get_element(auth_input_xpaths)
                            if browser.name == "jd1.2.c.wam":
                                browser.element_send(email_input, "jd1.2.c" + "@outlook.com", debug=False)
                            else:
                                browser.element_send(email_input, browser.name + "@outlook.com", debug=False)
                            clicked = True

                            def aux(browser, element):
                                browser.element_send(element, input_txt, debug=False)

                            while browser.name == "b4nvi.wam":
                                alert(frameinfo(2)["filename"] + " " + browser.name + " have to connect", level=1)
                                width = browser.get_width()
                                if not width or width > 1000:
                                    return clicked
                                sleep(3)
                            else:
                                aux(browser, auth_input)
                                browser.element_click(white_login_button)
                                sleep(1)
                            browser.updateinfos_current_page()
                            # width = browser.get_width()
                            # if width is not None and width < 1000:    # non car casse le login code
                            #     browser.close()
                            #     end_wax_approve(browser, i, save_current_num)
                            #     return clicked
                            auth_input_xpath = "/html/body/div[1]/div/section/div[2]/div/div[3]/form/div[1]/div/input"
                            authentified_input_xpath = "/html/body/div/div/div[3]/div[1]/div[3]"
                            error_xpath = "/html/body/div[1]/div/h1"
                            width = browser.get_width()
                            # if width is not None and width > 1000 or browser.get_text(WAX_APPROVE_URL,
                            #                                                           error_xpath) == "Error":
                            if browser.get_text(WAX_APPROVE_URL, error_xpath) == "Error":
                                browser.close()
                                end_wax_approve(browser, i, save_current_num)
                                return check_wax_approve(browser, pre_sleep)
                            browser.wait_element(WAX_APPROVE_URL, [auth_input_xpath, authentified_input_xpath])
                            is_auth = browser.get_element(authentified_input_xpath)
                            if is_auth and get_element_text(is_auth) == "Your Wallet Address":
                                end_wax_approve(browser, i, save_current_num)
                                return clicked
                            input_txt = get_login_input(browser, aux)
                            auth_input = browser.get_element(auth_input_xpath, all_windows=True)
                            browser.element_send(auth_input, input_txt, debug=False)
                            browser.element_send(auth_input, Keys.ENTER, debug=False)
                            input_txt, seed = "13", "37"
                            sleep(3)
                            browser.updateinfos_current_page()
                            start = now()
                        elif button:
                            browser.element_click(button)
                            sleep(1)
                            clicked = True
                            if white_login_empty_button:
                                browser.updateinfos_current_page()
                            elif red_login_button:
                                browser.updateinfos_current_page()
                            browser.goto(i)
                            continue
                        if elapsed_seconds(start) >= 30:
                            browser.close()
                            end_wax_approve(browser, i, save_current_num)
                            return clicked
                width = browser.get_width()
                if width is None:
                    end_wax_approve(browser, i, save_current_num)
                    return clicked
            i -= 1
    except WebDriverException or selenium.common.exceptions.NoSuchWindowException or StaleElementReferenceException or NoSuchWindowException or AttributeError:
        printc("check_wax_approve NoSuchWindowException WebDriverException AttributeError", color="black",
               background_color="red")
        end_wax_approve(browser, i, save_current_num)
        return clicked
    end_wax_approve(browser, i, save_current_num)
    return clicked


def end_wax_approve(browser, i, save_current_num):
    browser.print("little window close", False)
    browser.goto_work()
    if i is not None and browser is not None and browser.windows_url is not None and len(browser.windows_url) > i:
        del browser.windows_url[i]
    browser.goto(save_current_num)
