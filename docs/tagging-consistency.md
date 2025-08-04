# Tagging Consistency Report

This document summarizes how release tags are used and referenced in the O-RAN PTI O2 repository.

## Tag List

Current Git tags:
- 1.0.0
- 2.0.0
- 2.0.1
- ...
- 2.2.0
- k-release
- l-release

## Locations Where Tags Are Referenced

### Tag: `2.2.0`

Referenced in:
- `releases/release-2.2.0.yaml` (version and container_release_tag)
- `docs/release-notes.rst` (release notes for version 2.2.0)
- `docs/installation-guide.rst` (Docker image reference)
- Git metadata

### Observations

- Tags are consistently reflected in `release-*.yaml`, release notes, and installation guide.
- Release notes match the tag versions and dates.
- Docker container images use matching tags.

## Tag Update Checklist

When adding a new release tag, ensure consistency across all relevant files:

- `releases/release-<version>.yaml` (e.g., release-2.2.0.yaml)
- `container-tag.yaml` (used in CI for Docker image tagging)
- `docs/release-notes.rst` (formal release notes)
- `docs/installation-guide.rst` (image versions in deployment steps)

Use consistent naming conventions across tags (e.g., semantic versioning like `2.2.1`, or named releases like `l-release`).



---

Prepared by: Alisha Mahmood  
Date: 2025-08-04