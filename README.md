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
brew install --cask a-t-eight/tap/displaycal-py3
```

## DisplayCAL updates

`displaycal-py3` installs the Python 3 fork's complete macOS application suite,
with separate checksums for Apple Silicon and Intel and an ArgyllCMS dependency.
The upstream 3.9.19 apps fail Gatekeeper assessment; the cask preserves quarantine
and does not modify signatures. Packaging checks do not establish GUI operation.

The **Update DisplayCAL fortnightly** workflow checks stable releases every
14 days, anchored to **5 October 2026 at 01:17 UTC** (12:17 pm Sydney daylight
time; 11:17 am Sydney standard time). GitHub starts a small cadence job every
Monday; alternate weeks skip the release-check job entirely. Scheduled runs may
be delayed or dropped by GitHub. The workflow must be merged into the default
branch before the schedule becomes active. A manual **Run workflow** bypasses
the date gate.

A new version must provide both DMGs and GitHub SHA-256 asset digests. The updater
downloads and hashes both files before changing the cask, then checks its style,
metadata, all eight app versions, architectures and minimum macOS requirement.
Signing results are recorded separately without bypasses. One reusable branch,
`automation/displaycal-py3`, opens or updates a PR; no PR is created when the
version is unchanged. Updates require a manual merge. After merging:

```sh
brew update
brew upgrade --cask a-t-eight/tap/displaycal-py3
```

The updater uses the repository's `GITHUB_TOKEN`, with write permissions scoped
to its update job. **Settings → Actions → General → Allow GitHub Actions to
create and approve pull requests** must be enabled. Bot-created PR checks may
need **Approve workflows to run**; the updater validates the change before
opening the PR regardless. No PAT or third-party service is required. GitHub
may disable scheduled workflows in inactive public repositories after 60 days.

Local validation (Python 3.11+, Homebrew, `gh`, and macOS for DMG inspection):

```sh
python3 -m unittest discover -s tests -v
python3 scripts/update_displaycal.py --due
python3 scripts/update_displaycal.py --verify-current
brew style Casks/displaycal-py3.rb
brew audit --cask a-t-eight/tap/displaycal-py3
bash scripts/verify_displaycal.sh work/displaycal
```

For the local audit, the cask in the installed tap must match the checkout being
tested. CI makes a runner-local tap from its checkout and copies the proposed
cask into it before invoking the named audit.

To stop automation, disable **Update DisplayCAL fortnightly** in GitHub Actions.
To remove the application while retaining settings and unrelated dependencies:

```sh
HOMEBREW_NO_AUTOREMOVE=1 brew uninstall --cask a-t-eight/tap/displaycal-py3
```

## Documentation

`brew help`, `man brew`, or check [Homebrew's documentation](https://docs.brew.sh).
