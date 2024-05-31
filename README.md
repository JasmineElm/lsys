# L-System Experiments.

_very much alpha quality_

The idea to generate L-System rules on the fly occurred to me during
Genuary 2024.

This repo is very much a "one-trick-pony"; the code intends to generate
an image based on _reasonably_ sensible defaults:

```toml

```

Rather than re-invent the wheel, the rules generated use the same rules
and syntax as the [Lindenmayer
System](https://en.wikipedia.org/wiki/L-system):

- `F` for "forward"
- `+` for "turn left"
- `-` for "turn right"
- `[` for "push"
- `]` for "pop"

The code is all Python, and tries to avoid external
libraries. Libraries such as `numpy` can certainly be avoided, and will
given time be replaced by lighter-weight alternatives
