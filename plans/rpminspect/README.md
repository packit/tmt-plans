# Rpminspect

<!-- SPHINX-START -->

Run [rpminspect] on the current Copr project or Koji build

## Synopsis

```yaml
plans:
  import:
    url: https://github.com/packit/tmt-plans
    ref: main
    name: /plans/rpminspect
```

## Description

This plan simply runs the command

```console
$ rpminspect [previous_build] [koji_build/copr_build]
```

where `koji_build` is the build specified by `RPMINSPECT_KOJI_BUILD`. If this option is not provided, it is assumed
that the plan is running against a `copr_build`, and the build artifacts are retrieved automatically from testing-farm.

`previous_build` is automatically determined from running

```console
$ koji list-tagged
```

:::note

Some functionalities like automatically determining `previous_build` are only available for Fedora packages.

:::

## Options

`RPMINSPECT_KOJI_BUILD`

: :::note

Not yet implemented

:::

Run `rpminspect` on the specified Koji build instead of the expected Copr project

`RPMINSPECT_TESTS`

: Run only the specified inspections. This option has precedence over `RPMINSPECT_EXCLUDE`.

See `rpminspect -l` for a list of available tests.

`RPMINSPECT_EXCLUDE` \[Default: `metadata`\]

: Exclude the specified inspections. This option has no effect if `RPMINSPECT_TESTS` is specified.

See `rpminspect -l` for a list of available tests.

`RPMINSPECT_THRESHOLD` \[Default: `BAD`\]

: Set the maximum result status that makes the rpminspect test fail

One of \[`OK`, `INFO`, `VERIFY`, `BAD` \]

The default will treat each check status as `pass`, `info`, `warn`, `fail` respectively. Use this variable to mark the
overall `pass`/`fail` of the test.

`RPMINSPECT_SUPPRESS`

: Set the minimum result status that will be reported

One of \[`OK`, `INFO`, `VERIFY`, `BAD` \]

`RPMINPSECT_ARCHES`

: Run inspection only on the specified architecture packages

::: note

Keep in mind the architectures available in the testing-farm runner that runs this job.

Also note that `src`, and `noarch` are also considered "architectures" in this context.

:::

## Examples

- Inspect the upstream packit projects
  ```yaml
  plans:
    import:
      url: https://github.com/packit/tmt-plans
      ref: main
      name: /plans/rpminspect
  ```
- Filter `disttag` inspection
  ```yaml
  plans:
    import:
      url: https://github.com/packit/tmt-plans
      ref: main
      name: /plans/rpminspect
  environment:
    RPMINSPECT_EXCLUDE: disttag
  ```
- Inspect downstream koji builds
  ```yaml
  TBD
  ```

## See Also

- Downstream Fedora-CI: [docker-runner][fedora-ci-docker], [tmt-plan][fedora-ci-tmt]
- [rpminspect][rpminspect-doc]

<!-- SPHINX-END -->

[fedora-ci-docker]: https://github.com/fedora-ci/rpminspect-runner
[fedora-ci-tmt]: https://github.com/fedora-ci/rpminspect-pipeline
[rpminspect]: https://github.com/rpminspect/rpminspect
[rpminspect-doc]: https://rpminspect.readthedocs.io
