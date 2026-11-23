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

## Release Workflow
A schema change goes from code to the prod database in seven steps. The commands for steps 3 and 7 are in [Database Migrations](#database-migrations).

1. **Change the code.** On a feature branch, edit the models in `welearn_database/data/models`.
2. **Write the Alembic migration.** Add one revision for the release in `welearn_database/alembic/versions`. Name its id after the version with underscores, and point `down_revision` at the previous one:
   ```bash
   poetry run alembic revision -m "add my table" --rev-id 1_5_8
   # creates welearn_database/alembic/versions/1_5_8_add_my_table.py
   ```
   `--autogenerate` can draft it from the models, but it ignores indexes and compares against the database in `.env`, so always read and fix the result. Test `upgrade` then `downgrade` on a local database (`welearn-fullstack`, `scripts/bootstrap-db.sh`). `poetry run alembic heads` must show a single head. Open the PR and get it merged on `main`.
3. **Update the dev databases.** On Azure dev, preview the SQL with `--sql`, then run `alembic -x env=dev upgrade <revision>` (VPN on). On Scaleway dev, generate the SQL and run it in pgAdmin (see [Scaleway dev](#scaleway-dev-run-the-sql-in-pgadmin)). If the change only adds tables or columns, the API already deployed on dev keeps working. If it renames or drops something, deploy the matching API at the same time.
4. **Tag a `.dev` version and make a pre-release.**
   - In `pyproject.toml`, set `version = "1.5.8.dev0"` and merge it on `main`.
   - Create a GitHub release with the same tag (`1.5.8.dev0`) on `main`, with "Set as a pre-release" checked.
   - Pushing the tag runs the workflow, which publishes the package to PyPI. Every push also publishes to TestPyPI.
   - PyPI normalizes the version: a tag `1.5.7.dev` is published as `1.5.7.dev0`.
5. **Validate in dev.**
   - In the API, pin the exact pre-release, `welearn-database = "1.5.8.dev0"`, then run `poetry lock`. A caret constraint like `^1.5.7` never picks up a `.dev` version.
   - Deploy on dev and test the feature.
   - If you need a fix, publish `1.5.8.dev1` the same way. If the migration itself changed, run `downgrade` then `upgrade` on dev again.
6. **Tag the prod version, coordinated with the API.**
   - Set `version = "1.5.8"` (no `.dev`), merge it, and create a normal GitHub release (not a pre-release) tagged `1.5.8`.
   - In the API, a PR moves the dependency to `^1.5.8`.
   - Agree with the API team on when it goes out: that PR must not reach an environment whose database hasn't been migrated (step 7).
7. **Update the prod database.**
   - Migrate staging first, then prod. Both are on Azure; Scaleway only has a dev environment for now.
   - Make sure a recent backup exists, then preview with `--sql` and run `alembic -x env=<staging|prod> upgrade <revision>`. For `prod`, `env.py` asks you to type the environment name before it goes on.
   - After that, deploy the API version that uses the new schema.

## Database Migrations
Migrations are Alembic revisions in `welearn_database/alembic/versions`. Run them from a clone of this repository, after `poetry install`, not from the package installed from PyPI.

### Setup
- Create one file per environment at the root of the repository, copied from `.env.example`: `.env.dev`, `.env.staging`, `.env.prod`. Only `PG_HOST`, `PG_DB` and the credentials change between them. `PG_DB` is the database name (the API calls it `PG_DATABASE`).
- These files are git-ignored. Keep them private with `chmod 600 .env.*`.
- Pick the database with `-x env=<name>`, which loads `.env.<name>`. The flag goes before the subcommand: `poetry run alembic -x env=staging current`. The file's values override variables exported in your shell.
- Without `-x env`, `env.py` loads `.env` (handy for a local database), and a variable already exported in your shell wins. Check that `env | grep PG_` prints nothing, or only the values you expect.
- The dev and staging databases need the VPN.
- The Scaleway database isn't reachable from your machine, so it has no `.env` file. See [Scaleway dev](#scaleway-dev-run-the-sql-in-pgadmin).

### Check where the database is
```bash
poetry run alembic -x env=dev current   # revision the database is at
poetry run alembic heads                # latest revision in this repository
poetry run alembic history              # full chain
```
`env.py` prints the target first, for example `Target: staging -> <host>/welearn_datastack_staging`. For `prod`, or a host with `prod` in its name, it asks you to type the environment name before it connects.

The staging database has no `alembic_version` table yet, so `current` prints no revision there. Before its first `upgrade`, check which revision its schema matches and record it with `poetry run alembic -x env=staging stamp <revision>`. `stamp` changes nothing but `alembic_version`.

### Preview the SQL (`--sql`, nothing is applied)
```bash
poetry run alembic -x env=dev upgrade 1_5_6:1_5_7 --sql > 1_5_7.sql
```
- Offline mode only writes the SQL out. It doesn't connect to the database, doesn't change it, and doesn't update `alembic_version`. The SQL is the same for every environment, so any `-x env` works.
- It needs a `from:to` range, because it can't read the database's current revision.
- If you see `-- Running upgrade 1_5_6 -> 1_5_7` followed by SQL, nothing was applied.
- If you run the file by hand (psql, DBeaver…), it ends with `UPDATE alembic_version …`. That table lives in the `public` schema.

### Apply the migration
```bash
poetry run alembic -x env=staging upgrade 1_5_7   # or: upgrade head
poetry run alembic -x env=staging current         # should print 1_5_7
```
- Upgrading to a named revision runs only what you expect.
- A real run logs `INFO … Running upgrade 1_5_6 -> 1_5_7, …` and prints no SQL.

### Roll back
```bash
poetry run alembic -x env=staging downgrade 1_5_6
```
This runs the revision's `downgrade()`. For `1_5_7`, that drops the `feature`, `thread` and `guest_feature_usage` tables.

### Scaleway dev: run the SQL in pgAdmin
The Scaleway database is only reachable from inside the cluster, so Alembic can't connect to it. Generate the SQL locally and run it in the cluster's pgAdmin:
1. In pgAdmin, check where the database is:
   ```sql
   SELECT version_num FROM public.alembic_version;
   ```
2. Generate the SQL from that revision to the target one. Nothing connects: `-x env=dev` only fills in the URL Alembic needs.
   ```bash
   poetry run alembic -x env=dev upgrade 1_5_6:1_5_7 --sql > 1_5_7.sql
   ```
3. Read the file, then paste it into pgAdmin's Query Tool on the Scaleway database and run it. It is wrapped in `BEGIN;` … `COMMIT;`, so it applies fully or not at all, and it ends with `UPDATE public.alembic_version …`.
4. Run the query from step 1 again: it should print the target revision.

To roll back, generate the downgrade the same way, with the range reversed: `poetry run alembic -x env=dev downgrade 1_5_7:1_5_6 --sql > 1_5_7_down.sql`.

### Order across environments
Migrate dev (Azure with `-x env=dev`, Scaleway through pgAdmin), then staging (`-x env=staging`), then prod (`-x env=prod`). An environment must be migrated before an API version that uses the new tables is deployed there. A migration that only adds tables, like `1_5_7`, doesn't break an older API running on the migrated database.

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