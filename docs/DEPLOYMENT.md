# Deployment

## Public URL

Initial production target:

`https://m-osugi1230.github.io/jichi-insight/`

The repository is configured for a static Next.js export deployed through GitHub Pages custom workflows.

## Environments

| Environment | Source | Data policy |
|---|---|---|
| Local | Working tree | Fictional fixtures and explicitly selected reviewed data |
| Pull request | GitHub Actions build | Validation only; no public deployment |
| Production | `main` | Published data only |

A separate staging environment will be introduced before real evaluations are published. Until then, production pages may expose source coverage and methodology, but not unreviewed evaluation data.

## Deployment flow

```text
Pull request
  → repository validation
  → tests and lint
  → TypeScript check
  → static production build
  → static-export smoke test
  → merge to main
  → Pages build
  → artifact upload
  → github-pages environment
  → production URL
  → external production smoke test
```

## GitHub Pages settings

The repository must use **GitHub Actions** as the Pages build and deployment source. The `Deploy Pages` workflow uses least-privilege permissions:

- `contents: read`
- `pages: write`
- `id-token: write`

The deploy job targets the protected `github-pages` environment.

## Base path

Because the site is initially hosted as a project site, production builds set:

`NEXT_PUBLIC_BASE_PATH=/jichi-insight`

Next.js applies this base path to routes and generated assets. Local and pull-request quality builds use an empty base path.

## Production smoke test

`scripts/check_production.sh` verifies the deployed site from outside the build artifact.

It checks:

- the home page returns HTTP 200
- the site identity and development-status copy are present
- assets use `/jichi-insight/_next/`
- all primary routes return HTTP 200
- robots, sitemap and manifest are public

The workflow retries briefly to allow a Pages deployment to finish, then uploads a human-readable report whether it passes or fails.

## Release verification

After every production deployment, verify:

- Home, sources, municipalities, methodology and about pages return 200
- Static assets load under `/jichi-insight/_next/`
- Internal links remain under the project base path
- 404 page renders
- `robots.txt`, `sitemap.xml` and `manifest.webmanifest` are available
- Official source links open externally
- The home page still reports zero evaluations until reviewed evaluations exist

## Rollback

1. Identify the last known-good commit on `main`.
2. Revert the faulty merge through a pull request.
3. Run all quality checks.
4. Merge the revert.
5. Confirm that the Pages workflow deploys the restored artifact.
6. Record the incident and affected pages.

Do not force-push `main` to roll back production.

## Custom domain

A custom domain may be added after the public beta name, legal pages and canonical URL are finalized. When introduced, update metadata, sitemap, robots, deployment documentation and DNS together.
