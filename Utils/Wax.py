import sqlite3
from typing import Optional

from Alert import say
from Database import insert_or_update, get_column_names
from Jsons import url_to_json_ok, url_to_json, json_to_json_ok, call_request_api
from Prices import db_get_prices, get_n_update_prices
from Regex import re_float
from Telegrams import message
from Times import now
from Util import is_iter

WAX_APPROVE_URL = r"https://all-access.wax.io/"
# WAX_API = r"https://hyperion.docs.eosrio.io/endpoint/#wax"
WAX_API = "https://github.com/cc32d9/eosio_light_api", \
          "https://github.com/cc32d9/eosio_light_api/blob/master/endpoints.json"

# WAX_ENDPOINT_URL = r"https://wax.eosrio.io/v2/state"  #non
# WAX_ENDPOINT_URL = r"https://wax.eosusa.news/v2/state"  #non
# WAX_ENDPOINT_URL =
# WAX_ENDPOINT_URL = r"https://wax.pink.gg/v2/state"
# WAX_ENDPOINT_URL = r"https://api-wax.maltablock.org/v2/state"
# WAX_ENDPOINT_URL = r"https://wax.blokcrafters.io/v2/state"
# WAX_ENDPOINT_URL = r"https://hyperion.wax.eosdetroit.io/v2/state"
# WAX_ENDPOINT_URL = r"hhttps://wax.cryptolions.io/v2/state"

WAX_API_URL_ORDERS = [
    "https://wax.light-api.net/api",
]
WAX_NFT_API_URL_ORDERS = [
    "https://wax.api.atomicassets.io/atomicassets/v1/assets",
]


# def name_to_whitelist_wax_name(name: str):
#     if name == "ogvy":
#         return "o.gvy"
#     if name == "b4nvi":
#         return name
#     elif name == "pyyfu":
#         return name
#     elif name == "o.gvy":
#         return "o.gvy"
#     elif name == "progk":
#         return name
#     elif name == "xvzwu":
#         return name
#     elif name == "jd1.2.c":
#         return "jd1.2.c"
#     elif name == "n11k2.c":
#         return "n11k2.c"
#     raise ValueError(name + " base_name_to_whitelist_name is not a base account from me")


# def base_wam_name_to_whitelist_name(name: str):
#     if name == "ogvy.wam":
#         return "o.gvy.wam"
#     if name == "b4nvi.wam":
#         return name
#     elif name == "pyyfu.wam":
#         return name
#     elif name == "o.gvy.wam":
#         return name
#     elif name == "progk.wam":
#         return name
#     elif name == "xvzwu.wam":
#         return name
#     elif name == "jd1.2.c.wam":
#         return name
#     elif name == "n11k2.c":
#         return name
#     else:
#         raise ValueError("base_wam_name_to_whitelist_name is not a base account from me")


def whitelist_wam_account(name: str, memo: str = None) -> bool:
    whitelist = [
        "b4nvi.wam",

        "pyyfu.wam",
        "o.gvy.wam",
        "progk.wam",

        "xvzwu.wam",
        "jd1.2.c.wam",
        "n11k2.c.wam",

        "g32ke.c.wam",
        "oj3.e.c.wam",
        "e33ke.c.wam",
    ]
    if memo is None:
        return name in whitelist
    elif name == "waxonbinance" and memo == "101666816":
        return True
    else:
        say("Wam account {} is not whitelisted".format(name))
        message("Wam account is not whitelisted")
        return False


def get_tokens(account_names: str | list[str], tokens=None, update=True):
    """ Retourne la quantité de tous les tokens de la blockchain WAX d'un compte. """
    if not is_iter(account_names):
        account_names = [account_names]
    all_asset_amount = {}
    account_assets_amount = {}
    for account_name in account_names:
        asset_amount = call_request_api(WAX_API_URL_ORDERS, "account", "wax", account_name)
        # if asset_amount is None:
        #     return
        # wax_amount = float(re_float.search(asset_amount["account"]["core_liquid_balance"]).group(1))
        asset_amount = json_to_json_ok(asset_amount, ["currency"], ["balances"])
        asset_amount = {asset: float(infos["amount"]) for (asset, infos) in asset_amount.items()
                        if float(infos["amount"]) > 0}
        all_asset_amount.update(asset_amount)
        account_assets_amount[account_name] = asset_amount
    # all_asset_amount = call_request_api("get_tokens", {"account": account_name})
    connection = sqlite3.connect(r"../Bank.db")
    instant = now()
    assets = list(all_asset_amount) + ["WAXP"]
    if tokens is not None:
        assets = list(filter(lambda x: x in tokens, assets))
    if update:
        prices = get_n_update_prices(assets)
    else:
        prices = db_get_prices(assets, update_if_not_present=True)
    for account_name, asset_amount in account_assets_amount.items():
        for asset, amount in asset_amount.items():
            asset = "WAXP" if asset == "WAX" else asset
            if amount == 0 or asset not in prices:
                continue
            dol = round(prices[asset] * amount, 2)
            dol = -1 if dol < 0 else dol
            columns = get_column_names(connection, "WALLETS")
            values = [dol, asset, amount, account_name, "WAXBLOCKS", instant]
            insert_or_update(
                    connection, "WALLETS", values, columns,
                    ["asset", "account_name", "gateway"], [asset, account_name, "WAXBLOCKS"])
    connection.commit()
    connection.close()
    result = {}
    for account, infos in account_assets_amount.items():
        result[account] = {}
        for asset, amount in infos.items():
            asset = "WAXP" if asset == "WAX" else asset
            if tokens is None:
                result[account][asset] = amount
            elif asset in tokens:
                result[account][asset] = amount
    # return account_assets_amount
    return result


def get_nfts(account: str,
             collection_name: Optional[str] = None,
             template_id: Optional[str] = None,
             schema_name: Optional[str] = None,
             limit: int = 1000):
    json = call_request_api(
            WAX_NFT_API_URL_ORDERS, parameters_n_values={"collection_name": collection_name,
                                                         "template_id": template_id,
                                                         "schema_name": schema_name,
                                                         "owner": account,
                                                         "limit": str(limit),
                                                         })
    return json_to_json_ok(json, ["name"], ["data"])
    # url = "{}?collection_name=farmersworld&template_id=260676&owner=b4nvi.wam&limit=1000&order=desc&sort=asset_id" \
    # .format(WAX_NFT_API_URL_ORDERS, )


def get_nft_price(collection_name: Optional[str] = None,
                  template_id: Optional[str] = None,
                  schema_name: Optional[str] = None) -> float:
    sales_url = "https://wax.api.atomicassets.io/atomicmarket/v1/prices/sales"
    json = call_request_api(
            [sales_url], parameters_n_values={
                "collection_name": collection_name,
                "schema_name": schema_name,
                "template_id": template_id,
                "symbol": "WAX",
            })
    infos = json["data"][0]
    decimal_pos = len(infos["price"]) - int(infos["token_precision"])
    return float(infos["price"][:decimal_pos] + "." + infos["price"][decimal_pos:])
