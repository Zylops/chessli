import subprocess
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from chessli import ChessliPaths
from chessli.rich_logging import log
from chessli.utils import in_bold

console = Console()


@dataclass
class Opening:
    name: str
    site: str
    eco: str
    moves: str
    config: Any
    paths: ChessliPaths

    def __str__(self):
        return f"{self.eco} - {self.name}"

    @property
    def items(self) -> Dict:
        return vars(self)

    @property
    def md(self) -> str:
        md = "# Opening\n"
        for key, value in self.items.items():
            if key not in ["config", "paths"]:
                md += f"## {key.replace('_', ' ').title()}\n"
                md += f"{value}\n"
        return md

    @property
    def pprint(self) -> None:
        console.print(Markdown(self.md))

    @property
    def path(self) -> Path:
        openings_dir = self.paths.openings_dir
        return (openings_dir / str(self)).with_suffix(".md")

    def exists(self) -> bool:
        return self.path.exists()

    @property
    def apy_header(self) -> str:
        return "model: Chessli Openings\ntags: chess::openings\ndeck: Chessli::openings\nmarkdown: False\n\n"

    def store(self, force: bool = False) -> None:
        if not self.exists() or force:
            log.info(f"Storing opening: {in_bold(str(self))}")
            md = f"{self.apy_header}"
            md += f"{self.md}\n\n"
            self.path.write_text(md)
        else:
            log.info(f"Ignoring {in_bold(str(self))}. You already know that opening :)")

    def ankify(self):
        if self.exists():
            subprocess.run(["apy", "add-from-file", self.path], input=b"n")
        else:
            console.log(
                "To ankify, you first need to store the opening with `opening.store()`"
            )


class ECOVolume(str, Enum):
    A = "Volume A: Flank openings"
    B = "Volume B: Semi-Open Games other than the French Defense"
    C = "Volume C: Open Games and the French Defense"
    D = "Volume D: Closed Games and Semi-Closed Games"
    E = "Volume E: Indian Defenses"


def list_known_openings(eco_volume: Optional[ECOVolume], chessli_paths, config):
    opening_dict = defaultdict(list)
    known_openings = sorted([f.stem for f in chessli_paths.openings_dir.glob("*.md")])
    print(
        f":fire: You already know a total of {in_bold(len(known_openings))} openings!!! :fire:",
        end="\n\n",
    )

    for opening in known_openings:
        opening_dict[opening[0]].append(opening)

    for key, value in opening_dict.items():
        if eco_volume is None or key == eco_volume:
            eco_volume_title = f"{ECOVolume[key]} ({len(value)})"
            print(f"[bold blue]{eco_volume_title}[/bold blue]!", end="\n\n")
            for val in value:
                print("✔️ ", val)
            print("")


def print_openings(openings: List["Opening"]):
    table = Table("", "Name", "ECO", title="New Openings")

    for opening in openings:
        if opening.exists():

            new_str = ""
            name_str = f"[grey]{opening.name}[/grey]"
            eco_str = f"[grey]{opening.eco}[/grey]"
        else:
            new_str = ":new:"
            name_str = f"[green]{opening.name}[/green]"
            eco_str = f"[green]{opening.eco}[/green]"

        table.add_row(new_str, eco_str, name_str)

    console.print(table)
