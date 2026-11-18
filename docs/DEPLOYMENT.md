# Deployment

## Public URL

Production URL:

`https://jimieru.com/`

The repository is configured for a static Next.js export deployed through GitHub Pages custom workflows.

## Activation status

GitHub Pages was enabled on 2026-07-15 with **GitHub Actions** selected as the build and deployment source.

This change records the repository-level activation and intentionally triggers the first production deployment after Pages enablement.

## Environment boundary (adopted 2026-11-15)

This project is operated by a single publication owner and deployed as a
static export. It deliberately does **not** run hosted preview or staging
environments. The boundaries below are the adopted definition (Issue #11);
they describe what actually exists, not an aspirational topology.

### Production

- GitHub Pages, built by the `Deploy Pages` workflow from `main` only.
- Published data only: production pages are generated from reviewed,
  canonical records on `main`. Candidate (prepared) data is never part of
  the production build — candidates carry `publication.eligible=false`,
  the web data loaders are fail-closed, and contract tests assert that the
  public web source does not import candidate staging data.
- Every deployment is verified from outside the build artifact by the
  Production Smoke workflow, and the result is recorded in
  `.github/publication-status.json` (`verified` / `deployed_commit_sha`)
  on the dedicated `publication-status` branch, which the Verify Pages
  Publication workflow force-pushes after each deployment (branch
  protection requires pull requests for `main`, so the record cannot be
  pushed to `main` directly). Read it with
  `git show origin/publication-status:.github/publication-status.json`.

### Pre-merge (the staging function)

There is no hosted staging environment. Its function — checking changes
against reviewed-but-not-yet-public data before anything ships — is
fulfilled inside the repository:

- All work happens on feature branches and reaches `main` only through a
  pull request. Nothing merges without a local production build, the full
  Python test suite, and the web contract tests passing; the `Quality`
  workflow re-runs repository validation, tests, lint, type checking, the
  production build, and static-export validation on the pull request.
- Data changes follow the in-repository state transition instead of an
  environment promotion: candidate (prepared, `publication.eligible=false`)
  → human review by the publication owner → reviewed canonical records.
  Reviewed-but-not-yet-public data exists only on branches and in pull
  requests; it is never served publicly before merge.
- Honest limitation: GitHub branch protection is not configured (Issue #2),
  so the merge gate is enforced by this documented process and the PR-only
  workflow, not by a technical merge block.

### Preview

- Preview is the local build output only. No hosted per-PR preview URL is
  issued, and no PR preview deployment exists.
- The pre-merge substitute is building the exact production artifact
  locally and running the static-export smoke test, which is what CI
  does for every pull request.
- Hosted per-PR previews remain a future option to revisit if local
  verification becomes insufficient; they are not a current capability
  and must not be described as one.

### Rollback

- Rollback is a revert of the faulty merge through a pull request,
  followed by redeployment from `main` (see "Rollback" below and
  `docs/OPERATIONS_RUNBOOK.md` §7). Force-pushing `main` is prohibited.
- The procedure was executed end to end before the formal release
  (revert → redeploy drill, PRs #471 and #472).

### Issue #11 acceptance criteria — disposition

| Criterion | Disposition |
|---|---|
| Every UI PR receives a preview URL | **Deferred by this definition.** No hosted preview exists; the local production build plus CI static-export smoke is the adopted substitute. Hosted previews are a future option, not a current capability. |
| Staging uses reviewed but not-yet-public data | **Satisfied by this definition.** The staging function is the in-repository state transition on branches/PRs described above; reviewed-but-not-yet-public data is never publicly served. |
| Production uses published data only | **Satisfied by existing practice.** Production builds only from `main`; candidate data is excluded by `publication.eligible=false`, fail-closed loaders, and contract tests. |
| A failed quality gate cannot deploy to production | **Satisfied by existing practice.** Deployment is only from `main`; pull requests must pass the local gate and the `Quality` workflow before merge. Caveat: enforcement is procedural until branch protection is configured (Issue #2). |
| Rollback is documented and tested | **Satisfied by existing practice.** Documented below and in `docs/OPERATIONS_RUNBOOK.md` §7; tested in the pre-release drill (PRs #471, #472). |
| Monitoring and incident ownership are documented | **Satisfied by existing practice.** `docs/OPERATIONS_RUNBOOK.md` §2 (roles), §6 (incident levels), §9 (monitoring), §11 (weekly post-release stability checks). Recorded limitation: no automated alerting; detection relies on the weekly checks, merge-time publication verification, and user reports. |

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

The repository uses **GitHub Actions** as the Pages build and deployment source. The `Deploy Pages` workflow uses least-privilege permissions:

- `contents: read`
- `pages: write`
- `id-token: write`

The deploy job targets the protected `github-pages` environment.

## Base path

The site is served from the root of the custom domain `jimieru.com`, so
no base path is used: production builds no longer set
`NEXT_PUBLIC_BASE_PATH`, and local and pull-request quality builds use
the same empty base path. (Until the custom-domain migration the site
was hosted as a GitHub Pages project site and production builds set
`NEXT_PUBLIC_BASE_PATH=/jichi-insight`.)

## Automated production verification

After every successful `Deploy Pages` workflow, `Production Smoke` checks the public site from outside the build artifact.

It verifies:

- the home page returns HTTP 200
- the site identity and publication-state copy are present
- static assets use `/_next/`
- about, corrections, data quality, methodology, municipalities, the 福岡県 page and sources return HTTP 200
- `robots.txt`, `sitemap.xml` and `manifest.webmanifest` return HTTP 200

The workflow retries briefly while the deployment propagates and uploads a human-readable report whether it passes or fails.

## Release verification

After every production deployment, verify:

- Home, sources, municipalities, methodology, corrections, data quality and about pages return 200
- Static assets load under `/_next/`
- Internal links resolve from the domain root
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

The custom domain `jimieru.com` is the production domain. The CNAME
record file ships with the site artifact (`apps/web/public/CNAME`), and
metadata, sitemap, robots and the deployment workflows all use
`https://jimieru.com` as the canonical origin. The previous project-site
URL (`https://m-osugi1230.github.io/jichi-insight/`) redirects to the
custom domain once the repository Pages settings point at it. DNS
records at the registrar and the Pages custom-domain setting are
managed together with this migration.
