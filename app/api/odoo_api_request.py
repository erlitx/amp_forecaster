
from os import environ
import os
from odoo_rpc_client import Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import itertools


load_dotenv()
HOST = environ.get("ODOO_HOSTNAME")
PORT = int(environ.get("ODOO_PORT"))
DATABASE = environ.get("ODOO_DATABASE")
USERNAME = environ["ODOO_USERNAME"]
PASSWORD = environ["ODOO_PASSWORD"]


def odoo_api_get_inventory(products_num=1):
    def batch(iterable, size):
        "Split iterable by chunks of size (at max)"
        it = iter(iterable)
        while item := list(itertools.islice(it, size)):
            yield item


    load_dotenv()
    HOST = environ.get("ODOO_HOSTNAME")
    PORT = int(environ.get("ODOO_PORT"))
    DATABASE = environ.get("ODOO_DATABASE")
    USERNAME = environ["ODOO_USERNAME"]
    PASSWORD = environ["ODOO_PASSWORD"]

    ################
    # limit queries - 0 is no limit
    MAX_PRODUCTS = products_num
    MAX_LOCATIONS = 0

    # filter by this product ids (no ids = no filter)
    PRODUCT_IDS_FILTER = []
    LOCATION_IDS_FILTER = [141, 20, 58, 174, 59]
    ###########

    # inititalize json rpc client
    env = Client(
        HOST,
        DATABASE,
        USERNAME,
        PASSWORD,
        PORT,
        protocol="json-rpcs" if PORT == 443 else "json-rpc",
    )

    # short access to odoo models
    PP = env["product.product"]
    SL = env["stock.location"]
    SQ = env["stock.quant"]
    SO = env["sale.order"]

    ##### API request #####

    # get list of products
    print("Get products...")
    # get IDs of available products (filter by ids if set else all products)
    product_ids = PP.search(
        [("id", "in", PRODUCT_IDS_FILTER)] if PRODUCT_IDS_FILTER else [], limit=MAX_PRODUCTS
    )
    # get values of all products for ids from previous step
    # structure is dict, where
    #  key is product_id
    #  values is dict like
    #  {
    #    'id': 0,
    #    'display_name': '',
    #    'default_code': '',
    #    'categ_id': [ 0, 'All / Materials' ],
    #    'qty_available: 0,
    #    'sale_ok': True,
    #  }
    product_datas = PP.read(
        product_ids,
        ["name", "default_code", "categ_id", "qty_available", "sale_ok"],
    )
    print(f"Found {len(product_datas)} products")

    # get locations
    print("Get locations...")
    # get IDs of locations (filter by ids if set else all products)
    loc_ids = SL.search(
        [("id", "in", LOCATION_IDS_FILTER)] if LOCATION_IDS_FILTER else [],
        limit=MAX_LOCATIONS,
    )
    # get values for all locations from previous step
    # result is list with item is dict like { 'id': 0, 'display_name': '' }
    loc_datas = SL.read(list(loc_ids), ["display_name"])
    print(f"Found {len(loc_datas)} locations")

    # collect quant ids
    # get IDs of all quants for our products and our locations
    # ignore quants with zero quantity (minor speed up)
    quant_ids = SQ.search(
        [
            ("product_id", "in", product_ids),
            ("location_id", "in", loc_ids),
            "|",
            ("quantity", "!=", 0.0),
            ("reserved_quantity", "!=", 0.0),
        ]
    )
    print(f"Need to process {len(quant_ids)} quants...")

    # init result as empty dict
    result = {}

    # copy products to result
    # extend with quantities at locations
    # init quantities as zeroes
    # structure is dict, where
    #  key is product_id
    #  values is dict like
    #  {
    #    'id': 0,
    #    'display_name': '',
    #    'default_code': '',
    #    'categ_id': [ 0, 'All / Materials' ],
    #    'sale_ok': True,
    #    'qty_available_at_location: dict[location_id] {
    #      'id': 0,
    #      'display_name': '',
    #      'qty_available: 0,
    #      'qty_reserved: 0,
    #    }
    #  }
    for product_data in product_datas:
        data = {**product_data.copy(), "qty_available_at_location": {}}
        for location_data in loc_datas:
            data["qty_available_at_location"][location_data["id"]] = {
                "id": location_data["id"],
                "display_name": location_data["display_name"],
                "qty_available": 0.0,
                "qty_reserved": 0.0,
            }
        result[product_data["id"]] = data

    # process quants by 1000 at once
    processed = 0
    for work_ids in batch(quant_ids, 10000):
        print(f"Processed {processed} quants of {len(quant_ids)}...")
        # request quants values
        for data in SQ.read(
                work_ids, ["product_id", "location_id", "quantity", "reserved_quantity"]
        ):
            product_id = data["product_id"][0]
            location_id = data["location_id"][0]
            # update quantity of product at location
            result[product_id]["qty_available_at_location"][location_id].update(
                {
                    "qty_available": data["quantity"],
                    "qty_reserved": data["reserved_quantity"],
                }
            )
            processed += 1

    print("Done")

    return result

def get_odoo_tmp_id(id_list):
    load_dotenv()
    HOST = environ.get("ODOO_HOSTNAME")
    PORT = int(environ.get("ODOO_PORT"))
    DATABASE = environ.get("ODOO_DATABASE")
    USERNAME = environ["ODOO_USERNAME"]
    PASSWORD = environ["ODOO_PASSWORD"]

    ################
    # limit queries - 0 is no limit

    MAX_LOCATIONS = 0

    # filter by this product ids (no ids = no filter)
    PRODUCT_IDS_FILTER = []
    LOCATION_IDS_FILTER = [141, 20, 58, 174, 59]
    ###########

    # inititalize json rpc client
    env = Client(
        HOST,
        DATABASE,
        USERNAME,
        PASSWORD,
        PORT,
        protocol="json-rpcs" if PORT == 443 else "json-rpc",
    )

    PP = env["product.product"]
    product_ids = PP.search_records([('id', 'in', id_list)])
    result = []
    for product_id in product_ids:
        result.append({'odoo_id': product_id.id, 'odoo_tmpl_id': product_id.product_tmpl_id.id})
        #
        # print(f'{product_id.id}\t{product_id.default_code}\t{product_id.name}'
        #       f'\t{product_id.categ_id.name}\t{product_id.product_tmpl_id.id}')
    return result




def odoo_api_get_products(products_num=1, categ_id=2):
    ################
    # limit queries - 0 is no limit
    MAX_PRODUCTS = products_num
    MAX_LOCATIONS = 0

    # filter by this product ids (no ids = no filter)
    PRODUCT_IDS_FILTER = []
    LOCATION_IDS_FILTER = [141, 20, 58, 174, 59]
    CATEGORY_IDS_FILTER = [categ_id]
    ###########

    try:
    # inititalize json rpc client
        env = Client(
            HOST,
            DATABASE,
            USERNAME,
            PASSWORD,
            PORT,
            protocol="json-rpcs" if PORT == 443 else "json-rpc",
        )

        # short access to odoo models
        PP = env["product.product"]

        ##### API request #####

        # get list of products
        print("Get products...")
        # get IDs of available products (filter by ids if set else all products)
        product_ids = PP.search(
            [("categ_id", "in", CATEGORY_IDS_FILTER)] if CATEGORY_IDS_FILTER else [], limit=MAX_PRODUCTS)
        
        # get values of all products for category ids from previous step
        # structure is dict, where
        #  key is product_id
        #  values is dict like
        #  {
        #    'id': 0,
        #    'display_name': '',
        #    'default_code': '',
        #    'categ_id': [ 0, 'All / Materials' ],
        #    'qty_available: 0,
        #    'sale_ok': True,
        #  }

        product_data = PP.read(product_ids, ["name", "default_code", "categ_id", "product_tmpl_id", "sale_ok"],)
        print(product_data)


        return product_data
    
    except Exception as e:
        print(f"SOME ERROR occurred in odoo_api_get_products(): {e}")
        product_data = None


# Get the quants from Odoo for the list of products and locations
# loc_ids default = 141 (AMPRU/Stock)
def odoo_api_get_products_quants(prod_list_ids, loc_ids=[141]):
    try:
    # inititalize json rpc client
        env = Client(
            HOST,
            DATABASE,
            USERNAME,
            PASSWORD,
            PORT,
            protocol="json-rpcs" if PORT == 443 else "json-rpc",
        )

        quant_ids = env["stock.quant"].search(
            [
                ("product_id", "in", prod_list_ids),
                ("location_id", "in", loc_ids),
            ]
        )
        print(f"Need to process {len(quant_ids)} quants...")
        print(f"------quant_ids: {quant_ids}")
        # init result as empty dict
        result = {}

        quants = env["stock.quant"].read(
                quant_ids, ["product_id", "location_id", "quantity", "reserved_quantity"])
        


        return quants

        # copy products to result
        # extend with quantities at locations
        # init quantities as zeroes
        # structure is dict, where
        #  key is product_id
        #  values is dict like
        #  {
        #    'id': 0,
        #    'display_name': '',
        #    'default_code': '',
        #    'categ_id': [ 0, 'All / Materials' ],
        #    'sale_ok': True,
        #    'qty_available_at_location: dict[location_id] {
        #      'id': 0,
        #      'display_name': '',
        #      'qty_available: 0,
        #      'qty_reserved: 0,
        #    }
        #  }


        # for product_data in product_datas:
        #     data = {**product_data.copy(), "qty_available_at_location": {}}
        #     for location_data in loc_datas:
        #         data["qty_available_at_location"][location_data["id"]] = {
        #             "id": location_data["id"],
        #             "display_name": location_data["display_name"],
        #             "qty_available": 0.0,
        #             "qty_reserved": 0.0,
        #         }
        #     result[product_data["id"]] = data

    except Exception as e:
        print(f"SOME ERROR occurred in odoo_api_get_products_quants(): {e}")
        product_data = None

# {'id': 17342, 'default_code': '0218010_MXP', 'categ_id': [4, 'All / Materials'], 'sale_ok': False, 'display_name': '[0218010_MXP] 0218010.MXP Предохранитель 10A 5.2x20 (аналог  021810_MXP)', 'qty_available': 577.0,
#  'qty_available_at_location':
# {141: {'id': 141, 'display_name': 'AMPRU/Stock', 'qty_available': 0.0, 'qty_reserved': 0.0},
# 58: {'id': 58, 'display_name': 'PS/Kits', 'qty_available': 0.0, 'qty_reserved': 0.0},
# 20: {'id': 20, 'display_name': 'PS/Prepair', 'qty_available': 107.0, 'qty_reserved': 0.0},
# 174: {'id': 174, 'display_name': 'SS/Stock/Market', 'qty_available': 0.0, 'qty_reserved': 0.0},
# 59: {'id': 59, 'display_name': 'SS/Stock/Edu', 'qty_available': 0.0, 'qty_reserved': 0.0}}}