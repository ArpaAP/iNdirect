import discord
from discord.ext import commands, tasks
import random
import asyncio
import traceback
from itertools import chain
from typing import List, Dict
from copy import deepcopy

# pylint: disable=no-member

class RandChatMgrError(Exception):
    pass

class UserAlreadyMatched(RandChatMgrError):
    def __init__(self, uid):
        self.uid = uid
        super().__init__('이미 매치된 유저: {}'.format(uid))

class UserAlreadyInQueue(RandChatMgrError):
    def __init__(self, uid):
        self.uid = uid
        super().__init__('이미 매칭 중인 유저: {}'.format(uid))

class MatchCanceled(RandChatMgrError):
    pass


class QueueItem:
    def __init__(self, count: int, cancel: bool):
        self.count = count
        self.cancel = cancel


class RandchatMgr:
    def __init__(self):
        self.__queue: Dict[int, QueueItem] = {}
        self.__matches: List[List[int]] = []

    def start_match_task(self):
        self.match.start()

    async def start_match(self, uid, *, count: int=1, timeout: float):
        if uid in self.__queue:
            raise UserAlreadyInQueue(uid)
        if uid in chain.from_iterable(self.__matches):
            raise UserAlreadyMatched(uid)
        self.__queue[uid] = QueueItem(count, False)
        return await asyncio.wait_for(self.wait_for_match(uid), timeout=timeout)
        
    async def wait_for_match(self, uid):
        while True:
            m = list(filter(lambda o: uid in o, self.__matches))
            if m:
                return m[0]
            if uid not in self.__queue:
                if uid not in chain.from_iterable(self.__matches):
                    raise MatchCanceled
            await asyncio.sleep(0)

    def cancel_match(self, uid):
        if uid in self.__queue:
            del self.__queue[uid]

    def clear_queue(self):
        self.__queue = {}

    @tasks.loop()
    async def match(self):
        try:
            if not self.__queue:
                return

            uid = random.choice(list(self.__queue.keys()))
            count = self.__queue[uid].count
            matchables = list(filter(lambda u: u != uid and self.__queue[u].count == count, self.__queue.keys()))
            if len(matchables) >= count:
                match = []
                for x in random.sample(matchables, k=count):
                    match.append(x)
                    del self.__queue[x]
                match.append(uid)
                self.__matches.append(match)
        except:
            traceback.print_exc()

    def get_queue(self):
        return deepcopy(self.__queue)

    def get_matches(self):
        return deepcopy(self.__matches)

    def is_in_queue(self, uid):
        return uid in self.__queue

    def is_matched(self, uid):
        return uid in chain.from_iterable(self.__matches)

    def get_matched(self, uid):
        return deepcopy(next((m for m in self.__matches if uid in m), None))

    def exit_match(self, uid):
        matched = self.get_matched(uid)

        if len(matched) > 1:
            self.__matches[self.__matches.index(matched)].remove(uid)
        else:
            self.__matches.remove(matched)