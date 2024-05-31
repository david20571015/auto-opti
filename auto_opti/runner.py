import os
import subprocess
from collections.abc import Iterable
from itertools import product

from auto_opti.config import MT5ConfigBuilder
from auto_opti.param import Parameters


def execute_mt5_optimization(mt5_terminal_path: str, config_path: str):
    cmd = f'"{mt5_terminal_path}" /config:"{config_path}"'
    cmd = f"wc -l {config_path}"
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to run optimization, because {e}") from e


def run(
    params: Parameters,
    mt5_terminal: str,
    symbols: Iterable[str],
    periods: Iterable[str],
):
    if not os.path.exists(mt5_terminal):
        raise FileNotFoundError(f"MT5 terminal not found at {mt5_terminal}")

    builder = MT5ConfigBuilder(params.base_config_path)
    builder.upsert_tester(
        {
            "ShutdownTerminal": "1",
            "ReplaceReport": "1",
        }
    )

    for symbol, period in product(symbols, periods):
        builder.upsert_tester(
            {
                "Symbol": symbol,
                "Period": period,
                "Report": f"{params.__class__.__name__}-{symbol}-{period}",
            }
        )

        for param in params:
            builder.upsert_tester_input(param)
            config = builder.build()

            with config.save_temp_config(
                f"tmp-{symbol}-{period}.ini", delete=True
            ) as config_path:
                print(config_path)
                execute_mt5_optimization(mt5_terminal, config_path)
