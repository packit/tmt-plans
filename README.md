# Packit-tmt

This is a repository containing reusable tmt tests focused on testing the packaging process.

It is assumed that these tests are imported and used in a testing-farm environment or through their reproduction
script.

## Quick-start

In order to import such tests, simply define a tmt plan with the content:

```yaml
plan:
  import:
    url: https://github.com/packit/tmt-plans
    name: /plans/name-of-reusable-plan
```

You can alter the inputs of this plan through environment variables.

## Plans available

- Plans equivalent with jobs run on `bohdi`
  - [ ] `/rpminspect`
  - [ ] `/rpmdeplint`
  - [ ] `/installability`
- Other plans
  - [`/plans/rpmlint`](plans/rpmlint)
