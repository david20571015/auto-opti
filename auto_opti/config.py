import os
from abc import abstractmethod
from configparser import ConfigParser
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import Optional, Protocol, Self, runtime_checkable


class MT5Config(ConfigParser):
    ENCODING = "utf-16"

    def __init__(self, base_config: ConfigParser):
        super().__init__()
        self.update(deepcopy(base_config))

    def optionxform(self, optionstr: str):
        return optionstr

    @contextmanager
    def save_temp_config(self, file_path: Optional[str] = None, delete: bool = False):
        def write_config(file_name: str):
            with open(file_name, "w", encoding=self.ENCODING) as f:
                self.write(f)

        if file_path:
            write_config(file_path)
            yield file_path
            if delete:
                os.remove(file_path)
        else:
            with NamedTemporaryFile(delete=delete, delete_on_close=False) as file:
                file.close()
                write_config(file.name)
                yield file.name


@runtime_checkable
class SupportsStr(Protocol):
    __slots__ = ()

    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass
class TesterInputArg:
    start: SupportsStr
    step: SupportsStr
    end: SupportsStr

    def __str__(self) -> str:
        return "||".join(map(str, (self.start, self.start, self.step, self.end, "Y")))


class MT5ConfigBuilder:
    def __init__(self, base_config: ConfigParser | str):
        if isinstance(base_config, str):
            base_config_path = base_config

            base_config = ConfigParser()
            base_config.optionxform = str
            read_result = base_config.read(
                base_config_path, encoding=MT5Config.ENCODING
            )
            if not read_result:
                raise FileNotFoundError(
                    f"Config file {base_config_path} not found or failed to read."
                )

        self.config = MT5Config(base_config)

    def upsert_tester(self, tester_args: dict[str, str]) -> Self:
        self.config["Tester"].update(tester_args)
        return self

    def upsert_tester_input(self, tester_input_args: dict[str, TesterInputArg]) -> Self:
        inputs = {k: str(v) for k, v in tester_input_args.items()}
        self.config["TesterInputs"].update(inputs)
        return self

    def build(self) -> MT5Config:
        return self.config
