# Policy feed (living SSOT)

Do **not** maintain a duplicate knob table in this skill.

| Source | URL / path | Role |
|--------|------------|------|
| Machine contract | `https://cihook.heyeddi.com/api/public/eddi-ci-policy` | Knobs, rules, guide, minimal example |
| Human docs | `https://ci.heyeddi.com/docs#policy` | Narrative + UI tables |
| Backend SSOT | heyeddi-ci `backend/app/policy_insights.py` (`CONFIG_KNOBS`, `public_policy_contract`) | Code that serves the API |
| Frontend mirror | heyeddi-ci `src/content/policyReference.ts` | Docs site tables |

## Agent workflow

```bash
python .agents/skills/heyeddi-ci-config/scripts/load_policy_contract.py --project-root .
python .agents/skills/heyeddi-ci-config/scripts/inspect_repo.py --project-root .
```

Local override when developing against an unreleased schema:

```bash
export HEYEDDI_CI_ROOT=/path/to/heyeddi-ci
# or
export HEYEDDI_CI_POLICY_URL=http://localhost:8090/api/public/eddi-ci-policy
```
