# import datetime
# import glob
# import json as json_api
# import math
# import os
# import statistics
# import Times
# from decimal import Decimal
# from Times import sleep
# from typing import TypeVar, Iterable, Union, Optional, Callable
#
# from audiosegment import AudioSegment
# from binance.exceptions import BinanceAPIException
#
# from new.Config import WEIGHT
# from new.Global import CLIENT
# from new.Util import util_launch_web, util_is_iterable, binance_timestamp_to_datetime
#
# T = TypeVar("T")
# E = TypeVar("E")
#
#
# def get_candles(pair: str, start_time: datetime.datetime, interval=CLIENT.KLINE_INTERVAL_1MINUTE, sleep_time=0,
#                 looking: str = "Close") -> \
#         list[Optional[float]]:  # 1
#     WEIGHT.put(1)
#     while WEIGHT.sum_update() >= 1000:
#         sleep(1)
#     # return_value = CLIENT.get_historical_klines(pair, interval, int(start_time.timestamp() * 1000))[0]
#     plot_datas = CLIENT.get_klines(symbol=pair, interval=interval, limit=500,
#                                      startTime=int(start_time.timestamp() * 1000))
#     if sleep_time > 0:
#         time.sleep(sleep_time)
#     if len(plot_datas) > 0:
#         # return list(map(lambda x: (str(binance_timestamp_to_datetime(x[0])), x[4]), return_value))
#         if looking == "Open":
#             look = 1
#         elif looking == "Close":
#             look = 4
#         return list(map(lambda x: float(x[look]), plot_datas))
#     return None
#
#
# def test(pair: str, start_time: datetime.datetime, interval=CLIENT.KLINE_INTERVAL_1MINUTE, sleep_time=0) -> Optional[
#     float]:  # 1
#     WEIGHT.put(1)
#     while WEIGHT.sum_update() >= 1000:
#         sleep(1)
#     # return_value = CLIENT.get_historical_klines(pair, interval, int(start_time.timestamp() * 1000))[0]
#     return_value = CLIENT.get_klines(symbol=pair, interval=interval, limit=1000,
#                                      startTime=int(start_time.timestamp() * 1000))
#     time.sleep(sleep_time)
#     if len(return_value) > 0:
#         return_value = return_value[:5]
#         # return_value[0], return_value[6] = binance_timestamp_to_datetime(return_value[0]), binance_timestamp_to_datetime(return_value[6])
#         # print(return_value)
#         # return list(map(lambda x: x[4], return_value))
#         return list(map(lambda x: (str(binance_timestamp_to_datetime(x[0])), x[4]), return_value))
#     return None
#
#
# def complete_sell_order_pairs(pairs: Iterable[str], devise="USDT"):  # 5
#     """ A tester """
#     assets = list(map(lambda x: x.replace(devise, ""), pairs))
#     pair_prices: dict[str, dict[str, str]] = get_all_pair_price(CLIENT)
#     assets_infos = json_to_improve_dict(CLIENT.get_account()["balances"], key="asset")
#     for asset in assets:
#         pair = asset + devise
#         cash = asset_cash_estimation_free \
#             (asset, devise, True, pair_prices, assets_infos=assets_infos)
#         if cash >= 10.01:
#             step_size = get_step_size(pair)
#             coins = float(assets_infos[asset]["free"])
#             ask = float(pair_prices[pair]["askPrice"])
#             bid = float(pair_prices[pair]["bidPrice"])
#             sell_order = float(float_decimal(ask, max(last_decimal_position(ask)[1], last_decimal_position(bid)[1])))
#             if "UP" in asset or "DOWN" in asset:
#                 print(asset)
#                 try:
#                     print("sell_limit", asset, coins, sell_order)
#                     sleep(1)
#                     order = CLIENT.order_limit_sell(symbol=pair, quantity=coins, price=sell_order)
#                     print("\nOK. order = ", order)
#                 except BinanceAPIException as binanceError:
#                     print("Message Error", binanceError.message, pair)
#                     coins = float_stepsize(coins - step_size, step_size)
#                     print("sell_limit_step", asset, coins, sell_order)
#                     order = CLIENT.order_limit_sell(symbol=pair, quantity=coins, price=sell_order)
#                     print("\nOK.order = ", order)
#
#
# def get_all_up_and_down_pairs():  # 2
#     all_up_n_down = [p for p in get_all_pair_name_alive() if "UP" in p or "DOWN" in p]
#     all_up_n_down.remove("SUPERBTC")
#     all_up_n_down.remove("SUPERBUSD")
#     all_up_n_down.remove("SUPERUSDT")
#     return all_up_n_down
#
#
# def cancel_all_order_pairs(pairs: Iterable[str], order_side=None):
#     all_open_orders = all_open_orders_pairs()
#     for pair in pairs:
#         if pair in all_open_orders:
#             if order_side is not None:
#                 if all_open_orders[pair]["side"] == order_side:
#                     CLIENT.cancel_order(symbol=pair, orderId=all_open_orders[pair]["orderId"])
#             else:
#                 CLIENT.cancel_order(symbol=pair, orderId=all_open_orders[pair]["orderId"])
#
#
#
#
#
# def get_asset_quantity(currency, precision, account=None):  # 0, 10
#     """ Retourne la quantité d'une crypto libre à la décimal près.
#     >>> [get_asset_quantity("USDT", 1), get_asset_quantity("BNB", 0.1), get_asset_quantity("ETH", 0.01), get_asset_quantity("BTC", 0.001)]
#     [73.0, 1.7, 0.11, 0.003]
#     """
#     if account is None:
#         WEIGHT.put(10)
#         account = json_to_improve_dict(CLIENT.get_account()["balances"], key="asset")
#     return float_stepsize(account[currency]["free"], precision)
#
#
# def get_step_size(pair: str) -> float:  # 1
#     """ Retourne le step_size autorisé par binance d'une crypto.
#     >>> [get_step_size("BNBUSDT"), get_step_size("ETHUSDT"), get_step_size("BTCUSDT")]
#     [73.0, 1.7, 0.11, 0.003]
#     """
#     WEIGHT.put(1)
#     return float(
#         json_to_improve_dict(CLIENT.get_symbol_info(pair)["filters"], key="filterType")["LOT_SIZE"]["stepSize"])
#
#
#
#
# def bank_account(account=None) -> dict[str, dict]:  # 0, 10
#     """
#     >>> bank_account()
#     '{"WIN":{"asset":"WIN","free":50254.36800000,"locked":0.00000000},"HOT":{"asset":"HOT","free":2729.12200000,"locked":0.00000000}, ...}'
#     """
#     if account is None:
#         WEIGHT.put(10)
#         account = json_to_improve_dict(CLIENT.get_account()["balances"], key="asset")
#     return account
#
#
# def bank_account_str(account=None) -> str:  # 0, 10
#     """
#     >>> bank_account()
#     '{"WIN":{"asset":"WIN","free":50254.36800000,"locked":0.00000000},"HOT":{"asset":"HOT","free":2729.12200000,"locked":0.00000000}, ...}'
#     """
#     return sorted_dict(bank_account(account),
#                        key=lambda x: (1 / (float(x[1]["free"]) + 1), 1 / (float(x[1]["locked"]) + 1)))
#
#
# def asset_cash_estimation(asset_from: str, asset_to: str = "USDT", offer=True, pair_prices=None,
#                           assets_infos=None) -> float:  # 0, 10
#     if assets_infos is None:
#         WEIGHT.put(10)
#         assets_infos = json_to_improve_dict(CLIENT.get_account()["balances"], key="asset")
#     asset_infos = assets_infos[asset_from]
#     cash_estimation = float(asset_infos["free"]) + float(asset_infos["locked"])
#     if asset_from == asset_to:
#         return cash_estimation
#     pair = asset_infos["asset"] + asset_to
#     if pair not in pair_prices:
#         return 0
#     if offer:
#         value_price = float(pair_prices[pair]["bidPrice"])
#     else:
#         value_price = float(pair_prices[pair]["price"])
#     return cash_estimation * value_price
#
#
# def asset_cash_estimation_free(asset_from: str, asset_to: str = "USDT", offer=True, pair_prices=None,
#                                assets_infos=None) -> float:  # 0, 10
#     if assets_infos is None:
#         WEIGHT.put(10)
#         assets_infos = json_to_improve_dict(CLIENT.get_account()["balances"], key="asset")
#     asset_infos = assets_infos[asset_from]
#     cash_estimation = float(asset_infos["free"])
#     if asset_from == asset_to:
#         return cash_estimation
#     pair = asset_infos["asset"] + asset_to
#     if pair not in pair_prices:
#         return 0
#     if offer:
#         value_price = float(pair_prices[pair]["bidPrice"])
#     else:
#         value_price = float(pair_prices[pair]["price"])
#     return cash_estimation * value_price
#
#
#
#
#
# def calculate_change_percent(pair: str, price: float):
#     WEIGHT.put(2)
#     pair_prices = get_all_pair_price()
#     pair = pair.replace("_", "").replace("-", "").replace("/", "")
#     return round((float(pair_prices[pair]["bidPrice"]) / float(price) - 1) * 100, 2)
#
#
# def launch_web_chart_commited_pair(other_way: list[str] = ()):
#     devise = "USDT"
#     start_url = "https://cryptowat.ch/fr-fr/charts/BINANCE:"
#     end_url = "?period=15m"
#     start_url_other_way = "https://www.binance.com/fr/trade/"
#     end_url_other_way = "?type=spot"
#     for asset in map(lambda x: x[0], bank_estimation()[1]):
#         if asset != devise:
#             if asset not in other_way:
#                 util_launch_web(start_url + asset + "-" + devise + end_url, "edge")
#             else:
#                 util_launch_web(start_url_other_way + asset + "_" + devise + end_url_other_way, "edge")
#         sleep(2)
#
#
# def bank_estimation(assets_infos=None, pair_prices=None, offer=True) -> tuple[
#     float, list[str, float], float]:  # 0, 10, 12
#     """ Retourne la valeur en dollars de la banque avec pour chacune des crypto dans le compte sa valeur en dollars et sa quantité.
#     >>> bank_estimation()
#     (4393.074714487893, [('BUSD', (1261.79, 1262.16888759)), ... , 3694.142881338625)
#     """
#     print("in")
#     if assets_infos is None:
#         WEIGHT.put(10)
#         assets_infos = json_to_improve_dict(CLIENT.get_account()["balances"], key="asset")
#     if pair_prices is None:
#         WEIGHT.put(2)
#         pair_prices = get_all_pair_price(offer)
#     cash_bank = 0
#     assets_cash = {}
#     # not_pair = ["UP", "DOWN"]
#     not_pair = []
#     for asset_infos in assets_infos.values():
#         coins = float(asset_infos["free"]) + float(asset_infos["locked"])
#         cash = asset_cash_estimation(asset_infos["asset"], "USDT", offer=True, pair_prices=pair_prices,
#                                      assets_infos=assets_infos)
#         if cash < 1 and asset_infos["asset"] != "USDT" or asset_infos["asset"] in not_pair:
#             continue
#         cash_bank += cash
#         cash_visuel = float("{:.2f}".date_format(cash))
#         if cash_visuel > 0:
#             assets_cash[asset_infos["asset"]] = (cash_visuel, coins)
#     cash_bank_eur = cash_bank / float(pair_prices["EURUSDT"]["askPrice"])
#     return cash_bank, sorted(assets_cash.items(), key=lambda x: 1 / x[1][0]), cash_bank_eur
#
#
# def trade_max_value(ratio=1 / 20) -> float:
#     """ Retourne la valeur max accepté par un trade manuel. Fluctue en fonction des stables coins """
#     stables_devises = ["USDT", "BUSD"]
#     return amount_asset_free(stables_devises) * ratio
#
#
# def amount_asset_free(assets: Union[Iterable[str], str] = "USDT", account=None,
#                       pair_prices=None) -> float:  # 0, 2, 10, 12
#     """ Retourne la quantité libre d'une ou de plusieurs crypto en USDT.
#     >>> amount_asset_free("USDT")
#     182.89298754
#     """
#     asset_infos = bank_account(account)
#     if pair_prices is None:
#         WEIGHT.put(2)
#         pair_prices = get_all_pair_price()
#     if not util_is_iterable(assets):
#         return asset_cash_estimation_free(assets, "USDT", pair_prices=pair_prices,
#                                           assets_infos=asset_infos)
#     else:
#         return sum([asset_cash_estimation_free(asset, "USDT", offer=True, pair_prices=pair_prices,
#                                                assets_infos=asset_infos) for asset in asset_infos
#                     if asset in assets])
#
#
# def parser_screener(pattern_start="data-symbol=\"BINANCE:", pattern_end="\">") -> list[str]:
#     """ Je ne sais plus """
#     names: list[str] = []
#     file = open("txt/parse_screener.txt", "r")
#     for line in file.readlines():
#         if line.find("data-field-key=") > 0:
#             start_name_index = line.find(pattern_start) + len(pattern_start)
#             end_name_index = line.find(pattern_end, start_name_index)
#             name: str = line[start_name_index:end_name_index]
#             if name[-4:] == "USDT" and name.find("DOWN") == -1 and name.find("UP") == -1:
#                 names.append(name)
#     file.close()
#     return names[:-1]
#
#
# def all_orders_str(pair: str) -> str:  # 10
#     """ Retourne toutes les ordres de la plus grosse à la plus petite qui ont été effectée sur cette pair.
#     >>> all_orders_str("BNBUSDT")
#     {"354.69000000":{"clientOrderId":"ios_301e60dd0a804b279819e30bbe771b97","cummulativeQuoteQty":875.90380200,"executedQty":2.46970000,"icebergQty":0.00000000,"isWorking":"True","orderId":"2493901119","orderListId":-1,"origQty":2.46970000,"origQuoteOrderQty":0.00000000,"price":354.69000000,"side":"BUY","status":"FILLED","stopPrice":0.00000000,"symbol":"BNBUSDT","time":"1624004384120","timeInForce":"GTC","type":"LIMIT","updateTime":"1624004384120"}, "471.97930000":{"clientOrderId":"ios_da658e11b4f04bbb8d43f28188cff965","cummulativeQuoteQty":32.09459240,"executedQty":0.06800000,"icebergQty":0.00000000,"isWorking":"True","orderId":"1942052560","orderListId":-1,"origQty":0.06800000,"origQuoteOrderQty":0.00000000,"price":471.97930000,"side":"BUY","status":"FILLED","stopPrice":0.00000000,"symbol":"BNBUSDT","time":"1618781984342","timeInForce":"GTC","type":"LIMIT","updateTime":"1618781999309"}, ... }
#     """
#     WEIGHT.put(10)
#     return sorted_dict(json_to_improve_dict(CLIENT.get_all_orders(symbol=pair), key="price"),
#                        key=lambda x: 1 / x[1]["time"])
#
#
# def all_orders(pair: str) -> dict[float, dict]:  # 10
#     """ Retourne toutes les ordres qui ont été effectée sur une pair.
#     >>> all_orders("BNBUSDT")
#     {"354.69000000":{"clientOrderId":"ios_301e60dd0a804b279819e30bbe771b97","cummulativeQuoteQty":875.90380200,"executedQty":2.46970000,"icebergQty":0.00000000,"isWorking":"True","orderId":"2493901119","orderListId":-1,"origQty":2.46970000,"origQuoteOrderQty":0.00000000,"price":354.69000000,"side":"BUY","status":"FILLED","stopPrice":0.00000000,"symbol":"BNBUSDT","time":"1624004384120","timeInForce":"GTC","type":"LIMIT","updateTime":"1624004384120"}, "471.97930000":{"clientOrderId":"ios_da658e11b4f04bbb8d43f28188cff965","cummulativeQuoteQty":32.09459240,"executedQty":0.06800000,"icebergQty":0.00000000,"isWorking":"True","orderId":"1942052560","orderListId":-1,"origQty":0.06800000,"origQuoteOrderQty":0.00000000,"price":471.97930000,"side":"BUY","status":"FILLED","stopPrice":0.00000000,"symbol":"BNBUSDT","time":"1618781984342","timeInForce":"GTC","type":"LIMIT","updateTime":"1618781999309"}, ... }
#     """
#     WEIGHT.put(10)
#     return json_to_improve_dict(CLIENT.get_all_orders(symbol=pair), key="price")
#
#
# def all_open_orders_pairs():  # 40
#     WEIGHT.put(40)
#     return json_to_improve_dict(CLIENT.get_open_orders(), key="symbol")
#
#
# def all_open_orders_pair(pair: str):  # 3
#     WEIGHT.put(3)
#     return json_to_improve_dict(CLIENT.get_open_orders(pair), key="symbol")
#
#
# def sort_fee_pair() -> str:  # 1
#     """ Retourne le dictionnaire contenant les frais des pairs, des petites aux plus grosses.
#     >>> sort_fee_pair()
#     {"1INCHBUSD":{"makerCommission":"0","symbol":"1INCHBUSD","takerCommission":0.001},"AAVEBUSD":{"makerCommission":"0","symbol":"AAVEBUSD","takerCommission":0.001}, ... }
#     """
#     WEIGHT.put(1)
#     # return sorted_dict(json_to_improve_dict(CLIENT.get_trade_fee(), key="symbol")["tradeFee"], key=lambda x: x[1]["taker"])
#     return sorted_dict(json_to_improve_dict(CLIENT.get_trade_fee(), key="symbol"),
#                        key=lambda x: x[1]["makerCommission"])
#
#
# def get_all_pair_price(offer=True) -> dict[str, dict[str, str]]:  # 2
#     """ Retourne les prix actuel de toutes les paires.
#     >>> get_all_pair_price()
#     {'ETHBTC': {'symbol': 'ETHBTC', 'bidPrice': '0.03165600', 'bidQty': '3.86000000', 'askPrice': '0.03165700', 'askQty': '19.10000000'}, ... }
#     >>> get_all_pair_price(False)
#     {'ETHBTC': {'symbol': 'ETHBTC', 'price': '0.05835900'}, ...}
#     """
#     WEIGHT.put(2)
#     if offer:
#         return json_to_improve_dict(CLIENT.get_orderbook_ticker(), key="symbol")
#     else:
#         return json_to_improve_dict(CLIENT.get_symbol_ticker(), key="symbol")
#
#
# def get_all_pair_price_alive() -> dict[str, dict[str, str]]:  # 2
#     """ Retourne les prix actuel de toutes les paires actif sur le marché de Binance. """
#     WEIGHT.put(2)
#     return {asset[0]: asset[1] for asset in
#             json_to_improve_dict(CLIENT.get_orderbook_ticker(), key="symbol").items() if
#             asset[1]["bidPrice"] != "0.00000000" and asset[1]["bidQty"] != "0.00000000"}
#
#
# def get_all_pair_price_dead() -> dict[str, dict[str, str]]:  # 2
#     """ Retourne les prix actuel de toutes les paires morte de Binance. """
#     WEIGHT.put(2)
#     return {asset[0]: asset[1] for asset in
#             json_to_improve_dict(CLIENT.get_orderbook_ticker(), key="symbol").items() if
#             asset[1]["bidPrice"] == "0.00000000" and asset[1]["bidQty"] == "0.00000000"}
#
#
# def get_all_pair_name() -> list[str]:  # 2
#     """ Retourne la liste de toutes les paires.
#     >>> get_all_pair_name()
#     ['1INCHBTC', '1INCHBUSD', ...]
#     """
#     WEIGHT.put(2)
#     return sorted(get_all_pair_price(CLIENT).keys())
#
#
# def get_all_pair_name_alive() -> list[str]:  # 2
#     """ Retourne la liste de toutes les paires actif sur le marché de Binance.
#     >>> get_all_pair_name_alive()
#     ['1INCHBTC', '1INCHBUSD', ...]
#     """
#     WEIGHT.put(2)
#     return sorted(get_all_pair_price_alive().keys())
#
#
# def get_all_assets_name() -> list[str]:  # 10
#     """ Retourne la liste de toutes les crypto.
#     >>> get_all_assets_name()
#     ['1INCH', '1INCHDOWN', ...]
#     """
#     WEIGHT.put(10)
#     return sorted(json_to_improve_dict(CLIENT.get_account()["balances"], key="asset").keys())
#
#
# def get_all_assets_name_alive() -> list[str]:  # 12
#     """ Retourne la liste de toutes les crypto actif sur le marché de Binance.
#     >>> get_all_assets_name_alive()
#     ['1INCH', '1INCHDOWN', ...]
#     """
#     assets_alive = []
#     pairs_alive = get_all_pair_price_alive().keys()
#     for asset in get_all_assets_name():
#         for pair_alive in pairs_alive:
#             if asset in pair_alive:
#                 assets_alive.append(asset)
#                 break
#     return assets_alive
#
#
# def get_all_devises(quantity=False):  # 12
#     """ Essaye de trouver la liste de toutes les devises actif sur le marché de Binance et la retourne par odre du plus probable au moins.
#     >>> get_all_devises()
#     # ['1INCH', '1INCHDOWN', ...]
#     """
#     assets = get_all_assets_name_alive()
#     asset_count = {}
#
#     def incr_asset_count(pair: str):
#         # for i in range(3, len(pair)):
#         for i in range(len(pair) - 2):
#             # if pair[:i] in assets:
#             if pair[-3 - i:] in assets:
#                 if pair[-3 - i:] in asset_count:
#                     asset_count[pair[-3 - i:]] += 1
#                 else:
#                     asset_count[pair[-3 - i:]] = 1
#         return asset_count
#
#     # for pair_name in get_all_pair_name_alive():
#     #     incr_asset_count(pair_name)
#     for pair_name in sorted(get_all_pair_price_dead().keys()):
#         incr_asset_count(pair_name)
#     # print("assets =", assets)
#     # print("pairs =", get_all_pair_name())
#     # print("Top devises =", [devise for (devise, count) in sorted(asset_count.items(), key=lambda x: 1 / x[1]) if count >= 2])
#     if quantity:
#         return [(devise, count) for (devise, count) in sorted(asset_count.items(), key=lambda x: 1 / x[1]) if count >= 2]
#     return [devise for (devise, count) in sorted(asset_count.items(), key=lambda x: 1 / x[1]) if count >= 2]
#
#
# def value_and_pair(pairs: Iterable, dictionary_pairs_info: dict) -> str:
#     """ Retourne les prix actuel d'une liste de paires.
#     >>> value_and_pair()
#
#     """
#     return " \t".join([str(dictionary_pairs_info[pair]["bidPrice"]) + " " + pair for pair in pairs])
#
#
# def delete_log_file():  # supprime les anciens fichiers log
#     """ Je ne sais plus. """
#     for file_name in glob.glob("logs/*.txt"):
#         try:
#             os.remove(file_name)
#         except OSError as e:
#             print("Error: %s : %s" % (file_name, e.strerror))
#     # input("Voulez vous REINITIALISER ???")
#     # REINITIALISER = {pair: [open("historics/" + pair + ".txt", "w").close(), 0] for pair in pairs}
#
#
# def delete_trades_files():  # supprime les anciens fichiers py
#     """ Je ne sais plus. """
#     for file_name in glob.glob("trades/la/*.py"):
#         try:
#             os.remove(file_name)
#         except OSError as e:
#             print("Error: %s : %s" % (file_name, e.strerror))
#     file = open("trades/base_print.py", "r")
#     # file_pattern = "\n".join(file.readlines())
#     file.close()
#
#
# def copy_base_file_to_all_pair_file():
#     """ Je ne sais plus. """
#     file = open("trades/base.py", "r")
#     file_pattern = "\n".join(file.readlines())
#     file.close()
#     for pair in get_all_pair_name():
#         if pair[-4:] == "USDT":
#             file = open("trades/" + pair + ".py", "w")
#             file.write(file_pattern)
#             file.close()
#
#
# def all_open_orders() -> dict:  # 40
#     orders = json_to_improve_dict(CLIENT.get_open_orders(), key="symbol")
#     for order in orders:
#         orders[order]["time"] = binance_timestamp_to_datetime(int(orders[order]["time"]))
#         orders[order]["updateTime"] = binance_timestamp_to_datetime(int(orders[order]["updateTime"]))
#     return orders
#
#
# def all_open_orders_sorted() -> str:  # 40
#     return sorted_dict(all_open_orders(), key=lambda x: x[1]["time"], reverse=True)
#
# def get_assets_higher_than(dol: float):
#     return sorted(
#         ((asset_infos[0], asset_infos[1][0]) for asset_infos in bank_estimation()[1] if
#          float(asset_infos[1][0]) >= dol),
#         key=lambda x: 1 / x[1])
#
#
# def util_repeat_function_binance(fun: Callable, interval_time: datetime.timedelta, debug=False, *args):
#     """ Une fois que la fonction est terminée, on attend :interval_time:."""
#     while True:
#         # try:
#         fun()
#         if debug:
#             print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "executed successfully", *args)
#         sleep(interval_time.total_seconds())
#         # except Exception as err:
#         #     print("___", err)
#         #     print("_", err.args)
#
#
# if __name__ == "__main__":
#     print()
