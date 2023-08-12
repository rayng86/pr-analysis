from enum import Enum

class PullRequestState(Enum):
    MERGED = 'MERGED'
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    ALL = None

class ExportTypeOptions(Enum):
    CSV = 'csv'
    HTML = 'html'
    MARKDOWN = 'md'

PULL_REQUEST_STATE = PullRequestState.ALL.value
EXPORT_FILE_TYPE = ExportTypeOptions.CSV.value
MAX_PAGE_COUNT_LIMIT = 5

class MergeTimeFormat(Enum):
    HOURS = 'hours'
    DAYS = 'days'

MERGE_TIME_FORMAT = MergeTimeFormat.HOURS
