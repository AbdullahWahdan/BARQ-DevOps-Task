# Historical incident evidence

`application.log` is a deterministic, synthetic training fixture, not real customer data. All candidates receive the exact same file. It represents a historical staging window on **2026-08-20, UTC**, with normalized application and edge records.

Each line is an independent JSON object. `timestamp`, `level`, `service` and `event` are always present. Request records may include `request_id`, `instance_id`, `method`, `path`, `status` and `duration_ms`; edge records may additionally include an upstream and an error. Fields that do not apply to an event can be absent. There are request events and operational events: do not assume every line is one user request or count correlated edge/application records as two user requests.

The file is historical evidence, not a transcript of the starting containers and not an inventory of current hidden issues. Preserve it unchanged. Generate current environment logs separately and distinguish observations, correlations and hypotheses in your report.

Analyze it with tools of your choice and submit reproducible commands/scripts plus conclusions. No analysis answer or expected totals are provided in the student package.
