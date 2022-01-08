from time import sleep

from selenium.webdriver.common.keys import Keys

from Alert import say
from Regex import search_n_get_float
from Seleniums.ClassesSel import Browser
from Seleniums.Selenium import get_element_text
from Seleniums.WaxSel import check_wax_approve
from Telegrams import message
from Times import elapsed_seconds, now
from Wax import whitelist_wam_account

ALCOR_TRANSFERT_URL = "https://wax.alcor.exchange/wallet"

alcor_trade_url = "https://wax.alcor.exchange/trade/"
devise_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[" \
               "1]/div/div/div[1]/div/small[2]"
token_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[" \
              "1]/div/div/div[2]/div/small[2]"


def connect(browser: Browser) -> bool:
    browser.print("login_alcor", False)
    browser.new_page(ALCOR_TRANSFERT_URL)
    search_name_xpath_1 = "/html/body/div/div/div/div[4]/div/div/div[6]/div/div[2]/div/div[2]/table/thead/tr/th[1]/div"
    search_name_xpath_2 = "/html/body/div/div/div/div[4]/div/div/div[7]/div/div[2]/div/div[2]/table/thead/tr/th[1]/div"
    if browser.wait_text(ALCOR_TRANSFERT_URL, [search_name_xpath_1, search_name_xpath_2]) != "Asset":
        return False
    connect_wallet_xpath = "/html/body/div/div/div/div[4]/nav/div[2]/div/div[2]/button[1]"
    if browser.get_text(ALCOR_TRANSFERT_URL, connect_wallet_xpath) == "Connect Wallet":
        wallet_connect_xpath = "/html/body/div/div/div/div[4]/nav/div[2]/div/div[2]/button[1]"
        wallet_connect = browser.get_element(wallet_connect_xpath)
        browser.element_click(wallet_connect)
        wallet_wax_xpath = "/html/body/div[2]/div/div[2]/div/div[1]/div[1]/button"
        wallet_wax = browser.get_element(wallet_wax_xpath)
        browser.element_click(wallet_wax)
        sleep(1)
        check_wax_approve(browser, click=False)
    name_xpath_1 = "/html/body/div/div/div/div[4]/nav/div[2]/div/div[2]/div/div[2]"
    name_xpath_2 = "/html/body/div[1]/div/div/div[3]/nav/div[2]/div/div[2]/div/div[2]"
    if not browser.wait_element(ALCOR_TRANSFERT_URL, [name_xpath_1, name_xpath_2]):
        return False
    return True


def transaction(browser: Browser,
                to: str,
                amount: float,
                token_send: str,
                memo: str = None,
                send_msg: bool = False) -> bool:
    """ amount = -1 <=> max """
    if amount == 0:
        return True
    name = browser.name
    browser.print(("transaction", to, amount, token_send, memo), False)
    if not whitelist_wam_account(to, memo):
        raise ValueError("Wam account is not whitelisted")
    connect(browser)
    tokens_container_xpath_1 = "/html/body/div[1]/div/div/div[3]/div/div/div[7]/div/div[2]/div/div[3]/table/tbody"
    tokens_container_xpath_2 = "/html/body/div/div/div/div[4]/div/div/div[7]/div/div[2]/div/div[3]/table/tbody"
    tokens_container = browser.wait_element(ALCOR_TRANSFERT_URL, [tokens_container_xpath_1, tokens_container_xpath_2])
    if not tokens_container:
        return False
    tokens_tag = "tr"
    old_tokens_len = len(tokens_container.find_elements_by_tag_name(tokens_tag))
    while True:
        sleep(1)
        tokens = tokens_container.find_elements_by_tag_name(tokens_tag)
        if len(tokens) == old_tokens_len:
            break
        old_tokens_len = len(tokens)
    i = 1 - 4
    token_text = ""
    token = None
    for token in tokens:
        token_text = get_element_text(token)
        if token_send in token_text:
            break
        i += 4
    if token_send not in token_text:
        browser.print(("not_found_token", to, amount, token_send, memo))
        return False
    transfert_class = "el-button"
    if token is None:
        return False
    action_buttons = token.find_elements_by_class_name(transfert_class)
    if action_buttons is None:
        return False
    transfert_button = action_buttons[1]
    tokens_xpath_1 = "/html/body/div[1]/div/div/div[3]/div/div/div[7]/div/div[4]/div/div[2]/form/div[2]/div/span/button/span"
    tokens_xpath_2 = "/html/body/div[1]/div/div/div[4]/div/div/div[7]/div/div[4]/div/div[2]/form/div[2]/div/span/button/span"
    start = now()
    while True:
        if elapsed_seconds(start) > 30:
            return False
        browser.element_click(transfert_button)
        token_text = browser.wait_text(ALCOR_TRANSFERT_URL, [tokens_xpath_1, tokens_xpath_2], leave=2)
        if token_text is not None:
            break
    tokens = search_n_get_float(token_text)
    if tokens is None:
        return False
    browser.print(("token_send", token_send, tokens))
    if float(tokens) < float(amount):
        browser.print(("not_enough_tokens", tokens, "<", amount))
        return True
    inputs_xpath_1 = "/html/body/div[1]/div/div/div[3]/div/div/div[7]/div/div[4]/div/div[2]/form"
    inputs_xpath_2 = "/html/body/div[1]/div/div/div[4]/div/div/div[7]/div/div[4]/div/div[2]/form"
    inputs = browser.get_element([inputs_xpath_1, inputs_xpath_2]).find_elements_by_class_name("el-input__inner")
    adress_to = inputs[0]
    amount_send = inputs[1]
    memo_send = inputs[2]
    browser.element_send(adress_to, to)
    browser.element_send(memo_send, memo)
    amount_send_tokens = tokens if amount == -1 else amount
    browser.element_send(amount_send, Keys.BACK_SPACE, amount_send_tokens)
    send_transfer_class = "el-button.w-100.done.el-button--primary"
    send_transfer = browser.get_element(send_transfer_class, browser.driver.find_element_by_class_name)
    browser.element_click(send_transfer)
    # laaa
    browser.print(("transaction_sent", to, amount, token_send, memo))
    msgbox_header_xpath = "/html/body/div[3]/div/div[1]/div"
    transaction_text = browser.wait_text(ALCOR_TRANSFERT_URL, msgbox_header_xpath)
    if not transaction_text or (transaction_text and "Transaction complete!" not in transaction_text):
        while True:
            # relaunch apres avoir vérifié que tout est correct
            say(name + " have to validate Alcor transaction")
            say(name + " have to validate Alcor transaction")
            message(name + " have to validate Alcor transaction")
            sleep(30)
    if send_msg:
        browser.print(("transaction", to, amount, token_send, memo), False)
        message("{} {} Alcor transaction sent to {} {}".format(amount, token_send, to, memo))
    return True


def buy(browser: Browser, asset: str, roof_tokens_to_have: float) -> tuple[bool, bool]:
    asset = asset.upper()
    browser.print(("Alcor.sell", asset, roof_tokens_to_have), False)
    if not connect(browser):
        return False, False
    connect_to_trading(browser, asset)
    higher_bid_amount_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[4]/div[1]"
    # devise_amount = search_n_get_float(browser.get_text(alcor_trade_url, devise_xpath))
    token_amount = search_n_get_float(browser.get_text(alcor_trade_url, token_xpath))
    higher_bid_amount = search_n_get_float(browser.get_text(alcor_trade_url, higher_bid_amount_xpath))
    price_input_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[" \
                        "2]/div[1]/div/div/div[1]/form/div[1]/div/div/input"
    price_input = browser.get_element(price_input_xpath)
    if token_amount >= roof_tokens_to_have * 0.95:
        return True, True
    tokens_to_buy = (roof_tokens_to_have - token_amount) * higher_bid_amount
    browser.element_send(price_input, higher_bid_amount + 0.0000001)
    browser.print(("tokens_to_buy", tokens_to_buy, "use", tokens_to_buy * higher_bid_amount))
    total_input_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[" \
                        "2]/div[1]/div/div/div[1]/form/div[4]/div/div/input"
    total_input = browser.get_element(total_input_xpath)
    browser.clear_send(total_input)
    browser.element_send(total_input, tokens_to_buy)
    buy_button_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[" \
                       "2]/div[1]/div/div/div[1]/form/div[5]/div/button"
    browser.get_element_n_click(buy_button_xpath)
    # laaa
    start = now()
    existing_trades_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[1]/div/div/div[" \
                            "2]/div[1]/div/div[3]/table/tbody"
    trades_class = "el-table__row"
    existing_trades = browser.get_element(existing_trades_xpath)
    while len(existing_trades.find_elements_by_class_name(trades_class)) == 0:
        if elapsed_seconds(start) > 30:
            return False, False
        sleep(1)
        existing_trades = browser.get_element(existing_trades_xpath)
    return True, False


def sell(browser: Browser, asset: str, floor_tokens_to_keep: float) -> tuple[bool, bool]:
    asset = asset.upper()
    ratio_tokens_befor_me_to_cancel = 0.95
    browser.print(("Alcor.sell", asset, floor_tokens_to_keep), False)
    if not connect(browser):
        return False, False
    connect_to_trading(browser, asset)
    sell_price = 0
    while True:
        existing_trades_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[1]/div/div/div[" \
                                "2]/div[1]/div/div[3]/table/tbody"
        existing_trades = browser.get_element(existing_trades_xpath)
        if existing_trades is None:
            return False, False
        trades_class = "el-table__row"
        my_trades = existing_trades.find_elements_by_class_name(trades_class)
        trades_len = len(my_trades)
        if trades_len == 0:
            asks = get_all_asks(browser)
            sum_tokens_befor_me = 0
            for ask in asks:
                ask_text = get_element_text(ask)
                if ask_text is None or ask_text == "":
                    return False, False
                ask_price_devise, ask_token, total_ask_devise = map(
                    lambda x: float(x.replace(",", "")), ask_text.split())
                if sum_tokens_befor_me > ask_token * ratio_tokens_befor_me_to_cancel:
                    sell_price = ask_price_devise
                    break
                sum_tokens_befor_me += ask_token
            if sell_price > 0:
                break
        elif trades_len > 1:
            cancel_all_orders_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[" \
                                      "1]/div/div/div[1]/div/div/div[2]/button"
            browser.get_element_n_click(cancel_all_orders_xpath)
            sleep(1)
            continue
        elif trades_len == 1:
            trade = my_trades[0]
            trade_txt = get_element_text(trade)
            my_type_trade, my_date_trade, my_ask, my_bid, my_price, _ = trade_txt.split("\n")
            my_ask, my_bid, my_price = map(lambda x: search_n_get_float(x), (my_ask, my_bid, my_price))
            is_sell = "SELL" == my_type_trade
            if not is_sell:
                cancel_all_orders_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[" \
                                          "1]/div/div/div[1]/div/div/div[2]/button"
                browser.get_element_n_click(cancel_all_orders_xpath)
                break
            asks = get_all_asks(browser)
            sum_tokens_befor_me = 0
            for ask in asks:
                ask_text = get_element_text(ask)
                start_loop = now()
                while ask_text is None or ask_text == "":
                    ask_text = get_element_text(ask)
                    if elapsed_seconds(start_loop) >= 30:
                        return False, False
                ask_price_devise, ask_token, total_ask_devise = map(
                    lambda x: float(x.replace(",", "")), ask_text.split())
                is_my_ask = float(my_ask) == ask_price_devise
                if not is_my_ask:
                    sum_tokens_befor_me += ask_token
                # N'actualise pas le trade lorsque la somme des tokens jusqu'a l'ordre est < à l'ordre
                elif sum_tokens_befor_me <= ask_token * ratio_tokens_befor_me_to_cancel:
                    browser.print(
                        ("order_exist_and_is_fine",
                         sum_tokens_befor_me, "<=", ask_token * ratio_tokens_befor_me_to_cancel))
                else:
                    browser.print(
                        ("order_exist_and_is_not_fine_cancel_order",
                         sum_tokens_befor_me, ">", ask_token * ratio_tokens_befor_me_to_cancel))
                    cancel_all_orders_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[" \
                                              "1]/div/div/div[1]/div/div/div[2]/button"
                    browser.get_element_n_click(cancel_all_orders_xpath)
                    break
    # lower_ask_amount_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[1]"
    # higher_bid_amount_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[
    # 4]/div[1]"
    # devise_amount = search_n_get_float(browser.get_text(alcor_trade_url, devise_xpath))
    token_amount = search_n_get_float(browser.get_text(alcor_trade_url, token_xpath))
    # lower_ask_amount = search_n_get_float(browser.get_text(alcor_trade_url, lower_ask_amount_xpath))
    # higher_bid_amount = search_n_get_float(browser.get_text(alcor_trade_url, higher_bid_amount_xpath))
    price_input_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[" \
                        "2]/div[1]/div/div/div[2]/form/div[1]/div/div/input"
    price_input = browser.get_element(price_input_xpath)
    if token_amount <= floor_tokens_to_keep * 0.95:
        return True, True
    browser.element_send(price_input, sell_price - 0.0000001)
    if floor_tokens_to_keep == -1:  # all
        browser.print(("tokens_to_sell", token_amount, "to have devise", token_amount * sell_price))
        browser.get_element_n_click(token_xpath)
    else:
        tokens_to_sell = token_amount - floor_tokens_to_keep - 1
        browser.print(("tokens_to_sell", tokens_to_sell, "to have devise", tokens_to_sell * sell_price))
        token_input_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[" \
                            "2]/div[2]/div[1]/div/div/div[2]/form/div[2]/div/div/input"
        token_input = browser.get_element(token_input_xpath)
        browser.clear_send(token_input)
        browser.element_send(token_input, tokens_to_sell)
    sell_button_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[" \
                        "2]/div[1]/div/div/div[2]/form/div[5]/div/button"
    browser.get_element_n_click(sell_button_xpath)
    # laaa
    start = now()
    while len(existing_trades.find_elements_by_class_name(trades_class)) == 0:
        if elapsed_seconds(start) > 30:
            return False, False
        sleep(1)
        existing_trades = browser.get_element(existing_trades_xpath)
    return True, False


def connect_to_trading(browser, asset):
    alcor_markets_url = "https://wax.alcor.exchange/markets"
    browser.new_page(alcor_markets_url)
    wax_filter_xpath = "/html/body/div/div/div/div[4]/div/div/div[1]/div[1]/label[3]"
    browser.wait_element_n_click(alcor_markets_url, wax_filter_xpath)
    search_token_xpath = "/html/body/div/div/div/div[4]/div/div/div[1]/div[2]/div/input"
    search_token = browser.get_element(search_token_xpath)
    if search_token is not None:
        browser.element_send(search_token, asset)
    tokens_container_xpath = "/html/body/div/div/div/div[4]/div/div/div[2]/div/div[3]/table/tbody"
    tokens_container = browser.get_element(tokens_container_xpath)
    if tokens_container is None:
        return False
    tokens_tag = "tr"
    tokens = tokens_container.find_elements_by_tag_name(tokens_tag)
    token = None
    for token in tokens:
        token_text = get_element_text(token)
        if token_text is not None and token_text[:len(asset)] == asset:
            break
    if token is None:
        return False
    browser.element_click(token)
    if not browser.wait_url(alcor_trade_url):
        return False
    browser.wait_text(alcor_trade_url, devise_xpath)
    browser.wait_text(alcor_trade_url, token_xpath)
    return True


def get_all_asks(browser):
    all_ask_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[2]"
    all_ask = browser.get_element(all_ask_xpath)
    ask_line_class = "ltd.d-flex.text-danger"
    asks = all_ask.find_elements_by_class_name(ask_line_class)
    while len(asks) == 0:
        asks = all_ask.find_elements_by_class_name(ask_line_class)
        sleep(1)
    return asks
