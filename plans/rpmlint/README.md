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

## Options

None so far

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
