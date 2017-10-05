# UI Events KeyboardEvent code Values

This repository is for the [UI Events code](https://w3c.github.io/uievents-code/)
specification.

The there is also an [Implementation Report](https://w3c.github.io/uievents-code/impl-report.html) for this spec.

## Building

This spec was created using [bikeshed](https://github.com/tabatkins/bikeshed).
If you would like to contribute edits, please make sure that your changes
build correctly.

To **build** this spec:

1. Clone this repo into a local directory.
1. Install [bikeshed](https://github.com/tabatkins/bikeshed)
1. Run `python build.py` in your local directory.

To **make edits** to the spec:

1. Edit the `index-source.txt` file.
2. Build (as above). This will create `index.bs` and `index.html` files.

When submitting pull requests, make sure you don't include the `index.bs`
file in your changelist - it's part of `.gitignore` so that you don't include
it accidentally. All changes should be made in the `index-source.txt`
file.

To **update the implementation report**:

1. Edit the `impl-report.txt` file.
2. Build (as above). This will update the `impl-report.bs` and `impl-report.html` files.

As with the `index.bs` file, make sure you don't check in the `impl-report.bs` file.
It is also listed in the `.gitignore` file.

## Frequently Read Together

* <b>This spec:</b> [UI Events KeyboardEvent code Values](https://w3c.github.io/uievents-code/)
* UI Events KeyboardEvent key Values : [Github project](https://github.com/w3c/uievents-key/), [Link to spec](https://w3c.github.io/uievents-key/)
* UI Events : [Github project](https://github.com/w3c/uievents/), [Link to spec](https://w3c.github.io/uievents/)
