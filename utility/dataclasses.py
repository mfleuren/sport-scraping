from dataclasses import dataclass, field
import pandas as pd

from scraper_pcs.process_files import import_matches, import_points, import_teams, import_all_results

@dataclass
class Message:
    img_urls: list[list[str]] = field(default_factory=list)
    coach_mentions: list[list[str]] = field(default_factory=list)


@dataclass
class StageResults:
    matches: pd.DataFrame = field(default_factory=import_matches)
    default_points: pd.DataFrame = field(default_factory=import_points)
    teams: pd.DataFrame = field(default_factory=import_teams)
    all_results: pd.DataFrame = field(default_factory=import_all_results)
    stage_results: list[pd.DataFrame] = field(default_factory=list)
    stage_points: list[pd.DataFrame] = field(default_factory=list)
    stage_standings: list[pd.DataFrame] = field(default_factory=list)
    
