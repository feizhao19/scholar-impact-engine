# Medical education example

This example configures **Scholar Impact Engine** with time windows common in
training-outcomes research:

| Period | Window |
|--------|--------|
| `before_2017` | through 2016-12-31 |
| `period_2017_2021` | 2017-01-01 to 2021-12-31 |
| `after_2021` | from 2022-01-01 |

## Run

```bash
pip install -e .
scholar-impact-engine --config examples/medical_education/config.yaml
```

Replace `data/sample_author_ids.csv` with your cohort's Scopus author IDs.
Do not commit identifiable cohort data to a public repository without approval.
