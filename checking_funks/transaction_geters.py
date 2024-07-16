import asyncio
import datetime as dt
import requests
import json
from typing import List, Dict

from aiohttp import ClientSession, ContentTypeError

from bot.additional_funks import exception_cather


@exception_cather
async def get_transactions_trc20(address:str, lasttime:dt.datetime) -> List[Dict]:
    async with ClientSession(trust_env=True) as session:
        # url = f'https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?'
        # params = {
        #     "sort": 'blockNumber',
        #     'limit': 10,
        # }
        # async with session.get(url=url, params=params) as response:
        #     result_json = await response.json(content_type=None)
        # return result_json["data"]
        url = f'https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?'
        # url = f'https://api.trongrid.io/v1/accounts/{address}/transactions?'
        params = {
            'min_timestamp': dt.datetime.timestamp(dt.datetime.now() - lasttime)*1000,
            'limit': 20,
            "only_confirmed": "True",
        }
        async with session.get(
                    url=url, 
                    params=params, 
                    headers={"accept": "application/json"}
                ) as response:
            result_js = await response.json()
    return result_js["data"]


@exception_cather
async def get_transactions_trx(address:str, lasttime:dt.datetime) -> List[Dict]:
    async with ClientSession(trust_env=True) as session:
        url = f'https://api.trongrid.io/v1/accounts/{address}/transactions/'
    #     params = {
    #         "sort": 'blockNumber',
    #         'limit': 10,
    #     }
    #     async with session.get(url=url, params=params) as response:
    #         result_json = await response.json(content_type=None)
    # return result_json["data"]
        params = {
            'min_timestamp': dt.datetime.timestamp(dt.datetime.now() - lasttime)*1000,
            'limit': 200,
            "only_confirmed": "True",
        }
        async with session.get(
                    url=url, 
                    params=params, 
                    headers={"accept": "application/json"}
                ) as response:
            result_js = await response.json()
    try:
        result_js = await response.json(content_type=None)
        return result_js["data"]
    except json.JSONDecodeError as e:
        text = await response.text()
        print(f'ERROR get_transactions_trx {e}  ; {text}')
        return None
    except Exception as e:
        print(f'ERROR  get_transactions_trx {e} {result_js}')
        return None
    return result_js["data"]


@exception_cather
async def get_transactions_eth(start_block, address):
    async with ClientSession(trust_env=True) as session:
        url = f'https://api.etherscan.io/api?'
        # params = {'module': 'account',
        #           'action': 'txlist',
        #           'address': address,
        #           'startblock': start_block - 1000,
        #           'endblock': 999999999,
        #           'apikey': 'JK2KNMVT98447KEDW4DWWPNJE32GPRBUJJ',
        #           }
        
        params = {'module': 'account',
                  'action': 'txlist',
                  'address': address,
                  'startblock': start_block - 100,
                  'endblock': 999999999,
                  'page': 1,
                  'offset': 200,
                  'sort': 'desc',
                  'apikey': 'JK2KNMVT98447KEDW4DWWPNJE32GPRBUJJ',
                  }
        result_json = {"result": "Max rate limit reached"}
        while result_json["result"] == 'Max rate limit reached':
            async with session.get(url=url, params=params) as response:
                try:
                    result_json = await response.json(content_type=None)
                except json.JSONDecodeError as e:
                    # Обработка ошибки декодирования JSON
                    text = await response.text()
                    print(f"Erroy get_transactions_eth {text}")
                    return
                except Exception as e:
                    # Обработка других возможных исключений
                    print(f"Erroy get_transactions_eth {e}")
                    return
            if not result_json["result"]:
                return
            if result_json["result"] == 'Max rate limit reached':
                await asyncio.sleep(1.1)
        return result_json["result"]


@exception_cather
async def get_transactions_erc20(start_block, address):
    async with ClientSession(trust_env=True) as session:
        url = f'https://api.etherscan.io/api?'
        params = {'module': 'account',
                  'action': 'tokentx',
                  'address': address,
                  "offset": 200,
                  'startblock': start_block - 100,
                  'endblock': 999999999,
                  'page': 1,
                  'sort': 'desc',
                  'apikey': 'JK2KNMVT98447KEDW4DWWPNJE32GPRBUJJ',
                  }
        result_json = {"result": "Max rate limit reached"}
        while result_json["result"] == 'Max rate limit reached':
            async with session.get(url=url, params=params) as response:
                try:
                    result_json = await response.json(content_type=None)
                except json.JSONDecodeError as e:
                    # Обработка ошибки декодирования JSON
                    text = await response.text()
                    print(f"Erroy get_transactions_erc20 {text}")
                    return
                except Exception as e:
                    # Обработка других возможных исключений
                    print(f"Erroy get_transactions_erc20 {e}")
                    return
            if not result_json["result"]:
                return
            if result_json["result"] == 'Max rate limit reached':
                await asyncio.sleep(1.1)
        return result_json["result"]


# @exception_cather
# async def get_transactions_bsc(start_block, address):
#     async with ClientSession(trust_env=True) as session:
#         url = f'https://api.bscscan.com/api?'
#         params = {'module': 'account',
#                   'action': 'txlist',
#                   'address': address,
#                   'startblock': start_block - 1000,
#                   'endblock': 999999999,
#                   'apikey': 'TW44YTZA76E14FMIQ6SMSKDMDS5CN2VKUH',
#                   }
#         result_json = {"result": "Max rate limit reached"}
#         while result_json["result"] == 'Max rate limit reached':
#             async with session.get(url=url, params=params) as response:
#                 result_json = await response.json(content_type=None)
#             if not result_json["result"]:
#                 return
#             if result_json["result"] == 'Max rate limit reached':
#                 await asyncio.sleep(1.1)
#         return result_json["result"]


# @exception_cather
# async def get_transactions_bep20(start_block, address):
#     async with ClientSession(trust_env=True) as session:
#         url = f'https://api.bscscan.com/api?'
#         params = {'module': 'account',
#                   'action': 'tokentx',
#                   'address': address,
#                   "offset": 100,
#                   'startblock': start_block - 1000,
#                   'endblock': 999999999,
#                   "sort": "asc",
#                   'apikey': 'TW44YTZA76E14FMIQ6SMSKDMDS5CN2VKUH',
#                   }
#         result_json = {"result": "Max rate limit reached"}
#         while result_json["result"] == 'Max rate limit reached':
#             async with session.get(url=url, params=params) as response:
#                 result_json = await response.json(content_type=None)
#             if not result_json["result"]:
#                 return
#             if result_json["result"] == 'Max rate limit reached':
#                 await asyncio.sleep(1.1)
#         return result_json["result"]


@exception_cather
async def get_transactions_btc(address):
    async with ClientSession(trust_env=True) as session:
        url = f'https://blockchain.info/rawaddr/{address}'
        params = {
            'limit': '50'
        }
        
        async with session.get(url=url, params=params) as response:
            print("статус запроса",response.status)
            try:
                result_json = await response.json()
            except ContentTypeError:
                
                if response.status == 502:
                    print('я скипнул')
                    return []
                elif response.status == 429: 
                    print('429!!!!!!!')
                    return []
                    
                elif response.status != 204:
                    result_json = await response.json(content_type=None)
                else:
                    print("хуевый запрос")
            except Exception as e: # тут нужна нормальная проверка 
                print("Error in func get_transactions_btc", e)
                
            try:
                result = result_json['txs']
                return result
            except KeyError as e:
                if result_json['error'] == 'not-found-or-invalid-arg':
                    print("Нет кошелька, желательно это отправлять пользователю ")
                return []
            
            # print(f"ПРОВЕРКА ИИИИ  {data}")
            # result_json = json.loads(data)

            
            # result_json = await response.json(content_type='text/html')
            # print(f'{result_json=}')
            # return result_json
