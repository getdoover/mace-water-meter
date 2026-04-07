import logging

from pydoover.state import StateMachine


DEFAULT_SLEEP_TIME = 60 * 15  # 15 minutes
DEFAULT_AWAKE_TIME = 60 * 2  # 2 minutes
DEFAULT_WAKE_DELAY = 15  # 15 seconds


log = logging.getLogger(__name__)


class MaceWaterMeterState:
    state: str

    states = [
        {"name": "initial"},
        {"name": "sleeping", "timeout": DEFAULT_SLEEP_TIME, "on_timeout": "awaken"},
        {
            "name": "awake_init",
            "timeout": DEFAULT_WAKE_DELAY,
            "on_timeout": "initialised",
        },
        {"name": "awake_rt", "timeout": DEFAULT_AWAKE_TIME, "on_timeout": "goto_sleep"},
    ]

    transitions = [
        {"trigger": "initialise", "source": "initial", "dest": "awake_init"},
        {"trigger": "awaken", "source": "sleeping", "dest": "awake_init"},
        {"trigger": "initialised", "source": "awake_init", "dest": "awake_rt"},
        {"trigger": "goto_sleep", "source": ["awake_init", "awake_rt"], "dest": "sleeping"},
    ]

    def __init__(self):
        self.state_machine = StateMachine(
            states=self.states,
            transitions=self.transitions,
            model=self,
            initial="initial",
            queued=True,
        )

        self.should_request = False

    async def spin(self, battery_voltage: float):
        if self.state == "initial":
            await self.initialise()

    async def on_enter_sleeping(self):
        self.should_request = False

    async def on_enter_awake_init(self):
        self.should_request = True

    async def on_enter_awake_rt(self):
        self.should_request = True
