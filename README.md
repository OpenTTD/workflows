# OpenTTD's workflows

To automate all kinds of things, we use GitHub Actions, and especially, their workflow.
This repository runs a few workflows that don't belong to a repository we have.

## Workflows

- [New OpenTTD Release](.github/workflows/new_openttd_release.yml): workflow that is triggered when a new OpenTTD binary is produced
- [Publish Docs](.github/workflows/publish_docs.yml): publishes the HTML docs to https://docs.openttd.org/ based on an openttd-nightly version.
- [Update CDN](.github/workflows/update_cdn.yml): updates the [CDN](https://cdn.openttd.org) with required files like index.html, manifest.yaml, etc.
