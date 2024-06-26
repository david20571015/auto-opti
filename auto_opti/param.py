from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from functools import cache

from auto_opti.config import SupportsStr, TesterInputArg


class Parameters(ABC):
    @property
    @abstractmethod
    def base_config_path(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def parameter_list(
        self,
    ) -> Iterable[dict[str, TesterInputArg | Sequence[SupportsStr]]]:
        raise NotImplementedError

    @cache
    def __len__(self):
        return len(list(self.parameter_list))

    def __iter__(self):
        def unify(param: dict[str, TesterInputArg | Sequence[SupportsStr]]):
            return {
                k: v if isinstance(v, TesterInputArg) else TesterInputArg(*v)
                for k, v in param.items()
            }

        yield from map(unify, self.parameter_list)
