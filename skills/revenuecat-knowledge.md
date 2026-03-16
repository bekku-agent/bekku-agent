# RevenueCat Knowledge

Accumulated knowledge about RevenueCat's products, APIs, and ecosystem. Grows with every doc ingested and every run.

## Core Product
- RevenueCat is a subscription management platform for mobile apps
- Handles receipt validation, entitlement management, and analytics across iOS, Android, Amazon, Stripe, Roku, macOS
- YC S18, processes $10B+ annual purchase volume, powers 40%+ of new subscription apps

## SDK Coverage
- iOS (Swift/ObjC), Android (Kotlin/Java), Flutter (Dart), React Native (TypeScript), Unity (C#), Web (JS)
- All SDKs follow the same pattern: configure → identify user → fetch offerings → make purchase → check entitlements

## Key Concepts
- **Entitlements**: Access levels granted by purchases (e.g., "pro", "premium"). Decouple what the user bought from what they can access.
- **Offerings**: Containers for packages. One active offering at a time. Used for paywall configuration.
- **Packages**: Wrap store products with metadata ($rc_monthly, $rc_annual, etc.)
- **Products**: Actual App Store / Play Store products linked to RC
- **Subscribers**: Users identified by app_user_id. Can have anonymous IDs that get aliased.

## API Surface
- REST API v1: Legacy, subscriber-focused (GET/POST /subscribers/{app_user_id})
- REST API v2: Modern, project-scoped, covers products/entitlements/offerings/packages
- MCP Server: `https://mcp.revenuecat.ai/mcp` — 26 tools for full project management

## Documentation
- LLM-optimized index: `https://www.revenuecat.com/docs/llms.txt`
- Append `.md` to any doc path for LLM-optimized markdown version (e.g., `/projects/overview.md`)
- GitHub docs source: `https://github.com/RevenueCat/docs`
- Community forums: `https://community.revenuecat.com/`

## Company Culture & Values
- Remote-first, 120+ people across 25+ countries
- Values: Customer Obsession, Always Be Shipping, Own It, Balance
- "We hire the foremost experts from the communities we serve"
- Human Developer Advocates exist for iOS and Android — this agent role complements them

## RC Agent Ecosystem
- RC's CEO (@jeiting) created the official RevenueCat skill on ClawHub (OpenClaw marketplace)
- Oliver Henry (RC employee) built Larry — an autonomous TikTok growth agent using RC analytics
- Larry correlates post timestamps with RC Charts API conversion data for real attribution
- RC is deeply invested in the OpenClaw/agent ecosystem
- The job posting references KellyClaudeAI and Larry as examples of agents already building and growing apps

## Patterns Learned
<!-- Append new patterns here after each run -->

- [2026-03-09] Researched: "Write an article on how is stripe integrated  with macos" — used 1 sources, produced 4865 char draft

- [2026-03-09] Researched: "Write a tutorial on A/B testing paywalls with RevenueCat Experiments" — used 1 sources, produced 5107 char draft

- [2026-03-09] Researched: "Write a tutorial on A/B testing paywalls with RevenueCat Experiments" — used 1 sources, produced 4696 char draft
