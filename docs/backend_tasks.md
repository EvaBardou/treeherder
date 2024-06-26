# Backend tasks

## Running the tests

You can run the linter and the pytest suite inside Docker, using:

```bash
docker-compose run backend ./runtests.sh
```

Or for more control, run each tool individually, by first running:

```bash
docker-compose run backend bash
```

...which saves having to wait for docker-compose to spin up for every test run.

`yarn build` will generate a `.build` directory which will be seen within the `backend` container.
If you don't have `yarn` working on your host you can run this instead `docker-compose run frontend sh -c "yarn && yarn build"`

Then run the individual tools within that shell, like so:

- [pytest](https://docs.pytest.org/en/stable/):

  ```bash
  pytest tests/
  pytest tests/log_parser/test_tasks.py
  pytest tests/etl/test_job_loader.py -k test_ingest_pulse_jobs
  ```

  To run all tests, including slow tests that are normally skipped, use:

  ```bash
  pytest --runslow tests/
  ```

  For more options, see `pytest --help` or <https://docs.pytest.org/en/stable/usage.html>.

- [Ruff](https://docs.astral.sh/ruff/):

  ```bash
  ruff check .
  ```

## Hide Jobs with Tiers

To hide jobs we use the job's `tier` setting. Jobs with `tier` of 3 are
hidden by default. For TaskCluster, edit the task definition to include the
`tier` setting in the Treeherder section.

## Profiling API endpoint performance

On our development (vagrant) instance we have [django-debug-toolbar] installed, which can
give information on exactly what SQL is run to generate individual API endpoints. Navigate
to an endpoint (example: <http://localhost:8000/api/repository/>) and you should see the
toolbar to your right.

[django-debug-toolbar]: https://django-debug-toolbar.readthedocs.io

## Connecting to Services Running inside Docker

Treeherder uses various services to function, eg Postgres, etc.
At times it can be useful to connect to them from outside the Docker environment.

The `docker-compose.yml` file defines how internal ports are mapped to the host OS' ports.

In the below example we're mapping the container's port 5432 (Postgres's default port) to host port 5432.

```yaml
# This is a line from the docker-compose.yml file
ports:
  - '5432:5432'
```

<!-- prettier-ignore -->
!!! note
    Any forwarded ports will block usage of that port on the host OS even if there isn't a service running inside the VM talking to it.

With Postgres exposed at port 5432 you can connect to it from your host OS with the following credentials:

- host: `localhost`
- port: `5432`
- user: `postgres`
- password: `mozilla1234`

Other services running inside the Compose project, can be accessed in the same way.

## Releasing a new version of the Python client

- Determine whether the patch, minor or major version should be bumped, by
  inspecting the [client Git log].
- File a separate bug for the version bump.
- Open a PR to update the version listed in [client.py].
- Use Twine to publish **both** the sdist and the wheel to PyPI, by running
  the following from the root of the Treeherder repository:

  ```bash
  > pip install -U twine wheel
  > cd treeherder/client/
  > rm -rf dist/*
  > python setup.py sdist bdist_wheel
  > twine upload dist/*
  ```

- File a `Release Engineering::Buildduty` bug requesting that the sdist
  and wheel releases (plus any new dependent packages) be added to the
  internal PyPI mirror. For an example, see [bug 1236965].

[client git log]: https://github.com/mozilla/treeherder/commits/master/treeherder/client
[client.py]: https://github.com/mozilla/treeherder/blob/master/treeherder/client/thclient/client.py
[bug 1236965]: https://bugzilla.mozilla.org/show_bug.cgi?id=1236965
