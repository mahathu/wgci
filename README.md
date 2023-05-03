# wgci
wgcompany interface

To set up local development environment:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd client && npm build  # svelte frontend
cd ..
flask --debug run  # flask development server
```