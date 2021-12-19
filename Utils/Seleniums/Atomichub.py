from time import sleep

from selenium.common.exceptions import StaleElementReferenceException

from Wax import whitelist_wam_account


def atomichub_transfert_nft(browser, name_to: str, nft_ids: list[int]):
    try:
        browser.print(("atomichub_transfert_nft", name_to, nft_ids, False))
        if not whitelist_wam_account(name_to):
            raise ValueError("Wam account is not whitelisted")
        url_transfert = r"https://wax.atomichub.io/trading/transfer?asset_id=" + ",".join(map(str, nft_ids))
        browser.new_page(url_transfert)
        accept_cooki_btn_xpath = "/html/body/div[3]/div/div/div/div[2]/button[1]"
        accept_cooki_btn = browser.get_element(accept_cooki_btn_xpath)
        if accept_cooki_btn is not None:
            browser.element_click(accept_cooki_btn)
        input_to_xpath = "/html/body/div/div[2]/div/div[2]/div[2]/div[3]/table/tbody/tr[1]/td[2]/div/div/div/input"
        browser.wait_element(url_transfert, input_to_xpath, refresh=10)
        input_to = browser.get_element(input_to_xpath)
        browser.clear_send(input_to)
        browser.element_send(input_to, name_to)
        send_transfer_button_xpath = "/html/body/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/button"
        send_transfer_button = browser.get_element(send_transfer_button_xpath)
        if not send_transfer_button.is_enabled():
            browser.print("\tvalidate_button_is_not_enabled")
            return False
        browser.element_click(send_transfer_button)
        confirm_button_xpath = "/html/body/div[3]/div/div/div[2]/div[2]/div/button"
        browser.wait_element(url_transfert, confirm_button_xpath)
        transaction_message_xpath = "/html/body/div[3]/div/div/div/div[2]/div[1]"
        while True:
            transaction_message_text = browser.get_text(transaction_message_xpath)
            if transaction_message_text is not None and "Transaction" in transaction_message_text:
                break
            elif transaction_message_text == "Confirm":
                confirm_button = browser.get_element(confirm_button_xpath)
                browser.element_click(confirm_button)
            sleep(1)
    except StaleElementReferenceException:
        return atomichub_transfert_nft(browser, name_to, nft_ids)

