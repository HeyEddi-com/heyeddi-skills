# Vocabulary: Local first

- Plan: `terraform plan`, `tofu plan`, `pulumi preview`, or `ansible-playbook --check`. Shows the live diff. Does not apply it.
- Live change: any command that creates, updates, or deletes cloud, cluster, Firebase, or Workspace resources.
- Gate: `classify_command.py --check`. Exit 1 means every agent must not run the command. Plan exits 0 and requires a warning.
- Deploy path: the project's reviewed pipeline. For HeyEddi CI that is Cloud Build step `terraform-release` after merge.
