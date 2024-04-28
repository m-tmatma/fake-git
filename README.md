# fake_git

This script can create local cache of git repository and clone/fetch from the cache transparently.

`fake_git` relies on `-c` git option and 'url.<base>.insteadOf' configuration to replace base url with another url.

When you first clone a remote repository, `fake_git` tries to clone from the original reposotory to local reposotory(local cache).
But when you clone it in the second time, `fake_git` tries to clone from the local cache.

Once you clone a repository, `fake_git` tries to update the local cache first by running git fetch, and it fetches from the local cache.

## Installation

1. Copy `fake_git.py` to somewhere in your computer
2. create symbolic link as `git` or rename `fake_git.py` to `git`.
3. Include the location of the `git` script to envioromental variable (`PATH`)
4. Use `git` command normally.

## Internal behavior

### clone

Example

```
./fake_git.py clone https://git.yoctoproject.org/git/poky
```

1. `/usr/bin/git clone --mirror https://git.yoctoproject.org/git/poky ${HOME}/.git-mirror/git.yoctoproject.org/git/poky`
2. `/usr/bin/git -c url.${HOME}/.git-mirror/.insteadOf=https:// clone https://git.yoctoproject.org/git/poky`

## fetch

Example

```
./fake_git.py fetch
```

1. Update the local cache
    1. `/usr/bin/git remote get-url $(/usr/bin/git remote)`
    2. The output is `https://git.yoctoproject.org/git/poky`
    3. Extract the cache directory `${HOME}/.git-mirror/git.yoctoproject.org/git/poky`
    4. `/usr/bin/git -C ${HOME}/.git-mirror/git.yoctoproject.org/git/poky remote update -p`
2. Fetch from the local cache
    1. `/usr/bin/git -c url.${HOME}/.git-mirror/.insteadOf=https:// fetch`
