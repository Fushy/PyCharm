from time import sleep

from selenium.common.exceptions import NoSuchWindowException, WebDriverException

from Alert import say
from Seleniums.Selenium import wait_second_window_off
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
        browser.print("check_wax_approve")
        for i in range(len(browser)):
            browser.goto(i, False)
            approve_xpath = "/html/body/div/div/section/div[2]/div/div[5]/button"
            browser.print("Avant boucle", False)
            start_while, start_refresh = now(), now()
            while browser.driver.get_window_size()["width"] < 1000:
                approve_text = browser.get_text(approve_xpath)
                browser.print("approve_text", approve_text)
                if approve_text == "Approve":
                    approve = browser.get_element(approve_xpath)
                    if approve is not None:
                        browser.element_click(approve)
                        sleep(2)  # Attend que la transaction fasse effet
                if elapsed_seconds(start_while) > 60:
                    browser.goto_work()
                    return False
                elif elapsed_seconds(start_refresh) > 15:
                    login_button_xpath = "/html/body/div/div/section/div[2]/div/div/button/div"
                    login_button = browser.get_element(login_button_xpath)
                    while login_button and browser.driver.get_window_size()["width"] < 1000:
                        login_button = browser.get_element(login_button_xpath)
                        say("check wax approve have to login")
                        sleep(10)
                    browser.refresh()
                    start_refresh = now()
                if not browser.goto(i, False):
                    del browser.windows_url[i]
                    browser.goto_work()
                    return True
    except NoSuchWindowException or WebDriverException:
        browser.print("Err boucle", False)
        browser.goto_work()
        if i is not None and len(browser.windows_url) > i:
            del browser.windows_url[i]
        return True
    browser.goto_work()
    return True
