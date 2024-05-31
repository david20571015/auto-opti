import os
import subprocess
from collections.abc import Iterable
from itertools import product

from tqdm import tqdm

from auto_opti.config import MT5ConfigBuilder
from auto_opti.param import Parameters


def execute_mt5_optimization(mt5_terminal_path: str, config_path: str):
    cmd = [mt5_terminal_path, f"/config:{config_path}"]
    subprocess.run(cmd, shell=True, check=True)


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

    with tqdm(
        product(symbols, periods),
        total=len(list(symbols)) * len(list(periods)),
        dynamic_ncols=True,
    ) as pbar:
        for symbol, period in pbar:
            pbar.set_postfix_str(f"{symbol}-{period}")
            builder.upsert_tester(
                {
                    "Symbol": symbol,
                    "Period": period,
                    "Report": f"{params.__class__.__name__}-{symbol}-{period}",
                }
            )

            for param in tqdm(
                params, total=len(list(params)), dynamic_ncols=True, leave=False
            ):
                builder.upsert_tester_input(param)
                config = builder.build()

                with config.save_temp_config(
                    f"tmp-{symbol}-{period}.ini", delete=True
                ) as config_path:
                    print(f"Running config file: {config_path}")
                    try:
                        execute_mt5_optimization(mt5_terminal, config_path)
                    except subprocess.CalledProcessError as e:
                        print(f'Failed to run optimization, because "{e}"')
