# Environment & Domain Intelligence — Navigation Hub
**Sprint 13 · Milestone 4** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Environment & Domain Intelligence** specifications for the Personal AI OS.
> It builds upon the [Vercel Foundation](file:///Users/anzarakhtar/aios/docs/vercel/README.md), [Deployment Intelligence](file:///Users/anzarakhtar/aios/docs/vercel/deployments/README.md), and [Serverless & Edge Intelligence](file:///Users/anzarakhtar/aios/docs/vercel/runtime/README.md) documents.
>
> In accordance with local-first system design guidelines, all environment configurations, secret isolations, DNS checks, SSL lifecycle updates, and promotions are managed locally, keeping the AI OS kernel as the central director.

---

## Documents

| Document | Purpose |
|---|---|
| [environment_management.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/environment_management.md) | Env configurations, project environments, and the Runtime Resource state schema |
| [secrets_management.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/secrets_management.md) | Variable encryption vaults, secret scopes, and database keys isolation |
| [domain_intelligence.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/domain_intelligence.md) | Domain list maps, project custom domains, and redirect rules |
| [dns_analysis.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/dns_analysis.md) | A/CNAME record verification, name server checks, and propagation stats |
| [ssl_management.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/ssl_management.md) | Certificate expiry trackers, auto-renewal schedules, and validation |
| [environment_promotion.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/environment_promotion.md) | Preview to production deployment paths, variable promotions, and alias swaps |
| [environment_health.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/environment_health.md) | Configuration drift checks, database mapping syncs, and domain failover rules |

---

## Reading Order

1. **[`environment_management.md`](file:///Users/anzarakhtar/aios/docs/vercel/environment/environment_management.md)**: Start here to study environment configurations and the state schema.
2. **[`secrets_management.md`](file:///Users/anzarakhtar/aios/docs/vercel/environment/secrets_management.md)**: Explore variables encryption and credentials isolation.
3. **[`domain_intelligence.md`](file:///Users/anzarakhtar/aios/docs/vercel/environment/domain_intelligence.md)** & **[`dns_analysis.md`](file:///Users/anzarakhtar/aios/docs/vercel/environment/dns_analysis.md)**: Learn about domain lists mapping and DNS records check.
4. **[`ssl_management.md`](file:///Users/anzarakhtar/aios/docs/vercel/environment/ssl_management.md)** & **[`environment_promotion.md`](file:///Users/anzarakhtar/aios/docs/vercel/environment/environment_promotion.md)**: Explore SSL certificates lifecycle and production promotions.
5. **[`environment_health.md`](file:///Users/anzarakhtar/aios/docs/vercel/environment/environment_health.md)**: Examine configurations drift and environment health.
