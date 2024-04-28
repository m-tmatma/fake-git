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
