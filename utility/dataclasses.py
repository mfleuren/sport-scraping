from dataclasses import dataclass, field
import pandas as pd

@dataclass
class Message:
    img_urls: list[list[str]] = field(default_factory=list),
    coach_mentions: list[list[str]] = field(default_factory=list)


@dataclass
class StageResults:
    stage_results: list[pd.DataFrame] = field(default_factory=list)
    stage_points: list[pd.DataFrame] = field(default_factory=list)
    stage_standings: list[pd.DataFrame] = field(default_factory=list)