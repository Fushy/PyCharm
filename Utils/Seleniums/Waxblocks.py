from time import sleep

from selenium.common.exceptions import StaleElementReferenceException

from Alert import say

WAXBLOCKS_URL = r"https://wax.bloks.io/"


def waxblocks_connection(browser):
    try:
        print("waxblocks_connection")
        browser.new_tab_and_go()
        sleep(5)
        browser.new_page(WAXBLOCKS_URL)
        print("login_transfert_waxblock")
        login_xpath = "/html/body/div[1]/div[1]/div[1]/div/div/div/div[6]/div/div"
        if not browser.wait_element(WAXBLOCKS_URL, login_xpath, leave=10):
            say("change VPN connection")
            return waxblocks_connection(browser)
        connected_xpath = "/html/body/div[1]/div[1]/div[1]/div/div/div/div[6]/div[1]/div"
        is_connected = browser.get_element(connected_xpath) is not None and \
                       "(active)" in browser.get_text(connected_xpath)
        if is_connected:
            return True
        login_button = browser.get_element(login_xpath)
        browser.element_click(login_button)
        sleep(1)
        scrollbar_accounts_xpath = "/html/body/div[1]/div[1]/div[1]/div/div/div/div[6]/div[2]/div[3]/div/span"
        scrollbar_accounts = browser.get_element(scrollbar_accounts_xpath)
        if scrollbar_accounts is None:
            scrollbar_accounts_xpath = "/html/body/div[1]/div[1]/div[1]/div/div/div/div[3]/div[2]/div[3]/div/span"
            scrollbar_accounts = browser.get_element(scrollbar_accounts_xpath)
        if scrollbar_accounts is not None:
            browser.element_click(scrollbar_accounts)
            sleep(1)
        else:
            wallet_container_xpath = "/html/body/div[1]/div[1]/div[3]/div[2]/div/div[2]/div/div[2]/div"
            if not browser.wait_element(WAXBLOCKS_URL, wallet_container_xpath, leave=5):
                return waxblocks_connection(browser)
            wallet_container = browser.get_element(wallet_container_xpath)
            # cloud_wallet_xpath = "/html/body/div[1]/div[1]/div[3]/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div[2]"
            cloud_wallet = list(
                browser.get_all_tag_that_contains(
                    wallet_container,
                    [lambda x: "Cloud Wallet" == x]).values())[0]
            # cloud_wallet = get_element(browser, cloud_wallet)
            if cloud_wallet is not None:
                browser.element_click(cloud_wallet)
                sleep(1)
        if not browser.wait_second_window_off(browser):
            return False
        return True
    except StaleElementReferenceException:
        return waxblocks_connection(browser)
