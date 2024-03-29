import json
import os
from pathlib import Path
import uuid
import asyncio


class Config:
    """
    The "Config" object. Internally based on ``json``.

    All commands that modify the Config file will prompt the file to be
        flushed to disk using async
    """

    def __init__(self, name: Path, **options):
        self.name = name

        self.loop = options.pop('loop') #, asyncio.get_event_loop())
        self.lock = asyncio.Lock()
        if options.pop('load_later', False):
            self.loop.create_task(self.load())
        else:
            self.load_from_file()

    def load_from_file(self):
        """
        Load config from file
        """
        try:
            with self.name.open("r", encoding="utf-8") as config_file:
                self._db = json.load(config_file)
        except FileNotFoundError:
            self._db = {}

    async def load(self):
        """
        Load config from disk using async loop
        """
        async with self.lock:
            await self.loop.run_in_executor(None, self.load_from_file)

    def _dump(self):
        """
        Dump config file to disk while in use
        """
        temp = f"{self.name}-{uuid.uuid4()}.tmp"
        with open(temp, 'w', encoding='utf-8') as tmp:
            json.dump(self._db.copy(), tmp, ensure_ascii=True,
                      separators=(',', ': '), indent=4)

        # atomically move the file
        os.replace(temp, self.name)

    async def save(self):
        """
        Save config to disk using async loop
        """
        async with self.lock:
            self._dump()
            # await self.loop.run_in_executor(None, self._dump)

    def get(self, key, *args):
        """Retrieves a config entry."""
        return self._db.get(str(key), *args)

    async def put(self, key, value):
        """Edits a config entry."""
        self._db[str(key)] = value
        await self.save()

    async def remove(self, key):
        """Removes a config entry."""
        del self._db[str(key)]
        await self.save()

    def __contains__(self, item):
        return str(item) in self._db

    def __getitem__(self, item):
        return self._db[str(item)]

    def __iter__(self):
        """
        Object to iterate over
        """
        return iter(self.all())

    def __next__(self):
        return next(self.all())

    def __len__(self):
        return len(self._db)

    def all(self):
        """Returns entire config dictionary"""
        return self._db
