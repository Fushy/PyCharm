# def check_alcor_token(browser, profile, token: str):
#     name = profile_name(profile)
#     print("check_alcor_token", name, token)
#     new_page(browser, "https://wax.alcor.exchange/trade/" + token + "-farmerstoken_wax-eosio.token", profile)
#     url = "https://wax.alcor.exchange/trade/" + token + "-farmerstoken_wax-eosio.token"
#     try:
#         bids_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[2]"
#         wait_element(browser, bids_xpath, refresh=5, url=url)
#         if not login_alcor(browser, name):
#             return check_alcor_token(browser, profile, token)
#         sleep(1)
#         wallet_tokens_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[2]/div/small[2]"
#         alpha_text_found = None
#         while alpha_text_found is None:
#             connect_wallet_xpath = "/html/body/div/div/div/div[4]/nav/div[2]/div/div[2]/button[1]"
#             connect_wallet_text = get_text(browser, connect_wallet_xpath)
#             if connect_wallet_text is not None and "Connect Wallet" in connect_wallet_text:
#                 if not login_alcor(browser, name):
#                     return check_alcor_token(browser, profile, token)
#             sleep(1)
#             text = get_text(browser, wallet_tokens_xpath)
#             alpha_text_found = re_alpha.search(text)
#         sleep(1)
#         return get_trading_infos(browser)
#     except NoSuchElementException as err:
#         print("\t", name, "retry tokens_to_wax", err.msg)
#         return check_alcor_token(browser, profile, token)
import sqlite3
from datetime import datetime
from time import sleep

from Selenium.Selenium import get_element, element_click, wait_element, profile_name, get_text
from Selenium.Wax import wait_close_login_pop_up
from Times import now


def login_alcor(browser, name):
    # REFAIRE
    wallet_name_xpath = "/html/body/div/div/div/div[4]/nav/div[2]/div/div[2]/div/div[2]/div"
    wallet_name = get_element(browser, wallet_name_xpath)
    if wallet_name is None:
        wallet_name_xpath = "/html/body/div[1]/div/div/div[3]/nav/div[2]/div/div[2]/div/div[2]"
        wallet_name = get_element(browser, wallet_name_xpath)
    if wallet_name is None:
        wallet_connect_xpath = "/html/body/div/div/div/div[4]/nav/div[2]/div/div[2]/button[1]"
        wallet_connect = browser.find_element_by_xpath(wallet_connect_xpath)
        element_click(browser, wallet_connect)
        is_connected_xpath = "/html/body/div/div/div/div[4]/nav/div[2]/div/div[2]/div"
        is_connected = get_element(browser, is_connected_xpath)
        if is_connected is not None:
            return True
        wallet_wax_xpath = "/html/body/div[2]/div/div[2]/div/div[1]/div[1]/button"
        wait_element(browser, wallet_wax_xpath, leave=5)
        if wait_element is None:
            is_connected = get_element(browser, is_connected_xpath)
            if is_connected is not None:
                return True
            return False
        wallet_wax = get_element(browser, wallet_wax_xpath)
        if wallet_wax is None:
            return False
        element_click(browser, wallet_wax)
        sleep(1)
        browser.refresh()
    return wait_close_login_pop_up(browser, name)


def get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me=1, devise_to_buy=None):
    try:
        name = profile_name(profile)
        print("get_trading_infos", name, token, ratio_tokens_befor_me, devise_to_buy)
        my_ask = None
        bids_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[2]"
        wait_element(browser, bids_xpath, refresh=5, debug=True)
        sleep(5)
        devise_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div/small[2]"
        devise_text = get_text(browser, devise_xpath).replace(",", "")
        devise = devise_text.split(" ")[0]
        print("\tdevise", devise)
        if devise is None:
            browser.refresh()
            sleep(5)
            return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
        devise = float(devise)
        my_tokens_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[2]/div/small[2]"
        my_tokens = get_element(browser, my_tokens_xpath)
        if my_tokens is None or my_tokens == "":
            sleep(5)
            return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
        my_tokens_text = get_text(my_tokens).replace(",", "")
        print("\tmy_tokens_text", my_tokens_text)
        if my_tokens_text is None or my_tokens_text[:-4] == "":
            sleep(5)
            return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
        tokens = float(my_tokens_text[:-4])
        # bids = browser.find_elements_by_xpath(bids_xpath)
        # lower_bid = bids[-1]
        # lower_bid = float(lower_bid.text.split("\n")[-3])
        # my_bid = lower_bid - 0.00001
        all_ask_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[2]"
        all_ask = get_element(browser, all_ask_xpath)
        ask_line_class = "ltd.d-flex.text-danger"
        asks = get_element(all_ask, ask_line_class, browser.find_elements_by_class_name)
        sum_tokens = 0
        for ask in asks:
            ask_text = get_text(ask)
            if ask_text is None:
                return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
            ask_text = ask_text.replace(",", "")
            if ask_text is None or ask_text == "":
                # asks = get_element(all_ask, ask_line_class, browser.find_elements_by_class_name)
                # continue
                return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
            print("\t", name, "ask_text", ask_text)
            if "win" in ask_text:
                return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
            ask_price_devise, ask_token, total_ask_devise = map(lambda x: float(x.replace(",", "")), ask_text.split())
            sum_tokens += ask_token
            # Il y a eu un None
            if sum_tokens >= tokens * ratio_tokens_befor_me or (
                    devise_to_buy is not None and sum_tokens * ask_price_devise >= devise_to_buy):
                my_ask = ask_price_devise - 0.0000001
                break
        lower_bid_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[4]/div[1]/span[1]"
        lower_bid = get_text(browser, lower_bid_xpath)
        if lower_bid is None:
            return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
        lower_bid_text = lower_bid.replace(",", "")
        if lower_bid_text == "":
            return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
        lower_bid = float(lower_bid_text)
        my_bid = lower_bid + 0.0000001
    except IndexError:
        browser.refresh()
        sleep(5)
        return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
    print("\t", "get_trading_infos", my_bid, my_ask, tokens, devise)
    if my_ask is None:
        print("\t", name, "get_trading_infos", my_bid, my_ask, tokens, devise)
        return my_bid, my_ask, tokens, devise
        # return get_trading_infos(browser, profile, stats, token, ratio_tokens_befor_me, devise_to_buy)
    stats[name][token + "_tokens"] = tokens
    stats[name]["wax_tokens"] = devise
    if "wax_price" in stats["all"] and "wax_tokens" in stats[name]:
        stats[name]["wax_to_dol"] = stats[name]["wax_tokens"] * stats["all"]["wax_price"]
    print("\t", name, "get_trading_infos", my_bid, my_ask, tokens, devise)
    return my_bid, my_ask, tokens, devise


def have_to_deposit_wax(amount=0):
    connection = sqlite3.connect("D:\_Fichier-PC\Documents\Projets_dev\Python\pythonProject\Bank.sqlite")
    today = now(True).date()
    cursor = connection.execute("""select date from BINANCE_DEPOT where asset == 'WAXP' and dol_estimate >= {} ORDER BY date DESC""".format(amount))
    tuples = cursor.fetchall()
    for elements in tuples:
        depot_date = datetime.strptime(elements[0], "%Y-%m-%d %H:%M:%S.%f")
        if depot_date.date() == today:
            return False
    print(today)
    print(today.day)
    # if today.day == 9:
    #     return False
    connection.commit()
    connection.close()
    return True
