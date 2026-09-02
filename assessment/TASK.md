# BARQ Systems — DevOps Internship Acceptance Task

**Due date:** __________________________

You are taking over a small application that is not operating reliably. Every candidate receives this identical starter revision, instructions and historical log. The number and types of hidden issues are not disclosed. Your objective is to diagnose, restore, operate and explain the supplied environment.

## Stage 1 — Investigate

- Preserve the supplied baseline in your own GitHub repository. Make progressive, meaningful commits while working; do not submit only a final bulk upload or manufacture timestamps.
- Reproduce symptoms. Analyze `logs/application.log` using Bash, Python and/or Linux tools. Provide commands/scripts, output, counts or a timeline and evidence-backed conclusions.
- Keep a chronological troubleshooting report: symptom, hypothesis, test/command, observed result, unsuccessful attempts, root cause, fix and retest. Link findings to commits. Document failed attempts honestly; do not invent them.

## Stage 2 — Restore and operate

- Implement Docker and Docker Compose for the supplied application and SQL database. Preserve the real SQL-backed behavior in the application contract.
- Start with two separate application instances behind NGINX, used as a reverse proxy and load balancer.
- Configure Docker networking and service connectivity. Make instance identity visible so repeated requests prove both instances serve traffic.
- Implement meaningful health checks and failure handling. Test application and health endpoints, stop one instance, demonstrate continued service through NGINX, then recover it and show it serving traffic again.
- Explain timeout, retry, failure-detection and recovery choices. Report request results and any transient errors rather than hiding them.

## Stage 3 — Validate and run CI

- Write one repeatable Bash/Python validation command that checks endpoints, instance distribution, one-instance failure, continued availability and recovery. Use bounded waits, clear PASS/FAIL results and a non-zero exit status when an expectation fails.
- Build a basic GitHub Actions pipeline for pushes and pull requests that builds the image, starts the Compose environment and runs validation. Supply a run link for the submitted commit.

## Stage 4 — Document and preserve evidence

- Complete the README with setup, start/stop, validation and endpoint-test commands, failure/recovery behavior and links to all evidence.
- Provide an architecture diagram showing NGINX, instances, Docker networks, exposed ports and request flow.
- Supply the detailed troubleshooting/log-analysis report, including failed hypotheses and the evidence that changed your next step.
- Maintain a technical decision log with alternatives and trade-offs.
- Disclose AI tools used, their purpose, affected work and how you verified it. State `None` if none were used. Be able to explain every submitted change.
- Preserve genuine Git development history. Link report entries and video changes to commits. Evaluators inspect diffs, timing and progress, not commit count alone.

## Stage 5 — Continuous 8–12 minute technical video

Record a readable screen and actual terminal execution with live narration. No cuts, pauses, editing, speed-up or voice replacement. Slides, screenshots and prerecorded output cannot replace the demonstration.

In that single recording:

1. Identify your repository and starting commit; run `git status`. Start the Compose environment from stopped containers and show services. Images may be prebuilt.
2. Test the application and health endpoints. Send repeated requests through NGINX and show both instances responding.
3. Stop one application instance. Continue requests, demonstrate service availability and any errors, then recover it and prove it serves traffic again.
4. Run your validation script and explain the output. Demonstrate one historical-log finding using the terminal.
5. Make a configuration change on screen, explain it, show `git diff`, apply it and test its effect. Also add a third application instance during the recording and prove requests reach all three.
6. Rerun validation for the changed environment. Run `git status` and `git diff` before committing. Commit the video changes on screen and show the hashes. Push those commits before submission.

## Submit

GitHub repository URL, final commit hash, accessible video URL, CI run URL, README, diagram, troubleshooting report, decision log, AI disclosure and an evidence index mapping requirements to files/commits/video timestamps. The README and diagram must match the final three-instance state.

## How it is assessed

| Area | Points |
| --- | ---: |
| Troubleshooting and log analysis | 30 |
| Git development history | 25 |
| Recorded technical demonstration | 25 |
| Implementation and automation | 15 |
| Documentation and decisions | 5 |
| **Total** | **100** |

Understanding and verifiable evidence matter more than the final working state alone. Credible incomplete work can earn partial credit. GitHub, video and documentation are the main filtering evidence, and their consistency establishes ownership. AI disclosure is required; AI detection tools are not relied on.

Missing/inaccessible required evidence, a missing or non-compliant video, omitted mandatory live actions, or material contradictions/fabrication that make ownership/results unverifiable are hard-fail grounds. An honestly shown failed technical attempt is scored; it is not automatically treated as an omitted action. Timing or AI use alone does not prove misconduct.
