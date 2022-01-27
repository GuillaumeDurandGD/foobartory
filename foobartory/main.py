import asyncio
import logging

from foobartory.robot import (
    FooMiner,
    BarMiner,
    FooBarAssembler,
    FooBarSeller,
    RobotBuyer,
    Robot,
)

logging.basicConfig(level=logging.INFO)

stock = {"foo": 0, "bar": 0, "foobar": 0, "euros": 0, "robots": 2}

tasks_assignment = {
    "foo": [],
    "bar": [],
    "assembler": [],
    "seller": [],
    "buyer": [],
    "available": [],
}

mapping_name_task = {
    "foo": FooMiner,
    "bar": BarMiner,
    "assembler": FooBarAssembler,
    "seller": FooBarSeller,
    "buyer": RobotBuyer,
}

MINIMUM_NBR_OF_ROBOTS_TO_FILL_ALL_ROLES = 5


def take_the_best_robot_to_move_to() -> Robot:
    """Select a robot in an non empty assignment list
    It takes in priority bots in "available" role then "buyer", etc
    available -> buyer -> seller -> assembler -> bar -> foo

    Returns:
        A object of type Robot
    """
    role_with_available_robots = [
        role
        for role, associated_robots in tasks_assignment.items()
        if len(associated_robots)
    ]
    best_role_to_choose = role_with_available_robots[-1]
    return tasks_assignment[best_role_to_choose].pop()


async def change_robot_role_by(
    loop_: asyncio.AbstractEventLoop, wanted_role: str, from_role: str = None
) -> None:
    """Change the role of a robot to a specific one

    Args:
        loop_: asyncio event loop
        wanted_role: the role we need to have
        from_role (optional): force the list where to pick up the robot
    """
    if from_role:
        robot = tasks_assignment[from_role].pop()
    else:
        robot = take_the_best_robot_to_move_to()

    logging.info(
        f"Change robot with {from_role or robot.name} role to have {wanted_role}"
    )
    robot.cancel()

    await asyncio.sleep(5)

    robot_for_new_role = mapping_name_task[wanted_role](loop_, stock, tasks_assignment)
    robot_for_new_role.work()


async def init_step(loop_: asyncio.AbstractEventLoop) -> None:
    """Initialisation step where it's necessary to move one robot on different roles
    to product all necessary resources to get more robots.
    This initialisation step lasts until we get all robots to fulfill all roles.
    After that, it's not necessary to move the robots.

    Args:
        loop_: asyncio event loop
    """
    FooMiner(loop_, stock, tasks_assignment).work()
    BarMiner(loop_, stock, tasks_assignment).work()

    while stock["robots"] < MINIMUM_NBR_OF_ROBOTS_TO_FILL_ALL_ROLES:
        if stock["euros"] >= 3 and stock["foo"] >= 6 and not tasks_assignment["buyer"]:
            await change_robot_role_by(loop_, "buyer")
        elif stock["foobar"] >= 5 and not tasks_assignment["seller"]:
            await change_robot_role_by(loop_, "seller")
        elif (
            stock["foo"] > 10
            and stock["bar"] > 10
            and not tasks_assignment["assembler"]
        ):
            await change_robot_role_by(loop_, "assembler")
        elif (
            (stock["euros"] < 3 or stock["foo"] < 6)
            and tasks_assignment["buyer"]
            and not tasks_assignment["bar"]
        ):
            await change_robot_role_by(loop_, "bar")

        await asyncio.sleep(15)


def get_role_with_less_nbr_of_attributed_robots() -> str:
    """Return the role with less associated robots.
    If there is equality here the priority. The function returns :
    foo -> bar -> assembler -> seller -> buyer

    Returns:
        A role name
    """
    previous_nbr_of_assigned_robots = None
    for role, assigned_robots in tasks_assignment.items():
        if role != "available":
            if len(assigned_robots) == 0:
                return role

            if previous_nbr_of_assigned_robots is None:
                previous_nbr_of_assigned_robots = len(assigned_robots)
                continue

            if previous_nbr_of_assigned_robots > len(assigned_robots):
                return role

    return list(tasks_assignment.keys())[0]


async def manager(loop_: asyncio.AbstractEventLoop) -> None:
    """Manager is here to give a role to new available robot.
    Its second role is to stop the loop when 30 robots have been created.

    Args:
        loop_: asyncio event loop
    """
    while True:
        if len(tasks_assignment["available"]):
            logging.info("Robot(s) is/are available")
            role_to_take = get_role_with_less_nbr_of_attributed_robots()
            await change_robot_role_by(loop_, role_to_take, from_role="available")

        if stock["robots"] >= 30:
            logging.info("We reached 30 robots, we can stop the production")
            loop_.stop()

        await asyncio.sleep(1)


async def logger() -> None:
    """Log stock and assignment informations to follow the behaviour"""

    while True:
        logging.info(f"Stock information : {stock}")
        logging.info(
            f"Assignment information : {({key: len(ls) for key, ls in tasks_assignment.items()})}"
        )
        await asyncio.sleep(2)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(manager(loop))
        loop.create_task(logger())
        loop.create_task(init_step(loop))
        loop.run_forever()
    finally:
        loop.close()
