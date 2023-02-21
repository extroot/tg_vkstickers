
# VK to Telegram sticker pack transfer tool

## Description

This tool allows you to transfer stickers from VK to Telegram. It uses VK API to get stickers and Telethon MTProto library to upload them to your account.

## Installation

```bash
git clone https://github.com/extroot/tg_vkstickers
cd tg_vkstickers

# Install dependencies
pip install -r requirements.txt
```

## Usage
```bash
$ python main.py -h
options:
  -h, --help            show this help message and exit
  -env                  load .env file
  -pack_id PACK_ID      Pack ID to move
  -interval INTERVAL    interval between messages to stickers bot
  -suffix SUFFIX        suffix for sticker pack name
  -tg_api_id TI, --ti TI
                        Telegram API ID
  -tg_api_hash TH, --th TH
                        Telegram API HASH
  -session_name SN, --sn SN
                        Telegram session name
  -vk_token VK, --vk VK
                        VK token

```


## TODO
- [ ] Add support for multiple packs
- [ ] Add support for automatic pack id detection from link
- [ ] Add logging