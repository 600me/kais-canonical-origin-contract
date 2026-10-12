# Kais Canonical Origin Contract

Assert that one saved HTML page contains exactly one canonical link in its head, resolving to your explicit production origin. This free GitHub Action and Python CLI run offline, without tokens, external services, uploads or automatic cloud charges.

**Disclosure:** This tool was produced and checked by Kais's AI assistant. Kais also owns the separate paid SEO Release Diff Actor described below. Fixture results are synthetic tests, not customer examples or evidence of search performance.

## Why check the origin explicitly?

Comparing production and preview pages while treating their hostnames as equivalent can hide an unwanted preview hostname in the canonical. This tool checks a separate contract: the resolved canonical must match the scheme, hostname and port you specify. It does not determine which canonical Google will select.

## Try the local fixtures

With Python 3 installed, run from this repository:

```bash
python3 check_canonical.py \
  --html-file fixtures/production.html \
  --page-url https://preview.example/products/widget \
  --expected-origin https://production.example
```

The supplied synthetic fixture prints `{"passed": true, "code": "ORIGIN_MATCH"}` and exits 0. Replace the file with `fixtures/preview.html`: it reports `ORIGIN_MISMATCH` and exits 1. Both `.example` domains are placeholders; the tool does not visit them.

## Use in GitHub Actions

Your workflow must first save the HTTP HTML response you are authorized to inspect. Pass its **final page URL**, including any redirects, as `page-url`. The Action performs no download and does not build your site. It requires Bash and Python 3; the example uses an Ubuntu runner.

After saving `saved-page.html` in your workflow workspace:

```yaml
- uses: 600me/kais-canonical-origin-contract@v1.0.0
  with:
    html-file: saved-page.html
    page-url: https://preview.example/products/widget
    expected-origin: https://production.example
```

Review the source and pin the Action to its actual release commit SHA when integrating it. The version above identifies this release; it does not fetch or pay for a separate service.

## Contract and limits

- Reads one UTF-8 HTML file, at most 2 MiB, and inspects canonical links inside `<head>`.
- Requires exactly one nonempty canonical. Relative links resolve against `page-url`, with a single `<base href>` respected.
- Compares scheme, hostname and port. Host casing and default HTTP/HTTPS ports are normalized.
- Missing or duplicate canonicals, multiple base URLs, ambiguous attributes, invalid URLs, credentials, fragments and origin mismatches block the check.
- Prints a small JSON result and exits 0 on success, 1 on failure; missing CLI arguments exit 2.

This uses Python's HTMLParser, not a browser DOM parser. It does not render JavaScript, fetch hreflang targets, validate canonical paths, inspect response headers, verify search indexing or approve deployment. A passing origin check says nothing about those separate checks.

Twenty local synthetic behavior and CLI tests pass, and the composite Bash step was exercised locally. These results do not establish GitHub-hosted runner execution or external adoption.

## Optional companion for before/after comparisons

[SEO Release Diff](https://apify.com/resolute_client/seo-release-diff) compares old/new public HTTP HTML metadata, including titles, robots directives and canonical differences. It is a separate paid Apify Actor; this Action neither calls it nor requires an Apify account. Its origin normalization does not replace this explicit origin contract. Both tools have HTML-only limits and make no ranking promise.

MIT licensed. Report reproducible tool issues without credentials or private page content.
