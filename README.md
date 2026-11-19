# WeLearn Database

This repository contains the database schema and sample data for the WeLearn application, an online learning platform.

## Pypi Package
You can install this pacakge via pypi :

```bash
pip install welearn-database
```
or you can read pypi page [here](https://pypi.org/project/welearn-database/)

## Environment Variables
Before running the application, make sure to set the following environment variables:
```
PG_USER=<pg user>
PG_PASSWORD=<pg password>
PG_HOST=<pg address>
PG_PORT=<pg port, 5432 by default>
PG_DB=<pg database name>
PG_DRIVER=<driver to use, pg default is : postgresql+psycopg2>
PG_SCHEMA=document_related,corpus_related,user_related,agent_related
LOG_LEVEL=INFO
LOG_FORMAT=[%(asctime)s][%(name)s][%(levelname)s] - %(message)s
```

## Database Migrations
Migrations are Alembic revisions in `welearn_database/alembic/versions`. Run them from a clone of this repository, after `poetry install`, not from the package installed from PyPI.

### Setup
- Put a `.env` file at the root of the repository with the variables above. `PG_DB` is the database name (the API calls it `PG_DATABASE`).
- `env.py` loads `.env`, but a variable already exported in your shell wins. Check that `env | grep PG_` prints nothing, or only the values you expect.
- The dev and staging databases need the VPN.

### Check where the database is
```bash
poetry run alembic current   # revision the database is at
poetry run alembic heads     # latest revision in this repository
poetry run alembic history   # full chain
```
`env.py` prints which database it connects to: dev, staging or unknown. For prod, it waits for Enter before going on.

### Preview the SQL (`--sql`, nothing is applied)
```bash
poetry run alembic upgrade 1_5_6:1_5_7 --sql > 1_5_7.sql
```
- Offline mode only writes the SQL out. It doesn't connect to the database, doesn't change it, and doesn't update `alembic_version`.
- It needs a `from:to` range, because it can't read the database's current revision.
- If you see `-- Running upgrade 1_5_6 -> 1_5_7` followed by SQL, nothing was applied.
- If you run the file by hand (psql, DBeaver…), it ends with `UPDATE alembic_version …`. That table lives in the `public` schema.

### Apply the migration
```bash
poetry run alembic upgrade 1_5_7   # or: upgrade head
poetry run alembic current         # should print 1_5_7
```
- Upgrading to a named revision runs only what you expect.
- A real run logs `INFO … Running upgrade 1_5_6 -> 1_5_7, …` and prints no SQL.

### Roll back
```bash
poetry run alembic downgrade 1_5_6
```
This runs the revision's `downgrade()`. For `1_5_7`, that drops the `feature`, `thread` and `guest_feature_usage` tables.

### Order across environments
Migrate dev, then staging, then prod (and the Scaleway database). An environment must be migrated before an API version that uses the new tables is deployed there. A migration that only adds tables, like `1_5_7`, doesn't break an older API running on the migrated database.

## Database Schema
The database schema is organized into four main schemas:
- `document_related`: Contains tables related to documents and their metadata.
- `corpus_related`: Contains tables related to corpora and their metadata.
- `user_related`: Contains tables related to users and their profiles.
- `agent_related`: Contains tables related to agents and their interactions.

## How to Use
Data models are defined using SQLAlchemy ORM. You can import the models and use them to interact with the database.
```python
from welearn_database.data.models import WeLearnDocument
```
Every model are accessible there, schema are handled under the hood.