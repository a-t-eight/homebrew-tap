# a-t-eight Homebrew tap

## Install

```sh
brew tap a-t-eight/tap
```

## Formulae

```sh
brew install a-t-eight/tap/lua@5.1
```

## Casks

```sh
brew install --cask a-t-eight/tap/xquartz@rc
brew install --cask a-t-eight/tap/chatgpt-classic@1.2026.119
brew install --cask a-t-eight/tap/chatgpt-classic@1.2026.160
brew install --cask a-t-eight/tap/v2rayn
brew install --cask a-t-eight/tap/v2rayn@pre-release
brew install --cask a-t-eight/tap/idevice-pair
```

## idevice_pair updates

The `idevice-pair` cask installs upstream's signed, notarized universal macOS app
to `/Applications/idevice_pair.app`. It follows stable GitHub releases with a
fixed version and SHA-256 checksum. Existing manual installations must be moved
aside before installing; the cask does not remove pairing records or app data.

Check upstream manually:

```sh
brew livecheck --cask a-t-eight/tap/idevice-pair
```

Once merged into `main`, the `idevice_pair cask` workflow checks every other
Monday at 01:37 UTC, anchored on 19 October 2026. Manual workflow dispatch also
checks immediately. A newer release is downloaded and verified for checksum,
bundle identity/version, both CPU architectures, code signature and Gatekeeper
acceptance before an update PR is opened. Homebrew style and strict audit must
also pass. Updates reuse the `automation/idevice-pair` branch and require manual
merging. No app is launched and no device pairing is performed by the workflow.

The workflow uses GitHub's built-in token and requires Actions to be allowed to
create pull requests. It does not require a personal token. Inspect the update
job's validation results; PR workflows created by the built-in token may require
approval in GitHub before they run.

After merging an update PR:

```sh
brew update
brew upgrade --cask a-t-eight/tap/idevice-pair
```

## Documentation

`brew help`, `man brew`, or check [Homebrew's documentation](https://docs.brew.sh).
