from Parsers import TelegramParser, VKParser, WebParser
from Publishers import TelegramPublisher, VKtoTelegramPublisher, WebToTelegramPublisher
import telegram
import telegram.ext
from telegram.ext import MessageHandler
import asyncio
import vk
import aiohttp

to_id = -1001111111111
from_id = -1002222222222
telegram_token = "telegram_token"

vk_token = "vk_token"
vkVersion = "5.199"
vk_domain = "inshd"
vk_group_id = 112233445
group_access_token = "group_access_token"


telegram_application = (
    telegram.ext.Application.builder()
    .token(telegram_token)
    .get_updates_connection_pool_size(20)
    .build()
)


async def run_telegram_bot():

    telegram_parser = TelegramParser(telegram_application)

    telegram_publisher = TelegramPublisher(
        telegram_application, to_id, from_id, telegram_parser
    )

    telegram_application.add_handler(MessageHandler(None, telegram_parser.parse))

    telegram_parser.attach(telegram_publisher)

    await telegram_application.initialize()
    await telegram_application.updater.start_polling(
        allowed_updates=telegram.Update.ALL_TYPES
    )
    await telegram_application.start()

    async with aiohttp.ClientSession():
        while True:
            await asyncio.sleep(1)


async def run_vk_bot():

    vk_application = vk.API(access_token=group_access_token, v=vkVersion)
    long_poll_data = vk_application.groups.getLongPollServer(
        access_token=group_access_token, group_id=vk_group_id
    )

    server = long_poll_data["server"]
    key = long_poll_data["key"]
    ts = long_poll_data["ts"]
    wait = 1

    vk_parser = VKParser(vk_application, "toTelegramFromVK")
    vk_publisher = VKtoTelegramPublisher(
        vk_application, telegram_application, to_id, vk_parser
    )
    vk_parser.attach(vk_publisher)

    async with aiohttp.ClientSession() as session:
        last_response = None

        while True:
            async with session.get(
                f"{server}?act=a_check&key={key}&ts={ts}&wait={wait}"
            ) as response:

                response = await response.json()
                updates = response["updates"]
                if updates and last_response != response:
                    await vk_parser.parse(updates[-1])
                    last_response = response
                    await asyncio.sleep(1)


async def run_web_parsing():
    url = "https://edu.shd.ru/"
    last_post_id_file = "lastWebPostId"

    web_parser = WebParser(url, "toTelegramFromWeb")
    web_publisher = WebToTelegramPublisher(telegram_application, to_id, web_parser)

    while True:
        await web_parser.parse()

        with open(last_post_id_file, "r") as file:
            last_post_id = file.read().strip()

        if web_parser.message.id == last_post_id:
            await asyncio.sleep(1)
            continue
        else:
            await web_publisher.publish()
            with open(last_post_id_file, "w") as file:
                file.write(web_parser.message.id)
            await asyncio.sleep(1)


async def main():
    await asyncio.gather(run_telegram_bot(), run_vk_bot(), run_web_parsing())


try:
    asyncio.run(main())
except Exception:
    asyncio.run(main())