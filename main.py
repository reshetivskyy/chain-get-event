# import librarys
import telebot
import json
import requests
import time
import threading

# create telegram bot object
TOKEN = ""
bot = telebot.TeleBot(TOKEN)

with open('chats.txt', 'r') as file:
    chats = file.read().splitlines()

# set API keys
contract_address = ""
moralis_api_key = ""

# handle command /notify
@bot.message_handler(commands=['notify'])
def handle_notify(message):
    global chats
    if message.chat.id in chats:
        bot.send_message(message.chat.id, 'Bot alrealy in list')
    else:
        chats.append(message.chat.id)
        bot.send_message(message.chat.id, "Hello! Chat added to list!")

def check():
    time.sleep(3)
    transfers = requests.get(
        f'https://deep-index.moralis.io/api/v2.2/nft/{contract_address}/transfers?chain=bsc&format=decimal',
        headers={'x-api-key': moralis_api_key}
    ).json()['result']
    last_id = transfers[0]['token_id']

    while True:
        # get token ids
        transfers = requests.get(
            f'https://deep-index.moralis.io/api/v2.2/nft/{contract_address}/transfers?chain=bsc&format=decimal',
            headers={'x-api-key': moralis_api_key}
        ).json()['result']
        print(transfers)
        latest_mint = transfers[0]

        # if latest block equals to latest block from API request: wait and skip
        token_id = latest_mint['token_id']
        if last_id == token_id:
            time.sleep(150)
            continue

        # get info
        price = round(int(latest_mint['value']) / (10 ** 18), 5)
        mint_hash = latest_mint['transaction_hash']

        # get metadata
        meta_data = requests.get(
                        f'https://api.bnbutton.io/api/meta/{token_id}'
                    ).json()
        print(meta_data)

        # if error in metadata request: it's owner mint
        if meta_data.__contains__('error'):
            text = f'Owner Mint #{token_id}'
            rarity = 'None'
        else: # else get info from metadata
            name = meta_data['name']
            rarity = meta_data['attributes'][0]['value']
            text = f'<b>NEW Button!</b>\n{name}\n{rarity} for {price} BNB (usdt)'

        text += f'\n<a href="https://t.me/click_ann">Ann channel</a> | <a href="https://t.me/click_official_group">Click group</a>\n<a href="https://bscscan.com/tx/{mint_hash}">Transaction link</a>'
        print(text)

        try:
            for chat in chats:
                with open(f'photos/{rarity.lower()}.png', 'rb') as photo:
                    bot.send_photo(chat, photo, text, parse_mode='HTML')
        except FileNotFoundError:
            for chat in chats:
                bot.send_message(chat, text, parse_mode='HTML')

        # update last id
        last_id = latest_mint['token_id']

# start 2 funcs (init script)
if __name__ == "__main__":
    check_func = threading.Thread(target=check)
    polling_func = threading.Thread(target=lambda: bot.polling(none_stop=True))

    check_func.start()
    polling_func.start()

    check_func.join()
    polling_func.join()