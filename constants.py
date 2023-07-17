from enum import Enum

class PullRequestState(Enum):
    MERGED = 'MERGED'
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
