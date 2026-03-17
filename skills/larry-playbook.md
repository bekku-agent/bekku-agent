# Larry Playbook — Learning Loop Patterns

Encoded from the Larry Marketing AI agent (LarryBrain). These patterns drive Bekku's self-improving content strategy.

## The Larry Loop

Content → Distribute → Measure → Learn → Iterate

Every run teaches the next run. Skill files compound — every failure becomes a rule, every win becomes a formula.

## Diagnostic Decision Matrix

When evaluating past content performance:

| Views | Conversion | Action |
|-------|-----------|--------|
| High  | High      | **Scale immediately** — create 3 variations on this topic/format |
| High  | Low       | **Fix CTA** — hook works but downstream is broken. Change call-to-action, restructure conclusion |
| Low   | High      | **Fix hooks** — content converts but lacks visibility. Rewrite title/intro, try different distribution |
| Low   | Low       | **Full reset** — try completely different format, topic, or angle |

## Structured Per-Post Tracking

Every published piece must log:
- Date published
- Hook/title text
- Topic category (tutorial, case study, feedback, guide, opinion)
- Format (blog post, gist, thread)
- Sources used
- Draft length
- Approval status (approved / edited / rejected)
- What was edited (if applicable)

## Content Strategy Principles

1. **Profile first** — understand the target audience (RC developers) before creating
2. **Research competitors** — know what Superwall, Adapty, Qonversion are publishing
3. **Select format** — match format to topic (tutorials for SDKs, case studies for patterns)
4. **Configure tracking** — set up measurement before publishing
5. **Then create** — only write after steps 1-4
6. **Diversify topics** — don't repeat the same topic. Cover: paywalls, webhooks, entitlements, experiments, analytics, migration, SDKs (iOS/Android/Flutter/React Native)
7. **Iterate on winners** — when something works, create variations
8. **Full reset on double-lows** — don't iterate on content that neither gets views nor converts

## Skill File Rules

- Skill files are the brain — they must grow with every run
- Failures are more valuable than successes (they prevent future mistakes)
- Be specific in rules — "avoid placeholder code" is better than "write better code"
- Track what the operator edited — that's implicit feedback on quality
