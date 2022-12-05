import os
from typing import Dict
from prometheus_client import start_http_server, Gauge
import gitlab
import time
import logging as log
import yaml
from yaml.loader import SafeLoader
import fnmatch
from timeit import default_timer as timer

gauge = Gauge(
    "gitlab_ci_job_status",
    "Job status, 0 = success, 1 = failed (& everything else), 2 = in-progress",
    ["project", "job"],
)
log.basicConfig(level=log.INFO)


def poll_gitlab(gl: gitlab.Gitlab, jobs_config: dict[str, list[str]]):

    # {
    #   projectName: {
    #       jobName: <Job>
    #   }
    # }
    latest_unique_jobs = {}

    # Get jobs for each project
    for project_name, job_patterns in jobs_config.items():
        log.debug(f"Polling {project_name}")
        try:
            project = gl.projects.get(project_name)

            latest_unique_jobs[project_name] = {}

            # Jobs are sorted in descending order of their IDs.
            # Hence jobs will be from the latest to the oldest
            jobs = project.jobs.list(per_page=100)


            for job in jobs:
                job_name = job.attributes["name"]

                # We only care about the latest. Latest being the first to be seen, hence we check if we've already seen this job
                if job_name in latest_unique_jobs[project_name]:
                    continue

                # Matching
                for job_pattern_matcher in job_patterns:
                    if fnmatch.fnmatch(job_name, job_pattern_matcher):
                        latest_unique_jobs[project_name][job_name] = job

        except gitlab.GitlabError as e:
            log.error(f"Skipping {project_name} because {e}")

    # Process collected data and expose status metric
    for project_name, jobs_in_project in latest_unique_jobs.items():
        for job_name, job in jobs_in_project.items():
            match job.attributes["status"]:
                case "success":
                    gauge.labels(project=project_name, job=job_name).set(0)
                case "pending":
                    gauge.labels(project=project_name, job=job_name).set(2)
                case _:
                    gauge.labels(project=project_name, job=job_name).set(1)


def parse_config(config_path: str) -> dict[str, list[str]]:

    # jobs_config = {
    #   projectName: [jobName1, jobName2]
    # }
    jobs_config = {}

    with open(config_path) as f:
        data = yaml.load(f, Loader=SafeLoader)
        for project in data:
            project_name = project["project"]
            jobs = project["jobs"]
            jobs_config[project_name] = jobs

    return jobs_config


if __name__ == "__main__":

    token = os.getenv("GITLAB_TOKEN", "")
    gl = gitlab.Gitlab(url="https://gitlab.com", private_token=token)

    # jobs_config = {
    #   projectName: [jobName1, jobName2]
    # }
    config_path = "config/config.yaml"
    jobs_config = parse_config(config_path)

    # Start up the server to expose the metrics.
    start_http_server(9090)

    while True:
        start = timer()
        poll_gitlab(gl, jobs_config)
        end = timer()
        log.info(f"Polling GitLab took {end-start} seconds") 
        time.sleep(10)
