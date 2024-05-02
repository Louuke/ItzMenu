import re

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import itzmenu.util.image as image
from itzmenu.jobs import process_image, fetch_menu
from dataclasses import dataclass
from enum import StrEnum


class Type(StrEnum):

    INTERVAL = '--interval'
    PRELOAD = '--preload'
    VALUE = ''
    EOL = 'EOL'

    def __str__(self):
        return f'{self.__class__.__name__}.{self.name}'

    @classmethod
    def str2type(cls, value: str):
        types = [getattr(cls, attr) for attr in dir(cls) if attr.isupper()]
        for t in types:
            if t.value == value:
                return t
        return Type.VALUE


@dataclass
class Token:

    type: Type
    value: str = ''


class Tokenizer:

    def __init__(self, args: list[str]):
        self.__items = self.__read(args)
        self.__current = 0

    def __iter__(self):
        self.__current = 0
        return self

    @staticmethod
    def __read(args: list[str]) -> list[Token]:
        if len(args) > 0 and re.search(r'^.+\.py$', args[0]) is not None:
            args.pop(0)
        tokens = [Token(Type.str2type(value), value) for value in args]
        tokens.append(Token(Type.EOL))
        return tokens

    def __next__(self) -> Token:
        if self.__current < len(self.__items):
            result = self.__items[self.__current]
            self.__current += 1
            return result
        else:
            raise StopIteration


class Parser:

    def __init__(self, args: list[str]):
        self.__tokenizer = Tokenizer(args)
        self.__scheduler = AsyncIOScheduler()

    async def execute(self):
        await self.__preload()
        await fetch_menu()
        await self.__interval()

    async def __preload(self):
        parser = iter(self.__tokenizer)
        while (token := next(parser)).type is not Type.EOL:
            if token.type is Type.PRELOAD:
                while (value := next(parser)).type is Type.VALUE:
                    if re.match(r'^([A-Z]:)?[a-zA-Z0-9\\/_-]+\.jpg$', value.value) is not None:
                        await process_image(image.load_image(value.value))

    async def __interval(self):
        parser = iter(self.__tokenizer)
        while (token := next(parser)).type is not Type.EOL:
            if token.type is Type.INTERVAL:
                if (value := next(parser)).type is Type.VALUE:
                    self.__scheduler.add_job(fetch_menu, 'interval', seconds=int(value.value))
                    self.__scheduler.start()
                else:
                    raise ValueError(f'Expected value but got {value.type}')
