import asyncio
import random
from typing import Dict
from abc import ABCMeta, abstractmethod


def is_successful_assembly() -> bool:
    """Random boolean with 60% chance to be True

    Returns:
         A boolean
    """
    return round(random.random(), 2) <= 0.6


class Robot(metaclass=ABCMeta):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        self.stock_ref = stock_ref
        self.task_assignment_ref = task_assignment_ref
        self.loop = loop
        self.name = None
        self.task = None

    def work(self) -> None:
        self.task = self.loop.create_task(self.action())
        self.task_assignment_ref[self.name].append(self)

    @abstractmethod
    async def action(self):
        pass

    def cancel(self) -> None:
        self.task.cancel()


class FooMiner(Robot):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        super().__init__(loop, stock_ref, task_assignment_ref)
        self.name = "foo"

    async def action(self) -> None:
        while True:
            await asyncio.sleep(1)
            self.stock_ref["foo"] += 1
            print("foo")


class BarMiner(Robot):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        super().__init__(loop, stock_ref, task_assignment_ref)
        self.name = "bar"

    async def action(self) -> None:
        while True:
            await asyncio.sleep(1)
            self.stock_ref["bar"] += 1
            print("bar")


class FooBarAssembler(Robot):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        super().__init__(loop, stock_ref, task_assignment_ref)
        self.name = "assembler"

    async def action(self):
        while True:
            if self.stock_ref["foo"] > 0 and self.stock_ref["bar"] > 0:
                self.stock_ref["foo"] -= 1
                self.stock_ref["bar"] -= 1

                await asyncio.sleep(2)

                if is_successful_assembly():
                    self.stock_ref["foobar"] += 1
                else:
                    self.stock_ref["foo"] -= 1
                    self.stock_ref["bar"] += 1
            else:
                await asyncio.sleep(1)


class FooBarSeller(Robot):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        super().__init__(loop, stock_ref, task_assignment_ref)
        self.name = "seller"

    async def action(self):
        while True:
            if self.stock_ref["foobar"] == 0:
                await asyncio.sleep(1)
                continue

            nb_foobar_to_sell = 0

            if self.stock_ref["foobar"] <= 5:
                nb_foobar_to_sell = self.stock_ref["foobar"]
                self.stock_ref["foobar"] = 0
            elif self.stock_ref["foobar"] > 5:
                nb_foobar_to_sell = 5
                self.stock_ref["foobar"] -= 5

            await asyncio.sleep(10)

            self.stock_ref["euros"] += nb_foobar_to_sell


class RobotBuyer(Robot):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        super().__init__(loop, stock_ref, task_assignment_ref)
        self.name = "buyer"

    async def action(self):
        while True:
            if self.stock_ref["euros"] < 3 or self.stock_ref["foo"] < 6:
                await asyncio.sleep(1)
                continue

            self.stock_ref["foo"] -= 6
            self.stock_ref["euros"] -= 3
            self.stock_ref["robots"] += 1

            AvailableRobot(self.loop, self.stock_ref, self.task_assignment_ref).work()


class AvailableRobot(Robot):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        super().__init__(loop, stock_ref, task_assignment_ref)
        self.name = "available"

    async def action(self):
        while True:
            print("I'm waiting for a role")
            await asyncio.sleep(5)
