import asyncio

from aiohttp import ClientSession

from bot.additional_funks import exception_cather


@exception_cather
async def get_transactions_trc20(address):
    async with ClientSession(trust_env=True) as session:
        url = f'https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?'
        params = {
            "sort": 'blockNumber',
            'limit': 10,
        }
        async with session.get(url=url, params=params) as response:
            result_json = await response.json(content_type=None)
        return result_json["data"]


@exception_cather
async def get_transactions_trx(address):
    async with ClientSession(trust_env=True) as session:
        url = f'https://api.trongrid.io/v1/accounts/{address}/transactions/'
        params = {
            "sort": 'blockNumber',
            'limit': 10,
        }
        async with session.get(url=url, params=params) as response:
            result_json = await response.json(content_type=None)
    return result_json["data"]


@exception_cather
async def get_transactions_eth(start_block, address):
    async with ClientSession(trust_env=True) as session:
        url = f'https://api.etherscan.io/api?'
        params = {'module': 'account',
                  'action': 'txlist',
                  'address': address,
                  'startblock': start_block - 1000,
                  'endblock': 999999999,
                  'apikey': 'JK2KNMVT98447KEDW4DWWPNJE32GPRBUJJ',
                  }
        result_json = {"result": "Max rate limit reached"}
        while result_json["result"] == 'Max rate limit reached':
            async with session.get(url=url, params=params) as response:
                result_json = await response.json(content_type=None)
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
                  "offset": 100,
                  'startblock': start_block - 1000,
                  'endblock': 999999999,
                  "sort": "asc",
                  'apikey': 'JK2KNMVT98447KEDW4DWWPNJE32GPRBUJJ',
                  }
        result_json = {"result": "Max rate limit reached"}
        while result_json["result"] == 'Max rate limit reached':
            async with session.get(url=url, params=params) as response:
                result_json = await response.json(content_type=None)
            if not result_json["result"]:
                return
            if result_json["result"] == 'Max rate limit reached':
                await asyncio.sleep(1.1)
        return result_json["result"]


@exception_cather
async def get_transactions_bsc(start_block, address):
    async with ClientSession(trust_env=True) as session:
        url = f'https://api.bscscan.com/api?'
        params = {'module': 'account',
                  'action': 'txlist',
                  'address': address,
                  'startblock': start_block - 1000,
                  'endblock': 999999999,
                  'apikey': 'TW44YTZA76E14FMIQ6SMSKDMDS5CN2VKUH',
                  }
        result_json = {"result": "Max rate limit reached"}
        while result_json["result"] == 'Max rate limit reached':
            async with session.get(url=url, params=params) as response:
                result_json = await response.json(content_type=None)
            if not result_json["result"]:
                return
            if result_json["result"] == 'Max rate limit reached':
                await asyncio.sleep(1.1)
        return result_json["result"]


@exception_cather
async def get_transactions_bep20(start_block, address):
    async with ClientSession(trust_env=True) as session:
        url = f'https://api.bscscan.com/api?'
        params = {'module': 'account',
                  'action': 'tokentx',
                  'address': address,
                  "offset": 100,
                  'startblock': start_block - 1000,
                  'endblock': 999999999,
                  "sort": "asc",
                  'apikey': 'TW44YTZA76E14FMIQ6SMSKDMDS5CN2VKUH',
                  }
        result_json = {"result": "Max rate limit reached"}
        while result_json["result"] == 'Max rate limit reached':
            async with session.get(url=url, params=params) as response:
                result_json = await response.json(content_type=None)
            if not result_json["result"]:
                return
            if result_json["result"] == 'Max rate limit reached':
                await asyncio.sleep(1.1)
        return result_json["result"]


@exception_cather
async def get_transactions_btc(address):
    async with ClientSession(trust_env=True) as session:
        url = f"https://btcscan.org/api/address/{address}/txs"
        async with session.get(url=url) as response:
            result_json = await response.json()
            return result_json
