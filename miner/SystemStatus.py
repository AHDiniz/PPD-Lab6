from enum import Enum


class SystemStatus(Enum):
    INIT = 0
    PUB_KEYS = 1
    ELECTION = 2
    CHALLENGE = 3
    RUNNING = 4
    VOTING = 5
    UPDATE = 6
    