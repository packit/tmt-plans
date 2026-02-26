# Reverse Dependency Check

<!-- SPHINX-START -->

Run [fedora-revdep-check] on package version changes to detect reverse dependency issues

## Synopsis

```yaml
plans:
  import:
    url: https://github.com/packit/tmt-plans
    ref: main
    name: /plans/revdep-check
```

## Description

This plan runs `fedora-revdep-check` to verify that package version changes don't break reverse dependencies
in Fedora. The tool checks if any packages that depend on the updated package would have compatibility issues
with the new version.

An empty output means no reverse dependency issues were detected. If issues are found, the test will fail
and the output will be displayed in the test results.

For specific implementation details, see the [`/tests/revdep-check/run-revdep-check.py`] wrapper file.

Depending on the calling environment (`initiator`, `trigger` contexts) the inputs of this plan are provided
automatically, otherwise see the [options section](#options) for the expected control parameters.

## Options

`PACKAGE_NAME`

: koji-build: Extracted from build NVR using `koji taskinfo`, falls back to querying SRPM with `rpm -qp` if needed
: The name of the package to check

`PACKAGE_VERSION`

: koji-build: Extracted from build NVR using `koji taskinfo`, falls back to querying SRPM with `rpm -qp` if needed
: The new version of the package to check against reverse dependencies

## See Also

- [fedora-revdep-check]

<!-- SPHINX-END -->

[fedora-revdep-check]: https://github.com/fedora-python/fedora-revdep-check
[`/tests/revdep-check/run-revdep-check.py`]: ../../tests/revdep-check/run-revdep-check.py
