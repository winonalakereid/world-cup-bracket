# world-cup-bracket

# Getting Started
Pre-requisites:
- Python 3

Recommended:
- virtualenv
- virtualenvwrapper

```
http://virtualenvwrapper.readthedocs.io/en/latest/
```

# Local Dev
Install dependencies (after creating a new virtualenv if you so choose):

```
cd WCBSite
pip install -r requirements.txt
```

Now let's run the server

```
python manage.py runserver
```

Our server should be started on port 8000, check it out:
http://localhost:8000/bracket