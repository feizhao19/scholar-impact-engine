from pathlib import Path

from scholar_impact_engine.config import load_config


def test_load_example_config():
    config = load_config(Path("config.example.yaml"))
    assert config.author_id_column == "scopus_id"
    assert len(config.time_periods) == 3
    assert config.time_periods[0].name == "before_2017"
    assert config.citation_start_year == 2000
    assert config.output_formats == ["csv", "json"]
    assert config.output_basename == "impact_metrics"
