import os
import aiofiles

class File:

    @classmethod
    async def createFile(self, directory: str, file: bytes, name: str):
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_location = os.path.join(directory, name)

        async with aiofiles.open(file_location, "wb") as aioFile:
            await aioFile.write(file)

        return file_location