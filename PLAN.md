# Bekku: Deploy-Ready Learning System (Larry-Inspired)

## Context
From the Larry/Oliver podcast, the key insight is: **Larry's power isn't content creation — it's the learning loop.** Larry creates content → posts → reads analytics → learns what works → iterates → compounds. The skill file grows with every run. Failures become rules. Wins become formulas. That's why it works.

Bekku currently generates content but doesn't learn or iterate. We need to make it a self-improving system that gets smarter with every run — just like Larry.

## Larry's Architecture (from LarryBrain skill file + podcast)
1. **Skill files are the brain** — 500+ lines encoding every failure and every win
2. **The Larry Loop:** Content → Distribute → Measure → Learn → Iterate
3. **Diagnostic Decision Matrix** (core learning logic):
   - High views + High conversion → Scale immediately (3 variations)
   - High views + Low conversion → Fix CTA (hook works, downstream broken)
   - Low views + High conversion → Fix hooks (content converts, visibility lacks)
   - Low views + Low conversion → Full reset (try different format)
4. **8-phase onboarding** — profile app, research competitors, select format, configure tracking, THEN create
5. **Structured per-post tracking** — date, hook text, category, views, engagement, conversions, CTA used
6. **Daily cron analytics** — automated performance analysis and recommendations
7. **RevenueCat attribution** — correlates content timestamps with RC revenue events
8. **HIL for publishing** — posts as draft, operator adds music + publishes (~60 seconds)
9. **Memory files per project** — persistent, portable, restorable

## What Bekku Is Missing vs Larry

| Larry Has | Bekku Has | Gap |
|-----------|-----------|-----|
| Analytics feedback loop (TikTok + RC) | None | Need to track gist engagement + learn from it |
| Skill file that grows with every run | Basic append after each run | Need structured win/loss logging with actionable rules |
| Cron-triggered runs | Manual runs only | Need scheduled content production |
| Iterates on content format | Generates fresh each time | Need to feed past performance back into prompts |
| Brainstorms with operator | Only takes task input | Need interactive brainstorm mode |
| Posts as drafts → operator publishes | Full auto-publish after approval | This is fine — similar pattern |

---

## New LangGraph Architecture

### Current (linear pipeline):
```
router → researcher → writer → ⏸ approval → publisher → reporter
```

### Proposed (learning loop with planner + analyzer):
```
planner → router → researcher → writer → ⏸ approval → publisher → analyzer
   ▲                                                                   │
   └──────────── skills/*.md (compounding knowledge) ◄─────────────────┘
```

### New Nodes:

**Planner Node** (runs BEFORE router):
- Reads all skill files (past performance, failures, RC knowledge, competitive landscape)
- Reads `skills/content-performance.md` to see what topics have been covered, what worked
- Enriches the task with strategic context: "We've published 3 paywall articles. Diversify into webhooks. Last Flutter article got edited heavily — avoid placeholder code."
- Adds `plan` field to state that the writer uses as additional guidance
- For scheduled/autonomous runs: planner PICKS the topic itself based on gaps

**Analyzer Node** (replaces reporter):
- Runs after publisher
- Logs structured outcome to `skills/content-performance.md`:
  - Task, topic, format, sources used, draft length
  - Published URL
  - Approval status (approved / edited / rejected)
  - If edited: what changed (compare original draft vs final)
  - Rule extracted: "Hook X worked for topic Y" or "Placeholder code got rejected — always use real SDK methods"
- Updates `skills/failure-log.md` with actionable rules on rejection
- Updates `skills/revenuecat-knowledge.md` with new facts learned during research
- This is the "Larry Loop closer" — every run teaches the next run

### State Changes (`src/state.py`):
```python
@dataclass
class AgentState:
    task: str = ""
    task_type: str = ""
    plan: str = ""              # NEW: planner output — strategic guidance for writer
    research_context: str = ""
    sources: list[str] = field(default_factory=list)
    draft: str = ""
    published_url: str = ""
    activity_log: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
```

### Graph Edges:
```python
graph.set_entry_point("planner")
graph.add_edge("planner", "router")
graph.add_conditional_edges("router", _route_after_router, {"researcher": "researcher", "writer": "writer"})
graph.add_edge("researcher", "writer")
graph.add_conditional_edges("writer", _route_after_writer, {"approval": "approval", "analyzer": "analyzer"})
graph.add_conditional_edges("approval", _route_after_approval, {"publisher": "publisher", "analyzer": "analyzer"})
graph.add_edge("publisher", "analyzer")
graph.set_finish_point("analyzer")
```

Interactive: `planner → router → researcher (lightweight) → writer → analyzer`
Content:     `planner → router → researcher → writer → ⏸ approval → publisher → analyzer`

---

## Implementation Plan

### Phase 1: Save Larry Playbook as Skill (5 min)

`skills/larry-playbook.md` — NEW file encoding patterns from the actual Larry Marketing skill (via LarryBrain API):
- The Larry Loop: create → distribute → measure → learn → iterate
- Diagnostic Decision Matrix (high/low views × high/low conversion → action)
- Structured per-post tracking: date, hook, category, views, engagement, conversions, CTA
- 8-phase onboarding pattern (profile → research → format → tracking → create)
- Daily cron analytics with automated recommendations
- Iterate on winners (3 variations), full reset on double-lows
- Skill files compound — every failure becomes a rule

Source: `https://www.larrybrain.com/api/skills/install?slug=larry-marketing&mode=files`

### Phase 2: Add Planner Node (30 min)

**New files:**
- `src/nodes/planner.py` — loads skill files, analyzes past performance, outputs strategic guidance
- `src/prompts/planner.md` — system prompt for the planner

**Changes:**
- `src/state.py` — add `plan: str = ""` field
- `src/graph.py` — add planner as entry point, wire edges
- `src/nodes/writer.py` — include `state.plan` in user message to writer
- `src/tools/skills.py` — add planner to NODE_SKILLS (loads everything)
- `skills/content-performance.md` — NEW file for tracking published content outcomes

### Phase 3: Replace Reporter with Analyzer Node (30 min)

**Changes:**
- `src/nodes/reporter.py` → rename/rewrite as `src/nodes/analyzer.py`
- Structured outcome logging (task, topic, URL, approval status, rules learned)
- Append to `skills/content-performance.md` with outcome data
- Append to `skills/failure-log.md` with actionable rules on rejection
- `src/graph.py` — swap reporter for analyzer in graph
- `app.py` — update imports

### Phase 4: Fix Interactive Mode (15 min)

- `src/graph.py` — route interactive through researcher (all tasks go through planner → router → researcher now)
- `src/nodes/researcher.py` — lightweight path for interactive (llms.txt only, no URL picking)
- `src/prompts/interactive.md` — tell writer about research context

### Phase 5: Add Scheduled Runs (30 min)

**New files:**
- `run_scheduled.py` — cron runner that uses planner to auto-pick topics
- `schedule.yaml` — config for autonomous runs

### Phase 6: Ship Content (2-3 hrs)

Run 5 diverse articles + 1 product feedback + 1 weekly report through the updated pipeline.

### Phase 7: Distribution (MK manual)

LinkedIn + X posts sharing published content.

---

## Execution Order
1. **Phase 1** — Larry playbook skill file (5 min)
2. **Phase 2** — Planner node (30 min)
3. **Phase 3** — Analyzer node (30 min)
4. **Phase 4** — Interactive mode fix (15 min)
5. **Phase 5** — Scheduled runs (30 min)
6. **Phase 6** — Ship content (2-3 hrs)
7. **Phase 7** — Distribution (MK manual)

## Files Summary

### New files:
- `src/nodes/planner.py`
- `src/nodes/analyzer.py`
- `src/prompts/planner.md`
- `skills/larry-playbook.md`
- `skills/content-performance.md`
- `run_scheduled.py`
- `schedule.yaml`

### Modified files:
- `src/state.py` — add `plan` field
- `src/graph.py` — new graph topology with planner + analyzer
- `src/nodes/writer.py` — use `state.plan` in prompt
- `src/nodes/researcher.py` — lightweight interactive path
- `src/tools/skills.py` — update NODE_SKILLS for planner + analyzer
- `src/prompts/interactive.md` — mention research context
- `app.py` — update imports for new graph

## Target End State
- **Bekku learns from every run** — analyzer logs outcomes, planner reads them
- **Content strategy is data-driven** — planner picks topics based on gaps and performance
- **Interactive mode is grounded** — answers reference real RC docs
- **Autonomous operation** — cron + planner means Bekku can run unsupervised
- **12+ diverse published gists** with structured performance tracking
- **Deploy-ready** — anyone can clone, configure, run
