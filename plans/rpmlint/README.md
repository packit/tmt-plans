# Rpmlint

<!-- SPHINX-START -->

Run [rpmlint] on the current Copr project or Koji build

## Synopsis

```yaml
plans:
  import:
    url: https://github.com/packit/tmt-plans
    ref: main
    name: /plans/rpmlint
```

## Description

This plan simply runs `rpmlint` against the rpms and spec files provided. For specific details, see the
[`/tests/rpmlint/run-rpmlint.py`] wrapper file.

Depending on the calling environment (`initiator`, `trigger` contexts) the inputs of this plan are provided
automatically, otherwise see the [options section](#options) for the expected control parameters.

## Options

`SPEC_FILE`

: koji-build: Detected from dist-git (`*.spec`)
: Spec file to check.

`RPM_FILES`

: koji-build: Downloaded all rpm files from koji task
: RPM files to check. Can be wildcard.

`RPMLINT_RC_FILE`

: koji-build: Detected from dist-git (`*.rpmlintrc`)
: .rpmlintrc file.

`RPMLINT_TOML_FILE`

: koji-build: Detected from dist-git (`rpmlint.toml`)
: Rpmlint toml file to override.

## See Also

- [rpmlint]

<!-- SPHINX-END -->

[rpmlint]: https://github.com/rpm-software-management/rpmlint
[`/tests/rpmlint/run-rpmlint.py`]: ../../tests/rpmlint/run-rpmlint.py
