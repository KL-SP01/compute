# GPU rental price monitor

Daily tracker of GPU rental prices: the SemiAnalysis GPU pricing index tested against independent seller quotes and Latitude.sh list prices, with AI-demand signals (OpenRouter, Ramp) for context. Full history ships as an Excel workbook from the dashboard.

Live dashboard: https://kl-sp01.github.io/compute/

## Sources

| Source | What it measures | Update frequency |
| --- | --- | --- |
| [Latitude.sh pricing](https://www.latitude.sh/pricing) | List prices for whole-server GPU and CPU plans | Checked daily |
| [SemiAnalysis GPU Pricing Index](https://gpu-index.semianalysis.com/) | Composite GPU rental price index (B200, H100, A100 reference) | Daily index |
| [GPU Economy / SkyPilot](https://gpueconomy.com/data) | Weekly median and cheapest seller quotes (CC BY 4.0) | Checked daily; source updates weekly |
| [OpenRouter rankings](https://openrouter.ai/rankings) | Share of AI requests by model maker (CC BY 4.0) | Weekly source |
| [Ramp AI Index](https://ramp.com/data/ai-index) | Share of US businesses paying for AI | Monthly source |

## Local use

```sh
pip install playwright==1.55.0 openpyxl==3.1.5
python -m playwright install chromium
python test_collector.py
python test_demand.py
python collect_latitude.py
python rebuild_workbook.py
python build_latest.py
python -m http.server 8000
```

Open http://localhost:8000. Keep earlier keys in `snapshots.json`; same-day updates replace only that date. Check the page and workbook before committing `snapshots.json`, `workbook.b64`, `history.xlsx` and `latest.json` to `main`.

Actions > Daily update > Run workflow performs the same update and publishes the page. Pushes to `main` that touch the page or data files redeploy via the Publish dashboard changes workflow. The daily schedule is 21:17 UTC and may start late. Failed validation keeps the previous published data. Source dates are shown on the page; a new check does not imply a new release. Structural changes or large moves need manual review. The data, files and history are public.
