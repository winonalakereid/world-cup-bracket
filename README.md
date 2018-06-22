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

# Data Migrations

Any time a model is updated, we need to update our database schema. Django does this for us with migrations.
To create a migration script for a schema update, run:
```
./manage.py makemigrations
```
This will create a new script in the bracket/migrations folder.
Now we can apply the migration by running

```
./manage.py migrate
```

If we want to revert a migration, first list the migrations:
```
./manage.py showmigrations
bracket
 [X] 0001_initial
 [X] 0002_auto_20180619_0803
 [X] 0003_group_groupteam_match_pick
 [X] 0004_auto_20180621_2040
 [X] 0005_data_setup
```

Then revert to the migration that we want:
```
./manage.py migrate {app name} {migration name}
Example:
./manage.py migrate bracket 0003_group_groupteam_match_pick
```

To get back to the latest after a revert, just run the migrate command again