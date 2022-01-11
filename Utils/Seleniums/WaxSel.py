from time import sleep

from selenium.common.exceptions import NoSuchWindowException, WebDriverException

from Alert import say
from Seleniums.Selenium import get_element_text
from Telegrams import message
from Times import now, elapsed_seconds
from Wax import WAX_APPROVE_URL


def check_wax_approve(browser, click=True, pre_sleep: int=1):
    sleep(pre_sleep)
    i = None
    try:
        browser.print(("check_wax_approve", len(browser)))
        for i in range(len(browser))[::-1]:
            browser.goto(i, False)
            approve_xpath = "/html/body/div/div/section/div[2]/div/div[5]/button"
            start_while = now()
            width = browser.get_width()
            if width is None:
                end_wax_approve(browser, i)
                return True
            while width < 1000:
                error_xpath = "/html/body/div/div/section/div[2]/div/div[4]"
                is_error = browser.get_text(WAX_APPROVE_URL, error_xpath)
                if is_error is not None and "Error" in is_error:
                    browser.close()
                    browser.goto_work()
                    return False
                approve_text = browser.get_text(WAX_APPROVE_URL, approve_xpath)
                browser.print(("approve_text", approve_text))
                if approve_text == "Approve":
                    approve = browser.get_element(approve_xpath)
                    if approve is not None and click:
                        browser.element_click(approve)
                        sleep(2)  # Attend que la transaction fasse effet
                else:
                    login_button_xpath_1 = "/html/body/div/div/section/div[2]/div/div/button"
                    login_button_xpath_2 = "/html/body/div/div/div/div/div/div[3]/button"
                    login_button_xpath_3 = "/html/body/div/div/div/div/div[5]/div/div/div/div[4]/button"
                    login_buttons_xpath = [login_button_xpath_1, login_button_xpath_2, login_button_xpath_3]
                    login_button = browser.get_element(login_buttons_xpath)
                    start = now()
                    width = browser.get_width()
                    if width is None:
                        end_wax_approve(browser, i)
                        return True
                    while login_button and width < 1000 \
                            or browser.current_url() == WAX_APPROVE_URL:
                        login_button_text = get_element_text(login_button)
                        browser.print(("login_button_text", login_button_text))
                        if login_button_text == "Approve":
                            approve = browser.get_element(approve_xpath)
                            if approve is not None and click:
                                browser.element_click(approve)
                                sleep(2)
                        if elapsed_seconds(start) > 15:
                            msg = browser.name + " wax approve have to login"
                            say(msg)
                            message(msg)
                            sleep(10)
                        login_button = browser.get_element(login_buttons_xpath)
                if elapsed_seconds(start_while) > 60:
                    browser.goto_work()
                    return False
                if not browser.goto(i, False):
                    if len(browser) > i:
                        del browser.windows_url[i]
                        browser.goto_work()
                        return True
                    browser.goto_work()
                    return True
    except NoSuchWindowException or WebDriverException or AttributeError:
        # browser.print("Err boucle", False)
        browser.goto_work()
        if i is not None and len(browser.windows_url) > i:
            del browser.windows_url[i]
    browser.goto_work()
    return True


def end_wax_approve(browser, i):
    browser.print("Err boucle", False)
    browser.goto_work()
    if i is not None and len(browser.windows_url) > i:
        del browser.windows_url[i]
    browser.goto_work()
