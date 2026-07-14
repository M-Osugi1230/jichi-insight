# ADR 0005: GitHub Pages static deployment

- Status: Accepted
- Date: 2026-07-15

## Context

The initial product has three pilot municipalities and does not require authenticated writes or real-time queries. Trust, low operational cost, reproducible releases and a small attack surface are more important than server-side functionality.

## Decision

Use Next.js static export and GitHub Pages custom workflows for the first public version.

- Pull requests run the complete build and export validation.
- `main` deployments use the `/jichi-insight` base path.
- GitHub Pages receives only the generated `apps/web/out` artifact.
- Real evaluation data must pass the existing reviewed/published gates before entering production.

## Consequences

- Hosting and rollback remain simple.
- The public site has no application server or database attack surface.
- Dynamic search, authenticated review and APIs will require a later architecture stage.
- Route and asset handling must remain compatible with the project-site base path.
