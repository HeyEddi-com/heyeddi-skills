# Examples: Local first

User: "We are going to move the calendar account to another Google account."

Do: edit the Terraform or config that names the account. Run `terraform plan`. Summarize which resources the plan would change, then continue: commit, push, and open the PR. The apply runs where `check_permission.py` allows it.

Do not: swap the account with `gcloud`, GAM, or Calendar API writes, or apply to a target `check_permission.py` denies.

User: "What would production do if we remove the old service account?"

Do: `terraform plan`. Warn with the plan's create, change, and destroy lines.

Do not: `terraform apply -auto-approve` or `terraform state rm`.
