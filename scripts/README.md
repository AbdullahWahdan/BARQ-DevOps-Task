# Candidate automation

Implement your environment-validation script here (Bash or Python). No completed validation implementation is supplied.

Document one command in the README. It must check the application and health endpoints, instance distribution, an application-instance failure, continued proxy availability and recovery. Use timeouts/bounded retries, report actual PASS/FAIL results, and exit non-zero if any required expectation fails. Restore an instance you stopped even if a check fails. Support testing both your two-instance setup and the final three-instance setup.

The application contract tests under `tests/` are separate from this deliverable. Add your basic GitHub Actions pipeline under `.github/workflows/` and run your validation from it.
