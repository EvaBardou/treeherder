import logging
import re

import environ
import newrelic.agent

from treeherder.model.models import MozciClassification, Push, Repository
from treeherder.utils.taskcluster import download_artifact, get_task_definition

env = environ.Env()
logger = logging.getLogger(__name__)

CLASSIFICATION_ROUTE_REGEX = re.compile(
    r"index\.project\.mozci\.classification\.(.+)\.revision\.([0-9A-Fa-f]+)"
)


class ClassificationLoader:
    def process(self, pulse_job, root_url):
        task_id = pulse_job["status"]["taskId"]

        task_definition = get_task_definition(root_url, task_id)
        assert (
            "routes" in task_definition and len(task_definition["routes"]) > 0
        ), "A route containing the push project and revision is needed to save the mozci classification"
        # Retrieving a Push object thanks to the project/revision parsed from the task first route
        try:
            push = self.get_push(task_definition["routes"][0])
        except (ValueError, Repository.DoesNotExist, Push.DoesNotExist):
            return

        # Downloading the artifact containing the classification generated by mozci for this push
        classification_json = download_artifact(root_url, task_id, "public/classification.json")

        # Saving the mozci classification in the database
        results = dict(MozciClassification.CLASSIFICATION_RESULT)
        classification = classification_json["push"]["classification"]
        assert (
            classification in results.keys()
        ), "Classification result should be a value in BAD, GOOD, UNKNOWN"

        logger.info(
            "Storing mozci classification calculated as %s for push %s on repository %s",
            classification,
            push.revision,
            push.repository.name,
        )
        MozciClassification.objects.create(
            push=push,
            result=classification,
            task_id=task_id,
        )

    def get_push(self, task_route):
        try:
            project, revision = CLASSIFICATION_ROUTE_REGEX.search(task_route).groups()
        except ValueError as e:
            logger.error(
                "Failed to parse the given route '%s' to retrieve the push project and revision: %s",
                task_route,
                e,
            )
            raise

        try:
            newrelic.agent.add_custom_parameter("project", project)

            repository = Repository.objects.get(name=project)
        except Repository.DoesNotExist:
            logger.info("Job with unsupported project: %s", project)
            raise

        try:
            newrelic.agent.add_custom_parameter("revision", revision)

            revision_field = 'revision__startswith' if len(revision) < 40 else 'revision'
            filter_kwargs = {'repository': repository, revision_field: revision}

            push = Push.objects.get(**filter_kwargs)
        except Push.DoesNotExist:
            logger.info("Job with unsupported revision: %s", revision)
            raise

        return push
