# Fedora Review

Run [fedora-review] on the current Copr project or Koji build

See this discussion for more
https://discussion.fedoraproject.org/t/running-fedora-review-on-every-commit/178858


## Configuration

The majority of packages shouldn't require any configuration. But some packages
don't have to comply with all the [Fedora Packaging Guidelines][guidelines],
and exceptions can be granted to them. To avoid `fedora-review` reporting them
as issues, you can skip some checks.

Create a `fedora-ci.toml` like this in your package DistGit repository:

```toml
[tools.fedora-review]
exclude = [
  # A comment linking a FESCo exception that this package has
  "CheckOwnDirs",
  # Another explanation why we want to skip the check
  "CheckFilePermissions",
]
```

The configuration is passed to the `fedora-reivew` tool itself. So any
configuration besides skipping checks will work as well.

```toml
[tools.fedora-review]
verbose = true
mock_config = "fedora-45-x86_64"
define = [
  "FOO=bar",
]
# ...
```


[fedora-review]: https://forge.fedoraproject.org/packaging/FedoraReview
[distgit]: https://src.fedoraproject.org/
[guidelines]: https://docs.fedoraproject.org/en-US/packaging-guidelines/
