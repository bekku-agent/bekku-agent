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
- GitHub docs source: `https://github.com/RevenueCat/docs`
- Community forums: `https://community.revenuecat.com/`

## Patterns Learned
<!-- Append new patterns here after each run -->
