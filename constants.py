from enum import Enum

class PullRequestState(Enum):
    MERGED = 'MERGED'
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

class ExportTypeOptions(Enum):
    CSV = 'csv'
    HTML = 'html'
    MARKDOWN = 'md'
