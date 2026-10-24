# Examples: Local first

User: "We are going to move the calendar account to another Google account."

Do: edit the Terraform or config that names the account. Run `terraform plan`. Tell the user which resources the plan would change. Stop.

Do not: `gcloud`, GAM, Calendar API writes, or `terraform apply`.

User: "What would production do if we remove the old service account?"

Do: `terraform plan`. Warn with the plan's create, change, and destroy lines.

Do not: `terraform apply -auto-approve` or `terraform state rm`.
