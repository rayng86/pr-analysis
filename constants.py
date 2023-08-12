from enum import Enum

class ColumnNames(Enum):
    PR_NUMBER = 'PR #'
    TITLE = 'Title'
    CREATED_AT = 'Created At'
    CLOSED_AT = 'Closed At'
    IS_DRAFT = 'Is Draft?'
    STATE = 'State'
    FILE_CHANGES = 'File Changes'
    CODE_AUTHOR = 'Code Author'
    CODE_REVIEWERS = 'Code Reviewers'
    NUM_REVIEW_REQUESTS = '# Of Review Requests'
    APPROVED_BY = 'Approved By'
    MERGED_BY = 'Merged By'
    MERGE_TIME = 'Merge Time'

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
