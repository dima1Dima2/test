from abc import ABC, abstractmethod
import os
from telegram.ext import ContextTypes, Application
from telegram import Update as tgUpdate
from Observer import Observer
from ParsedMessage import ParsedMessage
import aiofiles
from bs4 import BeautifulSoup
import aiohttp
from ParsedMessage import ParsedMessage
from File import File

class Parser(ABC):

    @abstractmethod
    def __init__(self):
        Observer.__init__(self)
        self.message = ParsedMessage("", [])

    @abstractmethod
    def parse(self):
        pass

    async def getResponseContent(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()


class TelegramParser(Parser, Observer):

    def __init__(self, application: Application):
        super().__init__()
        self.application = application

    async def parse(self, update: tgUpdate, context: ContextTypes.user_data):
        self.message = update.effective_message

        await self.invoke()
        return self.message


class VKParser(Parser, Observer):

    def __init__(self, application: Application, directory):
        super().__init__()
        self.application = application
        self.directory = directory

    async def parse(self, update):

        json_object = update["object"]

        media = []

        for index, attachment in enumerate(json_object["attachments"]):

            fileUrl = attachment["photo"]["orig_photo"]["url"]

            file = await self.getResponseContent(fileUrl)

            file_location = f"{index}"

            file_location = await File.createFile(self.directory, file, f'{index}')

            media.append(file_location)

        self.message.text = json_object["text"]
        self.message.images = media

        await self.invoke()
        return self.message


class WebParser(Parser):

    def __init__(self, url: str, directory: str):
        super().__init__()
        self.url = url
        self.directory = directory

    async def parse(self):
        response = await self.getResponseContent(self.url)

        soup_content = BeautifulSoup(response, "html.parser").find(
            "div", class_="art-content"
        )

        new_post = soup_content.find("div", class_="leading-0")

        article = new_post.find("div", class_="art-article")

        message = ""
        strong = article.find("strong")
        for element in article:
            if element.find("strong"):
                continue
            message += element.text + " "

        images = article.find_all("img")

        id_element = new_post.find("a", class_="art-button").get("href")

        id_start_string_position = id_element.find("id=")
        id_end_string_position = (
            id_element[id_start_string_position:-1].find(":") + id_start_string_position
        )
        id_element = id_element[id_start_string_position:id_end_string_position]
        id = id_element[id_element.find("=") + 1 : -1]
        self.message.id = id

        media = []

        for index, image in enumerate(images):
            image = image.get("src")

            image = await self.getResponseContent(self.url + image)

            file_location = await File.createFile(self.directory, image, f'{index}')

            media.append(file_location)

        self.message.text = strong.text + "\n" + "\n"
        for text in message:
            self.message.text += text
        self.message.images = media

        return self.message