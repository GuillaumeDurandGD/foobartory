"""Robot related classes.

One class per role. Each role do a specific each

  Typical usage example:

  robot = RobotWithRole()
  robot.work()
  robot.cancel()
"""

import asyncio
import logging
import random
from typing import Dict
from abc import ABCMeta, abstractmethod

LOGGER = logging.getLogger(__name__)


def is_successful_assembly() -> bool:
    """Random boolean with 60% chance to be True

    Returns:
         A boolean
    """
    return round(random.random(), 2) <= 0.6


class Robot(metaclass=ABCMeta):
    no_action_sleeping_time = 1

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        self.loop = loop
        self.name = None
        self.stock_ref = stock_ref
        self.task = None
        self.task_assignment_ref = task_assignment_ref

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

    @property
    def action_duration(self):
        return 1

    async def action(self) -> None:
        while True:
            await asyncio.sleep(self.action_duration)
            self.stock_ref["foo"] += 1
            LOGGER.debug("foo")


class BarMiner(Robot):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        super().__init__(loop, stock_ref, task_assignment_ref)
        self.name = "bar"

    @property
    def action_duration(self):
        return round(random.uniform(0.5, 2.0), 1)

    async def action(self) -> None:
        while True:
            await asyncio.sleep(self.action_duration)
            self.stock_ref["bar"] += 1
            LOGGER.debug("bar")


class FooBarAssembler(Robot):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        super().__init__(loop, stock_ref, task_assignment_ref)
        self.name = "assembler"

    @property
    def action_duration(self):
        return 2

    async def action(self):
        while True:
            if self.stock_ref["foo"] == 0 or self.stock_ref["bar"] == 0:
                await asyncio.sleep(self.no_action_sleeping_time)
                continue

            self.stock_ref["foo"] -= 1
            self.stock_ref["bar"] -= 1

            await asyncio.sleep(self.action_duration)

            if is_successful_assembly():
                self.stock_ref["foobar"] += 1
            else:
                self.stock_ref["foo"] -= 1
                self.stock_ref["bar"] += 1


class FooBarSeller(Robot):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stock_ref: Dict,
        task_assignment_ref: Dict,
    ):
        super().__init__(loop, stock_ref, task_assignment_ref)
        self.name = "seller"

    @property
    def action_duration(self):
        return 10

    async def action(self):
        while True:
            if self.stock_ref["foobar"] == 0:
                await asyncio.sleep(self.no_action_sleeping_time)
                continue

            nb_foobar_to_sell = 0

            if self.stock_ref["foobar"] <= 5:
                nb_foobar_to_sell = self.stock_ref["foobar"]
                self.stock_ref["foobar"] = 0
            elif self.stock_ref["foobar"] > 5:
                nb_foobar_to_sell = 5
                self.stock_ref["foobar"] -= 5

            await asyncio.sleep(self.action_duration)

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
                await asyncio.sleep(self.no_action_sleeping_time)
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

    @property
    def action_duration(self):
        return 5

    async def action(self):
        while True:
            print("I'm waiting for a role")
            await asyncio.sleep(self.action_duration)
