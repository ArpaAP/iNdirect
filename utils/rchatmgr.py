import discord
from discord.ext import commands, tasks
import random
import asyncio
import traceback
from itertools import chain
from typing import List, Dict, Optional
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
    def __init__(self, count: int, cancel: bool, altnick: Optional[str]):
        self.count = count
        self.cancel = cancel
        self.altnick = altnick

    def __eq__(self, other):
        return self.count == other.count and self.cancel == other.cancel and self.altnick == other.altnick

class MatchItem:
    def __init__(self, uid, altnick: Optional[str]):
        self.uid = uid
        self.altnick = altnick

    def __eq__(self, other):
        return self.uid == other.uid and self.altnick == other.altnick

class RandchatMgr:
    def __init__(self):
        self.__queue: Dict[int, QueueItem] = {}
        self.__matches: List[List[MatchItem]] = []

    def start_match_task(self):
        self.match.start()

    async def start_match(self, uid, *, count: int=1, altnick: str=None, timeout: float):
        if uid in self.__queue:
            raise UserAlreadyInQueue(uid)
        if uid in map(lambda x: x.uid, chain.from_iterable(self.__matches)):
            raise UserAlreadyMatched(uid)
        self.__queue[uid] = QueueItem(count, False, altnick)
        return await asyncio.wait_for(self.wait_for_match(uid), timeout=timeout)
        
    async def wait_for_match(self, uid):
        while True:
            m = list(filter(lambda o: uid in map(lambda x: x.uid, o), self.__matches))
            if m:
                return m[0]
            if uid not in self.__queue:
                if uid not in (y.uid for x in self.__matches for y in x):
                    raise MatchCanceled
            await asyncio.sleep(1)

    def cancel_match(self, uid):
        if uid in self.__queue:
            del self.__queue[uid]

    def clear_queue(self):
        self.__queue = {}

    @tasks.loop()
    async def match(self):
        try:
            await asyncio.sleep(1)
            if not self.__queue:
                return

            uid = random.choice(list(self.__queue.keys()))
            count = self.__queue[uid].count
            matchables = list(filter(lambda u: u != uid and self.__queue[u].count == count, self.__queue.keys()))
            if len(matchables) >= count:
                match = [MatchItem(uid, self.__queue[uid].altnick)]
                for x in random.sample(matchables, k=count):
                    match.append(MatchItem(x, self.__queue[x].altnick))
                    del self.__queue[x]
                self.__matches.append(match)
                del self.__queue[uid]
        except:
            traceback.print_exc()

    def get_queue(self):
        return deepcopy(self.__queue)

    def get_matches(self):
        return deepcopy(self.__matches)

    def is_in_queue(self, uid):
        return uid in self.__queue

    def is_matched(self, uid):
        return uid in (y.uid for x in self.__matches for y in x)

    def get_matched(self, uid):
        return deepcopy(next((m for m in self.__matches if uid in map(lambda x: x.uid, m)), None))

    def exit_match(self, uid):
        matched = self.get_matched(uid)
        mymatchindex = self.__matches.index(next((x for x in self.__matches if x == matched), None))
        mymatchitem = next((x for x in matched if x.uid == uid), None)
        mymatchitemindex = matched.index(next((x for x in matched if x == mymatchitem), None))

        if len(matched) > 2:
            del self.__matches[mymatchindex][mymatchitemindex]
        else:
            del self.__matches[mymatchindex]
