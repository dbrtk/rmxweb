CREATE_DATA_PREFIX = "create_data"

COMPUTE_MATRIX_PREFIX = "compute_matrix"

COMPUTE_MATRIX_RUN = "compute_matrix_run"
COMPUTE_MATRIX_CALLBACK = "compute_matrix_callback"

COMPUTE_DENDROGRAM_PREFIX = "compute_dendrogram"

LAST_CALL = 'last_call'
SUCCESS = 'success'
EXCEPTION = 'exception'
DURATION = 'time'
ACTIVE_PROC = 'active_proc'

PROG_PREFIXES = [
    # this is called when a the function to create Data Objects is called by
    # the scraper, the crawler.
    CREATE_DATA_PREFIX,  # - create_from_webpage

    # this is called when the dendrogram is being computed
    COMPUTE_DENDROGRAM_PREFIX,  # - dendrogram

    # this is the prefix for the tasks computing network graphs
    COMPUTE_MATRIX_PREFIX,  # - compute_matrix
]
