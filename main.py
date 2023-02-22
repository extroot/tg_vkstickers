import os
import argparse
from time import sleep

import vk_api
from telethon import TelegramClient, sync
from dotenv import load_dotenv


class Telegram:
    client: TelegramClient
    vk_api_: vk_api.VkApi
    vk_session: vk_api.vk_api.VkApiMethod
    interval: float
    emoji_interval: float = 0.1
    suffix: str
    prefix: str
    link_prefix: str
    saved_packs: dict[int: tuple[str, list[str]]] = dict()

    def __init__(self,
                 vk_token: str = None,
                 tg_api_id: int = None, tg_api_hash: str = None,
                 session_name: str = 'session_name',
                 suffix: str = None,
                 prefix: str = None,
                 interval: float = 1.0,
                 emoji_interval: float = 0.1,
                 ):
        if vk_token:
            self.init_vk(vk_token)
        if tg_api_id and tg_api_hash:
            self.init_telegram(tg_api_id, tg_api_hash, session_name)
        self.suffix = suffix or ''
        self.prefix = prefix or ''
        self.interval = interval
        self.emoji_interval = emoji_interval

    def __del__(self):
        if self.client:
            self.client.disconnect()

    def init_telegram(self, tg_api_id: int, tg_api_hash: str, session_name: str = 'session_name'):
        self.client = TelegramClient(session_name, tg_api_id, tg_api_hash)
        self.client.start()

    def init_vk(self, vk_token: str):
        self.vk_api_ = vk_api.VkApi(token=vk_token)
        self.vk_session = self.vk_api_.get_api()

    def create_pack(self, pack_id: int):
        self.__check_telegram()

        pack_name = self.__get_pack_name(pack_id)
        links = self.__get_links(pack_id)
        # print(f'Proceeding {pack_name} with {len(links)}')

        self.client.send_message('Stickers', '/newpack')
        self.client.send_message('Stickers', f'{pack_name} {self.suffix}')

        for link in links:
            self.client.send_file('Stickers', link)
            sleep(self.emoji_interval)
            self.client.send_message('Stickers', '😄')
            sleep(self.interval)

        self.client.send_message('Stickers', '/publish')
        self.client.send_message('Stickers', '/skip')
        self.client.send_message('Stickers', f'{self.prefix}_{pack_name.replace("-", "_")}')

    def create_packs(self, pack_ids: list[int]):
        """
        TODO: Transfer multiple sticker packs with pack_ids given.
        """
        pass

    def __proceed_vk_pack(self, pack_id: int) -> tuple[str, list[str]]:
        self.__check_vk()
        if pack_id in self.saved_packs:
            return self.saved_packs[pack_id]

        data = self.vk_session.store.getProducts(type="stickers", product_ids=pack_id, extended=1)['items'][0]
        out = (data['title'], [sticker['images'][4]['url'] for sticker in data['stickers']])
        return out

    def __get_links(self, pack_id: int) -> list[str]:
        return self.__proceed_vk_pack(pack_id)[1]

    def __get_pack_name(self, pack_id: int) -> str:
        return self.__proceed_vk_pack(pack_id)[0]

    def __check_vk(self):
        if not self.vk_session:
            raise ValueError("Vk session is not initialized")

    def __check_telegram(self):
        if not self.client:
            raise ValueError("Telegram client is not initialized")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transfer sticker pack from VK to Telegram')
    parser.add_argument('-env', action='store_true', help='load .env file', default=False)
    parser.add_argument('-pack_id', type=int, help='Pack ID to move', required=True)
    parser.add_argument('-i', '--interval', type=float, help='interval between messages to stickers bot', default=1.0)
    parser.add_argument('-ei', '--emoji_interval', type=float,
                        help='Interval between image and emoji sent to stickers bot', default=0.1)
    parser.add_argument('-suffix', type=str, help='suffix for sticker pack name', default='via tg_stickers')
    parser.add_argument('-prefix', type=str, help='prefix for sticker pack link', default='pack')

    parser.add_argument('-tg_api_id', '--ti', type=int, help='Telegram API ID')
    parser.add_argument('-tg_api_hash', '--th', type=str, help='Telegram API HASH')
    parser.add_argument('-session_name', '--sn', type=str, help='Telegram session name', default='session_name')
    parser.add_argument('-vk_token', '--vk', type=str, help='VK token')

    args = parser.parse_args()
    SUFFIX = args.suffix
    PREFIX = args.prefix
    INTERVAL = args.interval or 1.0
    EMOJI_INTERVAL = args.emoji_interval or 0.1
    pack_id_inp = args.pack_id

    if args.env:
        load_dotenv()
        VK_TOKEN = os.getenv("VK_TOKEN")
        TG_API_ID = os.getenv("TG_API_ID")
        TG_API_HASH = os.getenv("TG_API_HASH")

        if not VK_TOKEN or not TG_API_ID or not TG_API_HASH:
            raise ValueError("You must set VK_TOKEN, TG_API_ID and TG_API_HASH in .env file")
        TG_API_ID = int(TG_API_ID)
    else:
        VK_TOKEN = args.vk
        TG_API_ID = args.ti
        TG_API_HASH = args.th

    telegram = Telegram(
        suffix=SUFFIX,
        prefix=PREFIX,
        interval=INTERVAL,
        emoji_interval=EMOJI_INTERVAL
    )
    telegram.init_vk(VK_TOKEN)
    telegram.init_telegram(TG_API_ID, TG_API_HASH)
    telegram.create_pack(pack_id_inp)
