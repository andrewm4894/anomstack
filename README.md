# AnomStack

Painless open source anomaly detection for business metrics!

## Project Structure

- [`./anomstack`](./anomstack) source code for AnomStack.
- [`./metrics`](./metrics) sample metrics data. This is where you define your metrics (check out `examples` folder). Defaults params etc live in `defaults` folder.

## Quick Start

```bash
# git clone
git clone https://github.com/andrewm4894/anomstack.git
# cd into project
cd anomstack
# make virtual env
python3 -m venv .venv
# activate virtual env
source .venv/bin/activate
# install deps
pip install -r requirements.txt
# cp example env file
cp .example.env .env
# run locally
dagster dev -f anomstack/main.py
```

```bash
# run via docker
docker compose up
```
