CRAWL_RUN_PREFIX = "crawl_run"
CRAWL_CALLBACK_PREFIX = "crawl_callback"

CREATE_DATA_PREFIX = "create_data"

COMPUTE_DENDROGRAM_RUN_PREFIX = "compute_dendrogram_run"
COMPUTE_DENDROGRAM_CALLBACK_PREFIX = "compute_dendrogram_callback"

COMPUTE_MATRIX_RUN_PREFIX = "compute_matrix_run"
COMPUTE_MATRIX_CALLBACK_PREFIX = "compute_matrix_callback"

INTEGRITY_CHECK_RUN_PREFIX = "integrity_check_run"
INTEGRITY_CHECK_CALLBACK_PREFIX = "integrity_check_callback"


ENTER = 'enter'
EXIT = 'exit'

PROG_PREFIXES = (
    # this is called when a the function to create Data Objects is called by
    # the scraper, the crawler.
    CRAWL_RUN_PREFIX,
    CRAWL_CALLBACK_PREFIX,
    # called whenever a new webpage is written to the database
    CREATE_DATA_PREFIX,  # - create_from_webpage

    # this is called when the dendrogram is being computed
    COMPUTE_DENDROGRAM_RUN_PREFIX,  # - dendrogram-run
    COMPUTE_DENDROGRAM_CALLBACK_PREFIX,  # - dendrogram-callback

    # this is the prefix for the tasks computing network graphs
    COMPUTE_MATRIX_RUN_PREFIX,  # - compute_matrix_run
    COMPUTE_MATRIX_CALLBACK_PREFIX,  # - compute_matrix_callback

    INTEGRITY_CHECK_RUN_PREFIX,
    INTEGRITY_CHECK_CALLBACK_PREFIX,
)
