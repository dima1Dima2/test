from abc import ABC, abstractmethod
import os
from telegram import InputMediaPhoto
from telegram.ext import Application, ExtBot
from Parsers import Parser
from Observer import Subscriber
import vk
import aiofiles


class Publisher(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def publish(self):
        pass


class TelegramPublisher(Publisher, Subscriber):

    def __init__(
        self,
        application: Application,
        to_id: int | str,
        from_id: int | str,
        parser: Parser,
    ):
        self.application = application
        self.to_id = to_id
        self.from_id = from_id
        self.parser = parser
        Subscriber.__init__(self, self.publish)

    async def publish(self):
        bot: ExtBot = self.application.bot
        await bot.forward_message(self.to_id, self.from_id, self.parser.message.id)


class VKtoTelegramPublisher(Publisher, Subscriber):

    def __init__(
        self,
        API: vk.API,
        telegram_application: Application,
        to_id: int | str,
        parser: Parser,
    ):
        self.vk = API
        self.telegram_application = telegram_application
        self.to_id = to_id
        self.parser = parser
        Subscriber.__init__(self, self.publish)

    async def publish(self):
        bot: ExtBot = self.telegram_application.bot

        if self.parser.message.images:
            media = []

            for filePath in self.parser.message.images:
                async with aiofiles.open(filePath, "rb") as file:
                    photo = InputMediaPhoto(await file.read())
                    media.append(photo)

            await bot.send_media_group(
                self.to_id, media=media, caption=self.parser.message.text
            )

        else:
            await bot.send_message(self.to_id, text=self.parser.message.text)


class WebToTelegramPublisher(Publisher, Subscriber):

    def __init__(
        self,
        telegram_application: Application,
        to_id: int | str,
        parser: Parser,
    ):
        self.telegram_application = telegram_application
        self.to_id = to_id
        self.parser = parser
        Subscriber.__init__(self, self.publish)

    async def publish(self):
        bot: ExtBot = self.telegram_application.bot

        if self.parser.message.images:
            media = []

            for filePath in self.parser.message.images:
                async with aiofiles.open(filePath, "rb") as file:
                    photo = InputMediaPhoto(await file.read())
                    media.append(photo)

            await bot.send_media_group(
                self.to_id, media=media, caption=self.parser.message.text
            )

        else:
            await bot.send_message(self.to_id, text=self.parser.message.text)