# Github analytics visualisation in Grafana through Elasticsearch
Visualization of Github analytics using Grafana, with Elasticsearch as datastore

![Flow diagram](https://github.com/Kondasamy/github-analytics-on-grafana-with-es/raw/master/dashboards/Untitled%20Diagram.png "Flow diagram")


1. With the usage of **Github V3 API**, collected related statistical data ad posted to **Elasticsearch** datasource. Then on top of it, used **Grafana** for data visualization.
2. Below are the **dashboard panels** I have constructed,
   * Comparison of Last 7 days commit activity of the popular ML library repos (tensorflow, theano, scikit & keras)
**Source:** Github API to get number of commits per hour in each day
[GET /repos/:owner/:repo/stats/punch_card]
   * Simple table which aggregates the total commits done on each repositories
   * Individual contributor wise changes (addition, deletion & commits) on each repository till date with weekly timeline
**Source:** Github API to get contributors list
[GET /repos/:owner/:repo/stats/contributors]

## Elasticsearch health check displaying document size
![Elasticsearch healthcheck](https://github.com/Kondasamy/github-analytics-on-grafana-with-es/raw/master/dashboards/Elasticsearch%20healthcheck.png "Elasticsearch healthcheck")

## Grafana dashboard
![Grafana](https://github.com/Kondasamy/github-analytics-on-grafana-with-es/raw/master/dashboards/Grafana%20dashboard.png "Grafana")
