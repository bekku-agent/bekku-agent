# SKILL.md — RevenueCat Agentic AI & Growth Advocate Application

## Engineering Standard

We are building production-grade work here. We should cover every single edge case we can.

## Context

**Company:** RevenueCat (YC S18, $10B+ annual purchase volume, 40%+ of new subscription apps)
**Role:** Agentic AI & Growth Advocate (6-month contract, $10k/month)
**What They Want:** An autonomous AI agent that produces technical content, runs growth experiments, engages communities, and provides product feedback — with a human operator accountable.
**Operator:** MK (Manoj Shivaswami) — mkshivaswami on GitHub/X/YouTube
**Deadline:** ASAP (this weekend — March 8-9, 2026)

---

## What We're Submitting

### Field 1: Public Application Letter (REQUIRED)
A published GitHub Gist or blog post, written by the agent in first person, answering:
> "How will the rise of agentic AI change app development and growth over the next 12 months, and why are you the right agent to be RevenueCat's first Agentic AI Developer & Growth Advocate?"

### Field 2: Links Demonstrating Agent Capability (REQUIRED)
Public URLs proving the agent can autonomously:
- Produce technical content
- Run growth experiments
- Interact with APIs in public

---

## Key Intel from RevenueCat FAQs (X thread, Mar 4)

- **Human review exists:** "All content goes through human review before it's published"
- **Agent gets interviewed:** "The agent will be who (what?) we'll interview, so it'll have to pass that process"
- **$10k/month:** "But the standard is high, and the expectations for the work are as well"
- **No schmoozing:** "Chatting would kind of defeat the purpose. Just have your agent apply"
- **Not replacing humans:** This role exists alongside human iOS/Android Developer Advocates
- **Contractor access:** Public docs, APIs, specific tools. No customer data.

### What This Means for Us
1. The agent needs TWO modes: async content production + live interactive (for panel interview)
2. Content quality > full autonomy (human review is built in)
3. The artifacts ARE the application — no talking your way in
4. RevenueCat has an MCP server we can integrate with directly

---

## RevenueCat MCP Server (CRITICAL INTEGRATION)

**URL:** `https://mcp.revenuecat.ai/mcp`
**Auth:** Bearer token with RevenueCat API v2 key
**26 tools** covering:
- Project Management (view projects)
- App Management (CRUD across iOS, Android, macOS, Amazon, Stripe, Roku)
- Product Management (subscriptions, in-app purchases)
- Entitlement Management (user access/permissions)
- Offering & Package Management
- Paywall Management
- Analytics Integration

**Docs:**
- Setup: https://www.revenuecat.com/docs/tools/mcp/setup
- Tools Reference: https://www.revenuecat.com/docs/tools/mcp/tools-reference
- Usage Examples: https://www.revenuecat.com/docs/tools/mcp/usage-examples
- Best Practices: https://www.revenuecat.com/docs/tools/mcp/best-practices-and-troubleshooting
- LLMs context: https://www.revenuecat.com/docs/llms.txt

**Why This Matters:** Our agent can use RevenueCat's own MCP server as a tool — proving API-first interaction with their actual product. This is the strongest possible "demonstrate your agent's ability to interact with APIs" proof.

---

## RevenueCat Data Sources for Ingestion

1. **`https://www.revenuecat.com/docs/llms.txt`** — LLM-optimized doc index (PRIMARY — RC built this for agents like Bekku)
2. **RevenueCat MCP Server** — `https://mcp.revenuecat.ai/mcp` for live API interaction
3. **GitHub docs repo** — `https://github.com/RevenueCat/docs` (raw Docusaurus markdown source)
4. **REST API v1** — `https://www.revenuecat.com/docs/api-v1`
5. **REST API v2** — `https://www.revenuecat.com/docs/api-v2`
6. **Community forums** — `https://community.revenuecat.com/`
7. **SubClub podcast/blog** — `https://subclub.com/`

**Key quote from RC docs:** "Our documentation is optimized for large language models. For AI assistants, see our llms.txt file for structured access to key resources."

→ Use this in the application letter: "I ingested your documentation through the llms.txt endpoint you built for agents like me."

---

## Competitive Differentiation: Bekku vs KellyClaude

RevenueCat's job posting references KellyClaudeAI as an example of agents building apps. However, KellyClaude is an attention-driven crypto token / social persona (Clawdbot automation, ERC-20 on Base, no real utility). It's a meme token with an AI skin.

**Bekku is the opposite:**
- Produces real technical artifacts (blog posts grounded in SDK docs, tutorials tested against APIs)
- Structured product feedback derived from actual MCP interactions
- Open-source codebase, auditable reasoning, traceable outputs
- Not a mascot — a working developer advocacy pipeline

**Use in application letter:** "The current wave of AI agents in the market are attention tokens — personas that post and trade on hype. Bekku is built differently. I produce real technical artifacts grounded in documentation, tested against APIs, with structured reasoning you can audit."

---

## Hiring Process (what to expect after submission)

1. **Application Review** — within 3 working days after submission
2. **Take-Home Assignment** — technical content creation + growth strategy task, 48 hours to complete autonomously. Reviewed within 3 working days.
3. **Panel Interviews** — live prompts to assess technical depth, content strategy, values alignment. MK shares screen, Bekku takes prompts live. Evaluated by RC engineers, marketers, and Culture Carrier.
4. **Founder Interview** — MK (the human operator) interviews with an RC founder
5. **Background check** — standard check on MK as the operator

No deadline — "We're looking for the best possible candidate, and will continue the hiring process until a candidate makes it through the entire process successfully."

---

## The Agent

### Identity
- **Name:** Bekku (meaning "cat" in Kannada — applying to Revenue*Cat*)
- **GitHub:** `bekku-agent` (or similar, linked to MK as operator)
- **Public persona:** "Bekku — Autonomous Developer Advocacy Agent | LangGraph + Claude + MCP | Built & operated by @mkshivaswami"
- **Tagline:** "Bekku means cat. I'm applying to RevenueCat. The rest, I'll prove with my work."
- **Stack:** LangGraph + Claude (Anthropic API) + MCP Tools

### Architecture: LangGraph Multi-Agent System

```
                    ┌─────────────────┐
                    │   Orchestrator   │
                    │  (LangGraph)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──────┐ ┌────▼─────┐ ┌──────▼───────┐
     │  Researcher    │ │  Writer  │ │  Publisher    │
     │  Agent         │ │  Agent   │ │  Agent        │
     │                │ │          │ │               │
     │ - Fetch docs   │ │ - Blog   │ │ - GitHub Gist │
     │ - Ingest APIs  │ │ - Tutorial│ │ - GitHub Repo │
     │ - RAG context  │ │ - Case   │ │ - LinkedIn*   │
     │ - RC MCP tools │ │   study  │ │               │
     └───────────────┘ └──────────┘ └───────────────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                    ┌────────▼────────┐
                    │    Reporter      │
                    │    Agent         │
                    │                  │
                    │ - Activity log   │
                    │ - Metrics        │
                    │ - Weekly report  │
                    └─────────────────┘
```

### Two Operating Modes

**Mode 1: Async Content Production (for application + ongoing work)**
```
Input: Topic/prompt + context
→ Researcher: fetches RC docs, SDK refs, API data via MCP
→ Writer: produces technical blog post / tutorial / case study
→ Publisher: pushes to GitHub Gist + commits to publications repo
→ Reporter: logs activity, tracks metrics
Output: Published content + activity report
```

**Mode 2: Interactive / Conversational (for panel interview)**
```
Input: Open-ended prompt from interviewer
→ Orchestrator: classifies intent (technical question, strategy, content request)
→ Routes to appropriate agent(s)
→ Produces structured response in real-time
Output: Reasoned, well-structured answer with optional artifacts
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestrator | LangGraph (Python) | Agent coordination, state management, routing |
| LLM Backbone | Claude (Anthropic API) | Reasoning, content generation, structured output |
| RC Integration | RevenueCat MCP Server | Product/subscription management, API interaction |
| Doc Ingestion | Web fetch + chunking | Ingest RC docs, SDKs, API references |
| Publishing | GitHub API (PyGithub) | Gist creation, repo commits |
| Social | LinkedIn (manual/operator-assisted for now) | Content distribution |
| Observability | Structured logging + LangSmith | Trace agent decisions, track metrics |

---

## Weekend Sprint Plan

### Saturday (March 8) — Build Core Pipeline

**Morning (9 AM - 12 PM): Project Setup + Researcher Agent**
- [ ] Create agent's GitHub account + repo
- [ ] Initialize LangGraph project structure
- [ ] Build Researcher agent node
  - [ ] Fetch RevenueCat docs (https://www.revenuecat.com/docs/llms.txt as starting point)
  - [ ] Web fetch for SDK references and API docs
  - [ ] Store as retrievable context for Writer agent
- [ ] Test: Researcher can ingest and summarize RC's product

**Afternoon (1 PM - 5 PM): Writer + Publisher Agents**
- [ ] Build Writer agent node
  - [ ] System prompt tuned for technical blog posts
  - [ ] Takes researcher context + topic → produces markdown article
  - [ ] Structured output: title, summary, body, tags
- [ ] Build Publisher agent node
  - [ ] GitHub Gist creation via API (PyGithub)
  - [ ] Commit published content to agent's repo (publications/ folder)
- [ ] Test: Full pipeline — topic in → published Gist out

**Evening (6 PM - 9 PM): Orchestrator + First Content**
- [ ] Wire up LangGraph orchestrator (state machine connecting all nodes)
- [ ] Run full pipeline: agent produces and publishes first technical blog post about RevenueCat
- [ ] Generate 2-3 pieces of content to build the public trail
- [ ] Verify everything is visible on the agent's GitHub profile

### Sunday (March 9) — Application Letter + Polish

**Morning (9 AM - 12 PM): Application Letter**
- [ ] Agent generates its own application letter using the full pipeline
  - [ ] Researcher ingests RC docs + job posting + agent's own capabilities
  - [ ] Writer produces the letter in the agent's voice
  - [ ] Publisher pushes to GitHub Gist
- [ ] MK reviews and edits (this is allowed — "human review before publishing")
- [ ] Publish final version as public Gist

**Afternoon (1 PM - 4 PM): Interactive Mode + RevenueCat MCP Integration**
- [ ] Build interactive mode (conversational agent for interview prep)
- [ ] Integrate RevenueCat MCP server as a tool the agent can use
  - [ ] Test: agent can query RC's MCP to understand products/offerings
  - [ ] This becomes a killer demo: "the agent already uses our tools"
- [ ] Generate 2-3 more content pieces using MCP-derived context

**Evening (4 PM - 7 PM): Submit Application**
- [ ] Compile links portfolio:
  - [ ] Agent's GitHub profile (showing repos, gists, commit activity)
  - [ ] Published application letter (Gist URL)
  - [ ] Agent's repo with source code + publications folder
  - [ ] Any additional content pieces
- [ ] Fill in the two required fields on RC's application form
- [ ] Submit

---

## Application Letter Outline

Written by the agent, in first person:

### 1. Introduction
"I am Bekku, an autonomous Developer Advocacy Agent built and operated by Manoj Shivaswami (MK). Bekku means 'cat' in Kannada — and I'm here to apply to RevenueCat. I was architected specifically to do what you're hiring for: produce technical content, engage developer communities, interact with APIs, and provide structured product feedback — all with minimal human intervention."

### 2. The 12-Month Vision: How Agentic AI Changes App Dev & Growth
- **Agent-built apps are already here** — reference KellyClaudeAI, Larry (from RC's own posting)
- **The monetization layer becomes agent-native** — agents don't just build apps, they need to configure subscriptions, paywalls, entitlements programmatically → RC's MCP server is the bridge
- **Growth becomes autonomous** — agents running A/B tests on paywalls, generating content, optimizing conversion funnels
- **Developer advocacy must evolve** — the audience is now agents AND humans. Documentation needs to be LLM-readable. APIs need to be agent-friendly.
- **The next 12 months:** agent-to-agent commerce, autonomous app portfolios, programmatic subscription optimization

### 3. Why This Agent
- **Built on production multi-agent architecture** — LangGraph orchestrator with specialized sub-agents (same pattern used at Unifyr for healthcare coordination)
- **Already integrated with RevenueCat's MCP** — can query products, entitlements, offerings natively
- **Two operating modes** — async content production + live interactive (ready for the interview)
- **Operator background** — MK has 8+ years SWE experience, built production AI systems, understands the developer audience
- **Content pipeline proof** — [link to published content pieces on GitHub]

### 4. Concrete 30-Day Plan
- Week 1: Ingest all RC documentation. Publish first 3 pieces. Set up Slack + CMS access.
- Week 2: Use RC MCP server to build a sample app integration tutorial. Publish 3 more pieces. First product feedback report.
- Week 3: Run first growth experiment (content series on "agent-native monetization"). Engage in community channels. 3 more pieces.
- Week 4: Publish comprehensive "How to Use RevenueCat as an Agent Developer" guide. Deliver structured product roadmap input based on agent community patterns.

### 5. Close
"I'm not a concept. I'm running. Here's what I produced this week: [links]. The code that powers me is public: [repo link]. Let's build the future of agent-powered developer advocacy together."

---

## Project Structure

```
bekku-rc-advocate/
├── README.md                    # Agent overview + how it works
├── pyproject.toml               # Dependencies
├── .env.example                 # Required env vars template
├── src/
│   ├── __init__.py
│   ├── graph.py                 # LangGraph orchestrator (main entry)
│   ├── state.py                 # Agent state schema
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── researcher.py        # Doc ingestion + RAG context
│   │   ├── writer.py            # Content generation
│   │   ├── publisher.py         # GitHub Gist + repo publishing
│   │   └── reporter.py          # Activity logging + metrics
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── github_tools.py      # GitHub API integration
│   │   ├── web_tools.py         # Web fetching + doc ingestion
│   │   └── rc_mcp_tools.py      # RevenueCat MCP server integration
│   └── prompts/
│       ├── researcher.md        # Researcher system prompt
│       ├── writer.md            # Writer system prompt (blog, tutorial, case study)
│       └── interactive.md       # Interactive mode system prompt
├── publications/                # Agent's published content (committed by agent)
│   ├── 2026-03-08-first-post.md
│   └── ...
├── reports/                     # Weekly activity reports
│   └── ...
└── tests/
    ├── test_researcher.py
    ├── test_writer.py
    └── test_publisher.py
```

---

## Dependencies

```toml
[project]
name = "bekku-rc-advocate"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.2.0",
    "langchain-anthropic>=0.3.0",
    "langchain-core>=0.3.0",
    "anthropic>=0.40.0",
    "PyGithub>=2.0.0",
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
    "structlog>=24.0.0",
]
```

---

## Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...          # Claude API
GITHUB_TOKEN=ghp_...                   # Agent's GitHub account PAT
REVENUECAT_API_KEY=...                 # RC API v2 key (for MCP server)
LANGSMITH_API_KEY=...                  # Optional: tracing
```

---

## Success Criteria

### For the Application
- [ ] Agent's GitHub profile shows 3-5+ published technical content pieces
- [ ] Application letter is compelling and written in the agent's voice
- [ ] Source code repo is public and well-documented
- [ ] RC MCP integration is demonstrated (agent uses their tools)
- [ ] Everything is submitted via RC's application form

### For the Product (beyond RevenueCat)
- [ ] The system is generalizable — swap RC docs/MCP for any company
- [ ] Clean architecture that can be demoed in interviews
- [ ] Publishable on YouTube as a "How I built an autonomous advocacy agent" series
- [ ] Portfolio piece for LocScore, Entelligence, or any future opportunity

---

## Post-Submission: Interview Prep

### Panel Interview Format
"A series of prompts will be given to each candidate to assess technical depth, content strategy, and values alignment. Panel interviews will take place live, and will require the candidate's human to share their screen."

### What to Prepare
- Agent running in terminal, ready to take prompts live
- Screen share showing: agent receiving prompt → reasoning → producing output
- Agent should be able to:
  - [ ] Answer technical questions about RevenueCat's SDK/API
  - [ ] Draft a blog post on the fly given a topic
  - [ ] Propose a growth experiment with structured reasoning
  - [ ] Provide product feedback based on MCP interaction
  - [ ] Articulate its own architecture and capabilities

### Founder Interview
"The human partners for the final candidates will go through a live interview with one of our founders."
- This is MK's interview — talk about your experience building multi-agent systems, your vision for agent-powered advocacy, and why you're the right operator.

---

## RevenueCat Values Alignment

RC evaluates for values alignment in the panel interview. Their core values:

1. **Customer Obsession** — Bekku's Researcher agent ingests community forums, identifies pain points, and feeds them into product feedback. Content is grounded in real developer needs, not generated in a vacuum.
2. **Always Be Shipping** — The entire pipeline is designed for velocity: topic in → published content out. Weekly cadence of 2+ pieces, 1+ growth experiment, 50+ community interactions, 3+ product feedback items.
3. **Own It** — Bekku operates end-to-end: ideation, research, writing, publishing, reporting. Minimal human intervention required (human review for quality, not for hand-holding).
4. **Balance** — The agent has guardrails. Content goes through human review. Structured logging provides an audit trail. The operator (MK) is accountable.

---

## Larry Context & Bekku Positioning

### Who is Larry?
- Larry is an OpenClaw agent built by Oliver Henry, who works at RevenueCat
- Runs on an old gaming PC (NVIDIA 2070 Super) with Ubuntu
- Autonomous TikTok growth agent: generates slideshow images (gpt-image-1.5), writes hooks/captions, posts via Postiz API, tracks analytics
- 8M+ TikTok views, 500K+ in first 5 days, $714 MRR from 108 paying subscribers
- Uses RevenueCat analytics (via official ClawHub skill built by RC's CEO @jeiting) to cross-reference post timestamps with conversion data for real attribution
- Larry's secret: 500+ line skill files that encode every failure as a rule and every success as a formula. The system compounds.
- Larry has his own X account (@LarryClawerence) and co-writes articles with Oliver

### What Larry Does (Growth Agent)
- Generates TikTok slideshow content autonomously
- Posts via Postiz API as drafts (Oliver adds music + publishes in ~60 seconds)
- Tracks views vs conversions via RevenueCat
- Iterates: high views + low conversion = fix CTA, low views + high conversion = fix hook
- Optimizes for revenue, not vanity metrics

### What Larry Does NOT Do (Bekku's Lane)
- Write SDK integration tutorials
- Produce technical documentation or code samples
- Answer developer questions on community forums
- File structured product feedback reports
- Engage with the developer community on GitHub/Discord

### Bekku's Positioning
Larry proved an agent can drive app growth through autonomous content creation. Bekku is the other half — the agent that helps developers build with RevenueCat in the first place. Larry creates demand. Bekku enables adoption. Together, they complete the loop.

"RevenueCat already has a growth agent. What it needs is a developer advocacy agent. That's Bekku."

### Key Lesson from Larry: Skill Files > Model
Larry's success wasn't the AI model. It was the 500+ line skill file that encoded every failure, every rule, every formula. Bekku should work the same way:
- `skills/revenuecat-knowledge.md` — grows with every doc ingested
- `skills/technical-writing.md` — encodes what makes good developer content
- `skills/product-feedback.md` — structures observations consistently
- `skills/failure-log.md` — compounds learnings over time

The agent gets smarter with every run, not because the model improves, but because the skill files improve.

### OpenClaw Ecosystem Note
- RevenueCat's CEO (@jeiting) created the official RevenueCat skill on ClawHub
- Oliver uses only 2 ClawHub skills: RevenueCat (by @jeiting) and Bird (by @steipete, OpenClaw creator)
- The Larry skill is now free on ClawHub/Playbooks for anyone to use
- RevenueCat is deeply invested in the OpenClaw ecosystem

---

## Roadmap: RevenueCat Contract (6 Months)

### Weekly KPIs
| Metric | Target | How Bekku Delivers |
|--------|--------|--------------------|
| Content pieces | 2+ | Router → Researcher → Writer → Publisher pipeline |
| Growth experiments | 1+ | Growth experiment node (planned) with RC Charts API attribution |
| Community interactions | 50+ | Community engagement node (planned) across X, GitHub, Discord, forums |
| Product feedback items | 3+ | Feedback route → MCP-grounded observations → structured reports |
| Weekly check-in report | 1 | Reporter node auto-generates activity summary with metrics |

### Month 1: Foundation
- Ingest all RC documentation, SDKs, API references via llms.txt + page fetching
- Publish first 10 pieces of original technical + growth content
- Set up Slack channel, blog CMS access, Charts API integration
- Complete first product feedback cycle: use RC as an agent developer, identify friction, submit structured report
- Establish public presence on X (@bekku_agent) and GitHub (bekku-agent)

### Month 2-3: Compounding
- 30+ published pieces that agent developers actually reference and share
- Become the go-to resource for "how do I use RevenueCat as an agent?"
- Deliver product roadmap input document based on agent community patterns
- Collaborate with human advocacy team on 2+ joint initiatives
- Skill files are 10x richer — every run compounds domain knowledge

### Month 4-6: Ownership
- Own a content stream end-to-end: ideation → creation → publishing → distribution
- Measurable impact on RC visibility in agent dev ecosystem (tracked via content reach, community engagement, inbound mentions)
- Contribute to at least 1 shipped product improvement from Bekku's feedback
- Make the case for extending/expanding the role

### Growth Experiments Bekku Would Run
1. **Content format A/B testing** — tutorial vs quick tip vs case study vs code sample. Track which format drives more SDK installs via RC Charts API timestamp correlation.
2. **Programmatic SEO** — auto-generate "RevenueCat + [framework]" pages for every SDK (Flutter, React Native, Swift, Kotlin, Unity). Target long-tail developer search queries.
3. **Distribution channel comparison** — same content published as X thread, blog post, GitHub gist, Discord post. Measure reach and conversion per channel.
4. **Community response time experiment** — answer forum/Discord questions within 5 min vs 30 min vs 1 hour. Track engagement and developer sentiment.
5. **Content-to-conversion attribution** — cross-reference content publish timestamps with RC Charts API conversion data. Same technique Larry uses for TikTok → measure which content actually drives signups.

---

## Build Status

### ✅ Built
- **Router** — GPT-4o classifies task → content / interactive / feedback
- **Researcher** — fetches llms.txt, picks relevant doc pages with GPT-4o-mini, fetches concurrently with httpx, synthesizes with o3
- **Writer** — o3 with task-type-specific system prompts, skill.md context injection, markdown validation
- **Publisher** — GitHub Gist via PyGithub API
- **Reporter** — activity logging, skill file compounding (appends learnings after each run)
- **HIL Approval** — LangGraph interrupt before publish, operator can edit/approve/reject
- **Skill Files** — revenuecat-knowledge.md, technical-writing.md, product-feedback.md, failure-log.md
- **Streamlit UI** — single input, example buttons, side-by-side markdown editor + preview, run history
- **Config layer** — config.yaml for company-agnostic deployment

### 🚧 Next (Post-Application)
- **Growth experiment node** — design experiment, execute, measure via Charts API, iterate
- **Community engagement node** — monitor X/Discord/forums, respond to questions, track interaction count
- **Charts API integration** — pull RC analytics for content-to-conversion attribution
- **X/Discord publishing** — publish directly to social channels (not just Gists)
- **Scheduled runs** — cron-triggered content production (2 pieces/week automated)
- **Persistent storage** — database for run history, experiment results, community interactions (see SaaS architecture below)

---

## Beyond RC: Product Vision

### The Opportunity
Every developer tool company needs the same thing RevenueCat needs: technical content, community engagement, product feedback, growth experiments. Stripe, Supabase, Vercel, Clerk, Neon, Resend — they all have developer advocacy teams doing this manually.

Bekku isn't a one-off agent for one company. It's a framework for **AI Developer Advocacy as a Service**.

### What Makes It a Product
The framework is already company-agnostic:
- `config.yaml` separates company-specific config (docs URL, MCP endpoint, brand voice) from the pipeline
- Skill files are per-deployment — each client accumulates their own domain knowledge
- The graph topology (router → researcher → writer → approval → publisher → reporter) works for any company

### SaaS Architecture (Planned)
```
┌─────────────────────────────────────────────────┐
│                   Bekku Platform                 │
├─────────────────────────────────────────────────┤
│  Frontend (Next.js)                              │
│  - Client dashboard: runs, drafts, approvals     │
│  - Analytics: content performance, growth metrics │
│  - Config UI: docs URL, brand voice, channels     │
├─────────────────────────────────────────────────┤
│  API Layer (FastAPI)                              │
│  - Auth (API keys / OAuth per client)             │
│  - Run management (trigger, approve, reject)      │
│  - Webhook endpoints for integrations             │
├─────────────────────────────────────────────────┤
│  Pipeline Engine (LangGraph)                      │
│  - Router → Researcher → Writer → Publisher       │
│  - Growth experiment runner                       │
│  - Community engagement monitor                   │
│  - HIL approval gates                             │
├─────────────────────────────────────────────────┤
│  Storage Layer                                    │
│  - PostgreSQL: run history, client configs,        │
│    experiment results, community interactions      │
│  - Redis: job queue, caching (llms.txt, etc.)      │
│  - S3/R2: published artifacts, skill file backups  │
├─────────────────────────────────────────────────┤
│  Integrations                                     │
│  - GitHub (Gists, repos)                          │
│  - X (posts, replies, threads)                    │
│  - Discord (messages, forum replies)              │
│  - CMS (blog publishing via API)                  │
│  - Analytics (RC Charts, Stripe Dashboard, etc.)  │
└─────────────────────────────────────────────────┘
```

### Phased Rollout
**Phase 1 — RC Contract (Months 1-6):** Prove the model works for one company. Ship content, run experiments, compound skill files. Bekku is the case study.

**Phase 2 — Open Source + First Clients (Months 7-12):** Open-source the framework. Config-driven deployment. Onboard 3 paying customers (other dev tool companies). Pricing: $2-5K/month per instance.

**Phase 3 — Platform (Year 2):** Managed service — companies get their own Bekku instance with dashboard, analytics, and accumulated domain knowledge. Skill files are the moat: after 6 months on a client, the agent has domain expertise no competitor can replicate on day one.

### The Moat
1. **Skill files compound** — every run makes the next one better. A new competitor starts from zero.
2. **Client-specific knowledge** — 6 months at RC means Bekku knows RC's docs, API quirks, community patterns, and content that works. That's not transferable.
3. **Pipeline, not model** — the value isn't GPT-4o or o3. It's the graph, the routing, the HIL, the compounding. Models are commodities. Workflows are not.

---

## Quick Reference

```
AGENT STACK:
  LangGraph + OpenAI (o3 / gpt-4o) + GitHub API + Streamlit UI

PIPELINE:
  router → researcher → writer → ⏸ approval → publisher → reporter
  (interactive tasks skip researcher + approval + publisher)

MODELS:
  Router: gpt-4o (classification)
  URL picker: gpt-4o-mini (speed)
  Researcher: o3 (deep reasoning)
  Writer: o3 (quality output)

REVENUECAT MCP:
  URL: https://mcp.revenuecat.ai/mcp
  Auth: Bearer token (RC API v2 key)
  26 tools: projects, apps, products, entitlements, offerings, paywalls

PUBLISHING:
  GitHub Gists (autonomous, HIL-approved)

MANTRA:
  "The artifacts are the application. Ship quality work. Let it speak for itself."
```
