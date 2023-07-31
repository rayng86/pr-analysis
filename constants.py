from enum import Enum

class PullRequestState(Enum):
    MERGED = 'MERGED'
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

class ExportTypeOptions(Enum):
    CSV = 'csv'
    HTML = 'html'
    MARKDOWN = 'md'

PULL_REQUEST_STATE = None
EXPORT_FILE_TYPE = ExportTypeOptions.CSV.value
MAX_PAGE_COUNT_LIMIT = 5
