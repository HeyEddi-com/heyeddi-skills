# Examples

## First run

```bash
python scripts/list_questions.py --project-root /path/to/app --missing-only

python scripts/write_setup.py --project-root /path/to/app --json '{
  "git.preset": "main_staging_dev",
  "git.custom_workflow": null,
  "git.worktrees": false,
  "agent.commit": "ask",
  "agent.push": "ask"
}'

python scripts/verify_setup.py --project-root /path/to/app --check
```

## Custom workflow escape hatch

```bash
python scripts/write_setup.py --project-root /path/to/app --json '{
  "git.preset": "main_dev",
  "git.custom_workflow": "gitflow: feature → develop → release → main",
  "git.worktrees": true,
  "agent.commit": "ask",
  "agent.push": "ask"
}'
# preset becomes custom; custom_workflow stores the description
```
