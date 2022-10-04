## Justification 

Why not use `gitlab-ci-pipelines-exporter`?

`gitlab-ci-pipelines-exporter` should still be used to give us an overview of all our latest pipelines, and developers will need this too

## Requirements

1. Able to get the status of GitLab CI jobs (even from child pipelines)
1. Able to use multiple tokens to scrape multiple projects
1. Able to configure jobs to look out for
   - e.g. Give me the status of this job in its latest run 

## Limitation
1. As it's not feasible to enumerate all jobs for each project, the search space will be restricted to the latest 100 jobs of each project

## Configuration
```yaml
- project: group/project
  jobs:
    - "job_name_1"
    - "job_name_2"
- project: group/project
  jobs:
    - "*"
```

## Output

```
# 0 = success, 1 = failed (& everything else), 2 = in-progress
gitlab_ci_job_status{project="group/project", job="job_name_1"} 0
```

## Edge cases

Previously scraped job does not exist in the latest 100 job
  - Metric to be garbage collected (i.e. not exposed)
