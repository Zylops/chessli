from typing import List, Optional

import typer
from omegaconf import OmegaConf
from rich import print
from rich.console import Console
from rich.table import Table

from chessli.ankify import ankify_openings
from chessli.enums import PerfType, SinceEnum
from chessli.games import GamesFetcher, GamesReader
from chessli.openings import ECOVolume, list_known_openings
from chessli.utils import (
    as_title,
    convert_since_enum_to_millis,
    create_config_from_options,
    extract_context_info,
    in_bold,
)

app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context,):
    """Show and ankify chess openings"""

    ctx.params = ctx.parent.params
    print(as_title("chessli openings"), end="\n\n")


@app.command()
def ls(
    ctx: typer.Context,
    eco: Optional[ECOVolume] = typer.Option(
        default=None, help="Limit the shown openings to specific ECO volume"
    ),
    perf_type: Optional[List[PerfType]] = typer.Option(
        None, help="Filter fetching of games to the selected `perf_types`"
    ),
):
    """List your played openings"""
    chessli_paths, cli_config = extract_context_info(ctx)
    list_known_openings(eco, chessli_paths, cli_config)


@app.command()
def ankify(
    ctx: typer.Context,
    new_openings_only: bool = typer.Option(True, help="Only ankify new openings"),
    since_enum: SinceEnum = typer.Option(
        SinceEnum.last_time,
        "--since",
        help="Filter fetching of games to those played since `since`",
    ),
    max: Optional[int] = typer.Option(30, help="Limit fetching of games to `max`",),
    perf_type: Optional[List[PerfType]] = typer.Option(
        None, help="Filter fetching of games to the selected `perf_types`"
    ),
    export_only: bool = typer.Option(
        True,
        "--export-only/--directly",
        help="Select to only export the created anki cards",
    ),
):
    """Parse your games to find new openings and create Anki cards"""
    chessli_paths, cli_config = extract_context_info(ctx)
    cli_config["since_millis"] = convert_since_enum_to_millis(
        since_enum, chessli_paths.user_config.last_fetch_time
    )

    if new_openings_only:
        games = GamesFetcher(chessli_paths, cli_config).fetch_games()
    else:
        games = GamesReader(chessli_paths, cli_config).games

    ankify_openings(games=games, export_only=export_only)


if __name__ == "__main__":
    app()
