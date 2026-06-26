from pathlib import Path

from scholar_impact_engine.config import load_config
from scholar_impact_engine.pipeline import read_author_ids


def test_read_headerless_author_ids(tmp_path: Path):
    csv_path = tmp_path / "ids.csv"
    csv_path.write_text("12345678900\n98765432100\n", encoding="utf-8")

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
input:
  file: {csv_path}
  author_id_column: scopus_id
  has_header: false
time_periods:
  - name: p1
    end: "2020-12-31"
citation:
  start_year: 2000
output:
  directory: {tmp_path / "out"}
  formats: [csv]
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)
    assert read_author_ids(config) == [12345678900, 98765432100]
