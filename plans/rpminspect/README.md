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
$ rpminspect [previous_build] [koji_build]
```

<!-- SPHINX-END -->

[rpminspect]: https://github.com/rpminspect/rpminspect
