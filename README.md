
## GitLab Job Exporter

Expose the status of GitLab CI jobs as Prometheus metrics
## Why not `gitlab-ci-pipelines-exporter`?

[`gitlab-ci-pipelines-exporter`](https://github.com/mvisonneau/gitlab-ci-pipelines-exporter) only gives information about latest pipeline. It is close to impossible to obtain metrics on different pipelines with different sets of jobs that run in the same project.

`gitlab-ci-pipelines-exporter` should still be the go-to tooling to give an overview of the latest pipelines.

## Requirements

1. Able to get the status of GitLab CI jobs (even from child pipelines)
1. Able to configure jobs to look out for
   - e.g. Give me the status of this job in its latest run 
2. Able to use multiple tokens to scrape multiple projects
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


## To-Do
- [ ] Garbage collection
- [ ] Use CLI library
- [ ] Enable multiple GitLab tokens
- [ ] Setup vscode formatting
- [ ] Setup `setup.cfg`
- [x] Log poll latency
- [ ] Configure DEBUG logging (and add CLI param for toggling log level)