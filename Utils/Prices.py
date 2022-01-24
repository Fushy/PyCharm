import sqlite3
from time import sleep
from typing import Iterable

from requests.exceptions import ChunkedEncodingError
from requests_html import HTMLSession

from Colors import printc
from Database import get_column_names, insert_or_update
from Jsons import url_to_json_ok
from Regex import re_float
from Strings import get_beetween_text_with_regex, quote
from Times import now
from Util import is_iter, frameinfo


def db_update_price(result, devise, gateway):
    connection = sqlite3.connect(r"../Bank.db")
    columns = get_column_names(connection, "PRICES")
    instant = now()
    for asset, price in result.items():
        values = [price, asset, devise, gateway, instant]
        insert_or_update(connection, "PRICES", values, columns, ["asset", "devise"], [asset, devise])
    connection.commit()
    connection.close()


def from_alcor(assets: str | Iterable[str]):
    """ Retourn les prix des assets en WAX"""
    result = {}
    if not is_iter(assets):
        assets = [assets]
    json = url_to_json_ok(
        'https://wax.alcor.exchange/api/markets',
        keys=["quote_token", "symbol", "name"],
        condition=lambda x: x["base_token"]["symbol"]["name"] == "WAX"
    )
    for asset in assets:
        if asset in json:
            result[asset] = round(float(json[asset]["last_price"]), 8)
    db_update_price(result, "WAXP", "ALCOR")
    return result


def from_gateio(assets: str | Iterable[str]):
    """ Retourn les prix des assets en USDT"""
    result = {}
    if not is_iter(assets):
        assets = [assets]
    html_session = HTMLSession()
    for asset in assets:
        print('https://www.gate.io/fr/trade/{}_USDT'.format(asset))
        try:
            html = html_session.get('https://www.gate.io/fr/trade/{}_USDT'.format(asset)).text
        except ChunkedEncodingError:
            printc("from_gateio ChunkedEncodingError", background_color="red")
            sleep(2)
            return from_gateio(assets)
        if asset.casefold() != "btc" and "BTC Bitcoin" in html[:500]:
            continue
        start = """title="Prix en temps réel">"""
        end = """</i>"""
        regex = get_beetween_text_with_regex(html, start, end, re_float)
        if regex is None:
            continue
        result[asset] = round(float(regex.group(1)), 8)
    db_update_price(result, "USDT", "GATEIO")
    return result


def get_n_update_prices(assets: str | Iterable[str]):
    """ Retourne les prix des assets de la blockchain WAX en USDT et met a jour la base de données """
    if not is_iter(assets):
        assets = [assets]
    wax_result = from_alcor(assets)
    wax_price = from_gateio("WAXP")
    while "WAXP" not in wax_price:
        sleep(5)
        wax_price = from_gateio("WAXP")
    wax_price = wax_price["WAXP"]
    result = {asset: round(asset_value * wax_price, 8) for (asset, asset_value) in wax_result.items()}
    db_update_price(result, "USDT", "ALCORxGATEIO")
    db_update_price({"WAXP": wax_price}, "USDT", "GATEIO")
    result.update({"WAXP": wax_price})
    return result


def db_get_prices(assets: str | Iterable[str], devise="USDT", update_if_not_present=False):
    if not is_iter(assets):
        assets = [assets]
    result = {}
    connection = sqlite3.connect(r"../Bank.db")
    for asset in assets:
        price = connection.execute(
            """SELECT price FROM PRICES WHERE asset = {} and devise = {}"""
            .format(quote(asset), quote(devise))).fetchone()
        if price is None:
            result[asset] = -1
            if update_if_not_present:
                return get_n_update_prices(assets)
        else:
            result[asset] = round(float(price[0]), 8)
    return result
