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

This plan simply runs the command

```console
$ rpmlint ./*.rpm
```

Currently, there is no support to pass in additional `.rpmlintrc` due to limitations of the [`tmt`][tmt-import]
interface. The `rpm` and `srpm` artifacts are taken from the testing-farm artifacts

:::note

The rpmlint of the `.spec` file is handled automatically when running `rpmlint` against a `srpm`.

:::

## Options

No options available

## Examples

- Rpmlint the upstream packit project
  ```yaml
  plans:
    import:
      url: https://github.com/packit/tmt-plans
      ref: main
      name: /plans/rpmlint
  ```

## See Also

- [rpmlint]

<!-- SPHINX-END -->

[rpmlint]: https://github.com/rpm-software-management/rpmlint
[tmt-import]: https://tmt.readthedocs.io/en/stable/spec/plans.html#import-plans
