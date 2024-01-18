# Rpmlint

<!-- SPHINX-START -->

Run [rpmlint] on the current Copr project or Koji build

## Synopsis

```yaml
discover:
  how: fmf
  filter: "tag: rpmlint"
  url: https://github.com/packit/tmt-plans
  ref: main
execute:
  how: tmt
```

## Description

This plan simply runs the command

```console
$ rpmlint ./*.rpm
```

The `rpm` and `srpm` artifacts are taken from the testing-farm artifacts. In order to pass a `.rpmlintrc` file, use the
[`prepare`] step of the plan to copy the file to `TMT_PLAN_DATA`. Only the `rpmlintrc` file that matches the spec file
is used.

:::note

The rpmlint of the `.spec` file is handled automatically when running `rpmlint` against a `srpm`.

:::

## Options

No options available

## Examples

- Rpmlint the upstream packit project
  ```yaml
  discover:
    how: fmf
    filter: "tag: rpmlint"
    url: https://github.com/packit/tmt-plans
    ref: main
  execute:
    how: tmt
  ```
- Use `rpmlintrc` file
  ```yaml
  prepare:
    - how: shell
      script: cp ./*.rpmlintrc $TMT_PLAN_DATA/
  discover:
    how: fmf
    filter: "tag: rpmlint"
    url: https://github.com/packit/tmt-plans
    ref: main
  execute:
    how: tmt
  ```

## See Also

- [rpmlint]

<!-- SPHINX-END -->

[rpmlint]: https://github.com/rpm-software-management/rpmlint
[`prepare`]: https://tmt.readthedocs.io/en/stable/spec/plans.html#prepare
