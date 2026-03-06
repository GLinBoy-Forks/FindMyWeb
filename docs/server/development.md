# Server setup for Development
## Frontend
The frontend is written in Vue and TypeScript.
1. install [`deno`](https://deno.com/)
2. Change to the frontend folder: `cd frontend`
3. Build the frontend with: `deno run build`
4. All the frontend files should now reside in `dist`

## Backend
The backend is written in Python3 and uses [FindMy.py](https://docs.mikealmel.ooo/FindMy.py/) for all requests to Apple's servers.
1. Create a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```
3. Change to the backend folder
```
cd backend
```
2. Install all requirements using pip
```
pip install -r requirements.txt
```
3. Copy the default config file
```
cp ../example.config.toml ../config.toml
```
4. Set all relevant [config options](config.md)
5. Run the backend
- Development:
```
CONFIG_PATH="../config.toml" uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
- Deploy:
```
CONFIG_PATH="../config.toml" gunicorn -b 0.0.0.0 -p 8000 -k uvicorn.workers.UvicornWorker app:app
```
