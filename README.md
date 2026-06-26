# Scholar Impact Engine

**Measure how scholarly impact evolves — at cohort scale.**

Scholar Impact Engine is an open-source pipeline that turns Scopus author data into **time-stratified impact metrics**: publications, citations, and h-index split across configurable career phases.

Instead of a single snapshot ("this author has 40 papers"), you get an **impact profile** that shows *when* research output and influence accumulated — enabling cohort studies in medical education, faculty evaluation, graduate training, and program benchmarking.

## Why Scholar Impact Engine?

| Traditional approach | Scholar Impact Engine |
|---------------------|----------------------|
| Total publication count | Impact by career phase |
| One cumulative h-index | Temporal citation breakdown |
| Manual Scopus lookups | Reproducible batch pipeline |
| Domain-specific scripts | Config-driven, field-agnostic |

## Features

- **Cohort-scale impact profiling** from a CSV of Scopus Author IDs
- **Configurable time windows** for publications and citations
- **Citation retrieval** with DOI → PubMed ID fallback
- **Data quality auditing** for publications missing identifiers
- **Export** to CSV, JSON, or Excel
- **CLI and Python API**

## Quick start

### 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Configure Scopus API access

Register for a [Scopus API key](https://dev.elsevier.com/) and copy the example config:

```bash
mkdir -p ~/.config
cp pybliometrics.cfg.example ~/.config/pybliometrics.cfg
# Edit ~/.config/pybliometrics.cfg and set APIKey
```

> Yearly citation breakdowns require access to the Scopus **Citation Overview** API.

### 3. Configure your study

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` — especially `input.file`, `time_periods`, and `output`.

### 4. Run

```bash
scholar-impact-engine --config config.yaml
```

Outputs are written to `output.directory` (default: `outputs/`).

## Configuration

```yaml
input:
  file: data/sample_author_ids.csv
  author_id_column: scopus_id

time_periods:
  - name: before_2017
    end: "2016-12-31"
  - name: period_2017_2021
    start: "2017-01-01"
    end: "2021-12-31"
  - name: after_2021
    start: "2022-01-01"

citation:
  start_year: 2000
  identifier_priority: [doi, pubmed_id]

output:
  directory: outputs
  basename: impact_metrics
  formats: [csv, json]
```

Periods are evaluated **in order**. Each publication or citation year is assigned to the first matching period.

## Output columns

| Column | Description |
|--------|-------------|
| `scopus_id` | Scopus Author ID |
| `last_name`, `first_name` | Author name from Scopus |
| `affiliation_current`, `affiliation_parent` | Current affiliation fields |
| `publications_total` | Total document count |
| `citations_total` | Sum of period citation counts |
| `h_index` | Current h-index |
| `publications_<period>` | Publications in each configured period |
| `citations_<period>` | Citations received in each period (by year) |
| `publications_missing_identifier` | Titles with no DOI or PubMed ID |

## Example use cases

- **Medical education** — impact before vs. after residency training
- **Faculty evaluation** — pre-tenure vs. post-tenure scholarly output
- **Graduate training** — PhD cohort impact trajectories
- **Program benchmarking** — cross-institution author cohort comparison

See [`examples/medical_education/`](examples/medical_education/) for a study-specific configuration.

## Python API

```python
from scholar_impact_engine.config import load_config
from scholar_impact_engine.pipeline import run_pipeline
from scholar_impact_engine.export import export_results

config = load_config("config.yaml")
results = run_pipeline(config)
export_results(results, config)
```

## Testing

```bash
pytest
```

## Data and ethics

- Do **not** commit real cohort data, API keys, or full Scopus exports to a public repository.
- Check your institution's IRB / ethics requirements before analyzing identifiable researcher data.
- Respect [Elsevier / Scopus API terms of use](https://dev.elsevier.com/policy.html).

## Citation

If you use Scholar Impact Engine in your research, please cite this repository.

## License

MIT — see [LICENSE](LICENSE).
