class ParsedMessage:

    def __init__(self, text : str = None, images: list = [], id: int = None):
        self.text = text
        self.images = images
        self.id = id