from time import sleep

from selenium.common.exceptions import NoSuchWindowException, WebDriverException

from Alert import say
from Seleniums.Selenium import wait_second_window_off, get_element_text
from Telegrams import telegram_msg
from Times import now, elapsed_seconds
from Wax import WAX_APPROVE_URL


def wait_close_login_pop_up(browser, name):
    while not wait_second_window_off(browser):
        have_to_login_xpath = "/html/body/div/div/div/div/div[5]/div/div/div/div[1]/div[2]/input"
        have_to_login = None
        for window in browser.window_handles:
            browser.switch_to.window(window)
            have_to_login = browser.get_element(have_to_login_xpath)
            if have_to_login is not None:
                break
        if have_to_login is not None:
            say(name + " have to login")
            sleep(1)
        else:
            browser.switch_to.window(browser.window_handles[-1])
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            return False
    browser.switch_to.window(browser.window_handles[0])
    return True


def check_wax_approve(browser):
    i = None
    try:
        browser.print(("check_wax_approve", len(browser)))
        for i in range(len(browser))[::-1]:
            browser.goto(i, False)
            approve_xpath = "/html/body/div/div/section/div[2]/div/div[5]/button"
            start_while = now()
            while browser.driver.get_window_size()["width"] < 1000:
                error_xpath = "/html/body/div/div/section/div[2]/div/div[4]"
                is_error = browser.get_text(error_xpath)
                if is_error is not None and "Error" in is_error:
                    browser.close()
                    browser.goto_work()
                    return False
                approve_text = browser.get_text(approve_xpath)
                browser.print("approve_text", approve_text)
                if approve_text == "Approve":
                    approve = browser.get_element(approve_xpath)
                    if approve is not None:
                        browser.element_click(approve)
                        sleep(2)  # Attend que la transaction fasse effet
                else:
                    login_button_xpath_1 = "/html/body/div/div/section/div[2]/div/div/button"
                    login_button_xpath_2 = "/html/body/div/div/div/div/div/div[3]/button"
                    login_button_xpath_3 = "/html/body/div/div/div/div/div[5]/div/div/div/div[4]/button"
                    login_buttons_xpath = [login_button_xpath_1, login_button_xpath_2, login_button_xpath_3]
                    login_button = browser.get_element(login_buttons_xpath)
                    while login_button and browser.driver.get_window_size()["width"] < 1000\
                        or browser.current_url() == WAX_APPROVE_URL:
                        login_button_text = get_element_text(login_button)
                        print("login_button_text", login_button_text)
                        if login_button_text == "Approve":
                            approve = browser.get_element(approve_xpath)
                            if approve is not None:
                                browser.element_click(approve)
                                sleep(2)
                        else:
                            login_button = browser.get_element(login_buttons_xpath)
                            msg = browser.name + "wax approve have to login"
                            say(msg)
                            telegram_msg(msg)
                            sleep(10)
                if elapsed_seconds(start_while) > 60:
                    browser.goto_work()
                    return False
                if not browser.goto(i, False):
                    del browser.windows_url[i]
                    browser.goto_work()
                    return True
    except NoSuchWindowException or WebDriverException:
        browser.print("Err boucle", False)
        browser.goto_work()
        if i is not None and len(browser.windows_url) > i:
            del browser.windows_url[i]
    browser.goto_work()
    return True
