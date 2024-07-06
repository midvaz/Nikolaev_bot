import asyncio
import time
import traceback
import json
import datetime as dt

from aiogram import types
from aiogram.utils.markdown import hlink
from aiohttp import ClientSession
from sqlalchemy import select, insert, delete, desc

from bot.additional_funks import send_alert_message, send_message_by_url
from bot.resources import chains
from db.accessor import session_maker, engine
from db.models import *
from collections import defaultdict

from checking_funks.transaction_geters import *

BLOCK_ETH=16011943
BLOCK_BSC=23408593

async def checking(message_id: id):
    # получение id для отправки сообщения
    async with session_maker() as session:
        user = await session.get(Users, message_id)
    chat_id = user.chat_id
    # инициализация словаря времени последней транзакции
    last_transactions_time = defaultdict(
        lambda: time.mktime(datetime.datetime.now().timetuple())
    )
    
    block_number_tasks = [
        asyncio.create_task(get_block_number_eth(BLOCK_ETH)),
        asyncio.create_task(get_block_number_bsc(BLOCK_BSC))
    ]
    start_block_eth, start_block_bsc = await asyncio.gather(*block_number_tasks)
    num_loop = 0
    count = 0
    
    while True:
        last_time = dt.timedelta(seconds=60)
        count += 1
        # print(count)
        async with session_maker() as session:
            make_requests = (await session.get(TrackingFlags, user.user_id)).flag
            if not make_requests: return
            addresses_querry = select(Wallets).where(Wallets.user == user.user_id)
            addresses = (await session.execute(addresses_querry)).scalars().all()
            tasks = []
            wallets_type = []
            for address in addresses:
                try:
                    if address.chain == "ETH":
                        tasks.append(asyncio.create_task(get_transactions_eth(start_block_eth, address.wallet)))
                        wallets_type.append({"chain": "ETH", "address": (address.wallet, "ETH")})
                        tasks.append(asyncio.create_task(get_transactions_erc20(start_block_eth, address.wallet)))
                        wallets_type.append({"chain": "ERC20", "address": (address.wallet, "ERC20")})
                    elif address.chain == "BTC":
                        tasks.append(asyncio.create_task(get_transactions_btc(address.wallet)))
                        wallets_type.append({"chain": "BTC", "address": (address.wallet, "BTC")})
                    elif address.chain == "BSC":
                        tasks.append(asyncio.create_task(get_transactions_bsc(start_block_bsc, address.wallet)))
                        wallets_type.append({"chain": "BSC", "address": (address.wallet, "BSC")})
                        tasks.append(asyncio.create_task(get_transactions_bep20(start_block_bsc, address.wallet)))
                        wallets_type.append({"chain": "BEP20", "address": (address.wallet, "BEP20")})
                    elif address.chain == "TRC":
                        tasks.append(asyncio.create_task(get_transactions_trx(address.wallet, last_time)))
                        wallets_type.append({"chain": "TRX", "address": (address.wallet, "TRX")})
                        tasks.append(asyncio.create_task(get_transactions_trc20(address.wallet, last_time)))
                        wallets_type.append({"chain": "TRC20", "address": (address.wallet, "TRC20")})
                except BaseException as e:
                    print(f"yyyyyyyy {address}  \n {e}")
                    send_message_by_url(address)
                    send_message_by_url(traceback.format_exc())
            print(f'{tasks=}')
            if not tasks:
                print('not tasks')
                await asyncio.sleep(30)
                continue
                
            wallets = await asyncio.gather(*tasks)
            for i, transactions in enumerate(wallets):
                try:
                    if (transactions is None) or (len(transactions) == 0):
                        print(f'(transactions is None) or (len(transactions) == 0)\n{transactions=}\n')
                        continue
                    else: 
                        print(f"{transactions=}")
                    if wallets_type[i]["chain"] == "ETH":
                        last_transaction_time = await process_transactions_eth(
                            transactions,
                            last_transactions_time[
                                wallets_type[i]["address"]
                            ],
                            chat_id,
                            wallets_type[i]["address"][0]
                        )
                        
                    elif wallets_type[i]["chain"] == "ERC20":
                        last_transaction_time = await process_transactions_erc20(
                            transactions,
                            last_transactions_time[
                                wallets_type[i]["address"]
                            ],
                            chat_id,
                            wallets_type[i]["address"][0]
                        )
                        
                    elif wallets_type[i]["chain"] == "BTC":
                        last_transaction_time = await process_transactions_btc(
                            transactions, 
                            last_transactions_time[
                                wallets_type[i]["address"]
                            ],
                            chat_id,
                            wallets_type[i]["address"][0]
                        )
                        
                    elif wallets_type[i]["chain"] == "BSC":
                        last_transaction_time = await process_transactions_bsc(
                            transactions, 
                            last_transactions_time[
                                wallets_type[i]["address"]
                            ],
                            chat_id,
                            wallets_type[i]["address"][0]
                        )
                        
                    elif wallets_type[i]["chain"] == "BEP20":
                        last_transaction_time = await process_transactions_bep20(
                            transactions, 
                            last_transactions_time[
                                wallets_type[i]["address"]
                            ],
                            chat_id,
                            wallets_type[i]["address"][0]
                        )
                        
                    elif wallets_type[i]["chain"] == "TRX":
                        last_transaction_time = await process_transactions_trx(
                            transactions, 
                            last_transactions_time[
                                wallets_type[i]["address"]
                            ],
                            chat_id,
                            wallets_type[i]["address"][0]
                        )
                        
                    elif wallets_type[i]["chain"] == "TRC20":
                        last_transaction_time = await process_transactions_trc20(
                            transactions, 
                            last_transactions_time[
                                wallets_type[i]["address"]
                            ],
                            chat_id,
                            wallets_type[i]["address"][0]
                        )
                    last_transactions_time[wallets_type[i]["address"]] = last_transaction_time
                    
                except BaseException as e:
                    print(f"rrrrrr {address}  \n {e}")
                    send_message_by_url(transactions)
                    send_message_by_url(traceback.format_exc())
            if num_loop == 10:
                for i in last_transactions_time:
                    last_transactions_time[i] = time.mktime(datetime.datetime.now().timetuple())
            if num_loop == 60:
                block_number_tasks = [
                    asyncio.create_task(get_block_number_eth(16011943)),
                    asyncio.create_task(get_block_number_bsc(23408593))
                ]
                start_block_eth, start_block_bsc = await asyncio.gather(*block_number_tasks)
                num_loop = 0
            
            num_loop += 1
        await asyncio.sleep(60)
        print('Количество проходок =',count)
            # time.sleep(30)



async def get_block_number_eth(last_block):
    try:
        async with ClientSession(trust_env=True) as session:
            # это какой-то сайт обозреватель прошедших транзаций в данной деньгах
            url = f'https://api.etherscan.io/api?'
            low = last_block
            high = 999999999

            params = {"module": "block",
                      "action": "getblockreward",
                      "blockno": round((high + low) / 2),
                      # что за код, хуй пойми
                      'apikey': 'JK2KNMVT98447KEDW4DWWPNJE32GPRBUJJ',
                      }
            while high - 5 > low:
                async with session.get(url=url, params=params) as response:
                    result_json = await response.json(content_type=None)
                    if int(result_json["status"]):
                        low = round((high + low) / 2)
                    else:
                        high = round((high + low) / 2)
                    params["blockno"] = round((high + low) / 2)
            return low
    except BaseException as e:
        print(e)
        return last_block


async def get_block_number_bsc(last_block):
    try:
        async with ClientSession(trust_env=True) as session:
            url = f'https://api.bscscan.com/api?'
            low = last_block
            high = 999999999

            params = {
                "module": "block",
                "action": "getblockreward",
                "blockno": round((high + low) / 2),
                'apikey': 'TW44YTZA76E14FMIQ6SMSKDMDS5CN2VKUH',
            }
            while high - 1 > low:
                async with session.get(url=url, params=params) as response:
                    result_json = await response.json(content_type=None)
                    if int(result_json["status"]):
                        low = round((high + low) / 2)
                    else:
                        high = round((high + low) / 2)
                    params["blockno"] = round((high + low) / 2)
                    await asyncio.sleep(0.2)
            return low
    except BaseException as e:
        print(e)
        return last_block


async def process_transactions_eth(transactions, last_transaction_time, chat_id, address):
    for t in transactions[::-1]:
        if int(t["timeStamp"]) > last_transaction_time:
            f = t["from"]
            to = t["to"]
            value = int(t["value"]) / 10e17
            text = hlink('Link to blockchain', "https://etherscan.io/tx/" + t["hash"])
            await send_alert_message(
                chat_id, 
                address.lower(), 
                f.lower(), 
                to.lower(), 
                value, 
                "ETH ETH",
                text,
                0.00001,
                writing_address=address
            )
        else:
            break
    return int(transactions[-1]["timeStamp"])


async def process_transactions_erc20(transactions, last_transaction_time, chat_id, address):
    for t in transactions[::-1]:
        if int(t["timeStamp"]) > last_transaction_time:
            f = t["from"]
            to = t["to"]
            value = int(t["value"]) / (10 ** int(t["tokenDecimal"]))
            t_name, t_symbol = t["tokenName"], t["tokenSymbol"]
            text = hlink('Link to blockchain', "https://etherscan.io/tx/" + t["hash"])
            contract = t["contractAddress"]
            await send_alert_message(
                chat_id, 
                address.lower(), 
                f.lower(), 
                to.lower(), 
                value, 
                f"{t_symbol} ERC20",
                text, 
                0.1, 
                writing_address=address,contract=contract
            )
        else:
            break
    return int(transactions[-1]["timeStamp"])


async def process_transactions_btc(transactions, last_transaction_time, chat_id, address):
    have_updates = False
    for i, t in enumerate(transactions):
        if t["status"]["confirmed"]:
            t_time = int(t["status"]["block_time"])
            if not have_updates:
                first_confirmed_transaction = i
            have_updates = True
        else:
            continue
        if t_time > last_transaction_time:
            value = 0
            is_output_trans = False
            for vin in t["vin"]:
                if vin["prevout"]["scriptpubkey_address"] == address:
                    value = vin["prevout"]["value"] / 10e7
                    is_output_trans = True
            for vout in t["vout"]:
                if vout["scriptpubkey_address"] == address:
                    value = vout["value"] / 10e7
            f = []
            if is_output_trans:
                for vout in t["vout"]:
                    f.append(vout["scriptpubkey_address"])
            else:
                for vin in t["vin"]:
                    f.append(vin["prevout"]["scriptpubkey_address"])
            f = "\n".join(f)
            to = address
            if is_output_trans:
                f, to = to, f
            text = hlink('Link to blockchain',
                         "https://www.blockchain.com/explorer/transactions/btc/" + t["txid"])
            await send_alert_message(
                chat_id, address, f, 
                to, value, 
                "BTC", text, 0.001,
                writing_address=address
            )
        else:
            break
    if have_updates:
        return int(transactions[first_confirmed_transaction]["status"]["block_time"])
    else:
        return last_transaction_time


async def process_transactions_bsc(transactions, last_transaction_time, chat_id, address):
    for t in transactions[::-1]:
        if int(t["timeStamp"]) > last_transaction_time:
            f = t["from"]
            to = t["to"]
            value = int(t["value"]) / 10e17
            text = hlink('Link to blockchain', "https://bscscan.com/tx/" + t["hash"])
            await send_alert_message(
                chat_id, address.lower(), 
                f.lower(), to.lower(), 
                value, f"BSC BSC", 
                text, 0.1, writing_address=address
            )
        else:
            break
    return int(transactions[-1]["timeStamp"])


async def process_transactions_bep20(transactions, last_transaction_time, chat_id, address):
    for t in transactions[::-1]:
        if int(t["timeStamp"]) > last_transaction_time:
            f = t["from"]
            to = t["to"]
            value = int(t["value"]) / (10 ** int(t["tokenDecimal"]))
            t_name, t_symbol,t_contract = t["tokenName"], t["tokenSymbol"],t["contractAddress"]
            text = hlink('Link to blockchain', "https://bscscan.com/tx/" + t["hash"])
            await send_alert_message(
                chat_id, address.lower(), 
                f.lower(), to.lower(), 
                value, f"{t_symbol} BEP20",text, 0.1, 
                writing_address=address,contract=t_contract
            )
        else:
            break
    return int(transactions[-1]["timeStamp"])


async def get_trx_tansaction_data(hash, attempt_number):
    try:
        async with ClientSession(trust_env=True) as session:
            url = f'https://apilist.tronscan.org/api/transaction-info?hash={hash}'
            async with session.get(url=url) as response:
                result_json = await response.json(content_type=None)
        return result_json
    except:
        if attempt_number < 5:
            print(datetime.datetime.now(), traceback.format_exc(), sep='\n')
            return await get_trx_tansaction_data(hash, attempt_number + 1)
        else:
            return None


async def process_transactions_trx(transactions, last_transaction_time, chat_id, address):
    print(f"_______________________ {len(transactions)}")
    for i in range(len(transactions)):
        # print(f'--------------------------------------sss{i} \n {json.dumps(transactions[i], indent=4)}')
        # TransferAssetContract  TriggerSmartContract
        # transactions[i]["raw_data"]["contract"][0]["type"] != 'TriggerSmartContract' and
        #  int(transactions[i]["block_timestamp"]) / 1000 >= \
        #         last_transaction_time
        ti = int(transactions[i]["block_timestamp"]) / 1000 >= last_transaction_time
        if  True:
            transaction_data = await get_trx_tansaction_data(transactions[i]["txID"], 0)
            if transaction_data is None or 'ownerAddress' not in transaction_data.keys():
                print(transactions)
                print(transaction_data)
                print(last_transaction_time)
                continue
                # break
            
            f = transaction_data['ownerAddress']
            to = transaction_data['toAddress']
            try:
                value = int(transactions[i]["raw_data"]["contract"][0]["parameter"]["value"]["amount"]) / 10e5
                f = int(transactions[i]["raw_data"]["contract"][0]["parameter"]["value"]["amount"]) / 10e5
                # print(f'ура1 {ti} {transactions[i]["raw_data"]["contract"][0]["parameter"]["value"]["amount"]}')
            except:
                # print(json.dumps(t, indent=4))
                # print(f'ура2 {ti} {transactions[i]["raw_data"]["contract"][0]["parameter"]["value"]["data"]}')
                f = transactions[i]["raw_data"]["contract"][0]["parameter"]["value"]["data"]
                value = int(transactions[i]["raw_data"]["contract"][0]["parameter"]["value"]["data"][72:], 16) / 1e6
            # send_message_by_url(f"проверка {f}  \n {value}")
            text = hlink('Link to blockchain', "https://tronscan.org/#/transaction/" + transactions[i]["txID"])
            await send_alert_message(
                chat_id, address, 
                f, to, value, "TRX TRX", 
                text, 0.1
            )
        else:
            print(f'--------------------------------------sss{i} \n {json.dumps(transactions[i], indent=4)}')
            continue
            # break
    # for t in transactions:
    #     # print(f'--------------------------------------sss \n {json.dumps(t, indent=4)}')
    #     # что нахуй за числа 1000 и тд ?
    #     # TransferAssetContract
    #     # if t["raw_data"]["contract"][0]["type"] != 'TriggerSmartContract' and int(t["block_timestamp"]) / 1000 > \
    #     #         last_transaction_time:
    #     # print(f'{t["block_timestamp"]}  {last_transaction_time} \n {json.dumps(t, indent=4)}')
    #     if t["raw_data"]["contract"][0]["type"] != 'TriggerSmartContract' and int(t["block_timestamp"]) / 1000 >= \
    #             last_transaction_time:
    #     # if t["raw_data"]["contract"][0]["type"] != 'TransferAssetContract' :
    #         transaction_data = await get_trx_tansaction_data(t["txID"], 0)
    #         if transaction_data is None or 'ownerAddress' not in transaction_data.keys():
    #             print(transactions)
    #             print(transaction_data)
    #             print(last_transaction_time)
    #             break
            
    #         f = transaction_data['ownerAddress']
    #         to = transaction_data['toAddress']
    #         try:
    #             value = int(t["raw_data"]["contract"][0]["parameter"]["value"]["amount"]) / 10e5
    #             print(f'ура1 {t["raw_data"]["contract"][0]["parameter"]["value"]["amount"]}')
    #         except:
    #             # print(json.dumps(t, indent=4))
    #             print(f'ура2 {t["raw_data"]["contract"][0]["parameter"]["value"]["data"]}')
    #             value = int(t["raw_data"]["contract"][0]["parameter"]["value"]["data"][72:], 16) / 1e6
    #         text = hlink('Link to blockchain', "https://tronscan.org/#/transaction/" + t["txID"])
    #         await send_alert_message(
    #             chat_id, address, 
    #             f, to, value, "TRX TRX", 
    #             text, 0.1
    #         )
    #     else:
    #         break
    
    # print(json.dumps(transactions, indent=4))

    print(f"--------------------\n{transactions=}")
    return int(transactions[0]["block_timestamp"]) / 1000


async def process_transactions_trc20(transactions, last_transaction_time, chat_id, address):
    for t in transactions:
        if int(t["block_timestamp"]) / 1000 > last_transaction_time:
            f = t['from']
            to = t["to"]
            value = int(t["value"]) / (10 ** int(t["token_info"]["decimals"]))
            t_name, t_symbol, t_contract = t["token_info"]["name"], t["token_info"]["symbol"], t["token_info"]["address"]
            text = hlink('Link to blockchain', "https://tronscan.org/#/transaction/" + t["transaction_id"])
            await send_alert_message(
                chat_id, address, f, to, 
                value, f"{t_symbol} TRC20", 
                text, 0.1, contract=t_contract
            )
        else:
            break
    return int(transactions[0]["block_timestamp"]) / 1000
