web: gunicorn runp-heroku:app
init: pip install -r requirements.txt; python db_create.py
upgrade: python db_upgrade.py
