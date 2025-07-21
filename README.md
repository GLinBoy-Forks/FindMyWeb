# FindMyWeb

## Setup

### Prerequisites
1. install [`deno`](https://deno.com/) / `npm`, `python3` and `pip`
2. Create a python venv: `python3 -m venv .venv`
3. Enter the venv: `source .venv/bin/activate`
4. Install all python packages: `python3 -m pip install -r backend/requirements.txt`

### Run
1. Build frontend: `cd frontend`
  - deno: `deno run build`
  - npm: `npm run build`
2. Copy `example.config.toml` to `config.toml`
3. Replace `jwt` keys with randomly generated ones: e.g `openssl rand -hex 32`
4. Replace `admin` name and password
5. Replace `findmy` `anisette` with your custom [anisette server](https://github.com/Dadoum/anisette-v3-server)
6. Create an `account.json` with the `scripts/login.py` script
7. Replace `findmy` `account` with the path to your `account.json`
8. Specify a `db` `uri`: e.g `/findmy.db`
9. Specify the path to the dist folder from 1.
10. Start the server:
  - `cd backend`
  - `CONFIG_PATH="../config.toml" gunicorn -k uvicorn.workers.UvicornWorker main:app`


### Development env
1. Do steps 1-10 from Run
2. run `CONFIG_PATH="../config.toml" uvicorn main:app --host 0.0.0.0 --reload --port 8000` instead of step 10.2
