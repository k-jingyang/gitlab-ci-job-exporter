import os
from typing import Dict
from prometheus_client import start_http_server, Gauge
import gitlab
import time
import logging as log

gauge = Gauge('gitlab_ci_job_status', 'Job status, 0 = success, 1 = failed (& everything else), 2 = in-progress', ["project", "job"])

def poll_gitlab(gl: gitlab.Gitlab, jobs_config: dict[str, str]):

    # {
    #   projectName: {
    #       jobName: <Job>
    #   }
    # }
    latest_unique_jobs = {}

    # Get jobs for each project
    for project_name, jobs_to_find in jobs_config.items():
        try:
            project = gl.projects.get(project_name)

            latest_unique_jobs[project_name] = {}

            # Jobs are sorted in descending order of their IDs.
            # Hence jobs will be from the latest to the oldest
            jobs = project.jobs.list(per_page=100)
            jobs_to_find = set(jobs_to_find)

            for job in jobs:
                job_name = job.attributes["name"]
                # We only care about the latest, hence we check if we've already seen this job
                if job_name in jobs_to_find and job_name not in latest_unique_jobs[project_name]:
                    latest_unique_jobs[project_name][job_name] = job

        except gitlab.GitlabError as e:
            log.error(f"Skipping {project} because {e}")

    # Process collected data and expose status metric
    for project_name, jobs_in_project in latest_unique_jobs.items():
        for job_name, job in jobs_in_project.items():
            if job.attributes['status'] == "success":
                gauge.labels(project=project_name,job=job_name).set(0)
            else:
                gauge.labels(project=project_name,job=job_name).set(1)

if __name__ == '__main__':

    token = os.getenv("GITLAB_TOKEN", "")
    gl = gitlab.Gitlab(url='https://gitlab.com', private_token=token)

    # projectName: [jobName1, jobName2]
    jobs_config = {
        "k.jingyang/pipeline-test" : [ "rpm", "debian" ]
    }

    # Start up the server to expose the metrics.
    start_http_server(9090)

    while True:
        poll_gitlab(gl, jobs_config)
        time.sleep(10)

