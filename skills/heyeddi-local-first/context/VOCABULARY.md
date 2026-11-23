# Vocabulary: Local first

- Plan: `terraform plan`, `tofu plan`, `pulumi preview`, or `ansible-playbook --check`. Shows the live diff. Does not apply it.
- Live change: any command that creates, updates, or deletes cloud, cluster, Firebase, or Workspace resources.
- Gate: `check_permission.py --check`. Exit 0 allow, 2 ask once, 1 deny. Uses `classify_command.py` to spot infra writes. Plan exits 0 and requires a summary.
- Preset: `agent.preset` in `.heyeddi/stack.json` (`cautious`, `balanced`, `autonomous`). Missing means `balanced`.
- Deploy path: the project's reviewed pipeline. For HeyEddi CI that is Cloud Build step `terraform-release` after merge.
