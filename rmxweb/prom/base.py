
from .config import DURATION, EXCEPTION, LAST_CALL, PROG_PREFIXES, SUCCESS


class BasePrometheus:

    def __init__(self, *args, dtype: str = None, **kwds):

        if dtype not in PROG_PREFIXES:
            raise ValueError(f'"{dtype}" is not in {PROG_PREFIXES}')
        self.dtype = dtype

        self.containerid = None
        self.features = None
        self.func_name = None

    def process_parameters(self, **kwds):
        if "containerid" in kwds:
            self.containerid = kwds.get('containerid')
        elif "container" in kwds:
            self.containerid = kwds["container"].pk
        self.features = kwds.get('features') or kwds.get('feats')

    @property
    def gname_suffix(self):
        suffix = f'_containerid_{self.containerid}'
        if self.features is not None:
            suffix += f'_features_{self.features}'
        return suffix

    @property
    def progress_name(self):
        return f'{self.dtype}__{DURATION}_{self.gname_suffix}'

    @property
    def lastcall_name(self):
        return f'{self.dtype}__{LAST_CALL}_{self.gname_suffix}'

    @property
    def exception_name(self):
        return f'{self.dtype}__{EXCEPTION}_{self.gname_suffix}'

    @property
    def success_name(self):
        return f'{self.dtype}__{SUCCESS}_{self.gname_suffix}'
