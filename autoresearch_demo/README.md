# Autoresearch Demo

This directory contains a synthetic MoFNet-shaped demonstration of the `autoresearch-bio` protocol. The data are generated locally and are not ROS/MAP; the numbers illustrate the process discipline, not biology.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-demo.txt
python autoresearch_demo/run_autoresearch.py
python autoresearch_demo/make_plots.py
python scripts/validate_autoresearch_artifacts.py --budget 25 autoresearch_demo/outputs/experiments
```

The committed `outputs/` files are a small reference run used by CI to ensure the example still satisfies the current validator.
