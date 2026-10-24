# Anti-patterns: Local first

- Running `terraform apply`, `terraform destroy`, or `terraform import` from the agent because the user described a future change.
- Swapping a Google or calendar account with `gcloud`, GAM, or a Google API write instead of editing Terraform or config.
- Hiding apply inside `bash -c`, `python -c`, a shell script, or an MCP argument.
- Treating `terraform plan` as permission to apply after the plan looks small.
- Skipping the warning. After a plan, name what would be created, changed, or destroyed.
