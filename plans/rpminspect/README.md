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

## Options

`RPMINSPECT_KOJI_BUILD`
: Run `rpminspect` on the specified Koji build instead of the expected Copr project
: Note: Not yet implemented

## Examples

- Inspect the upstream packit projects
  ```yaml
  plans:
    import:
      url: https://github.com/packit/tmt-plans
      ref: main
      name: /plans/rpminspect
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
