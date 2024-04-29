#!/usr/bin/python3
'''
git hook script to mirror git repository to local disk and use it instead of remote repository.

Basic mechanism:
1. git can accept '-c' option to set configuration as ephemeral option.
2. git can accept 'url.<base>.insteadOf' configuration to replace base url
   with another url.
3. clone from actual remote repository at the first time if local mirror does
   not exist and clone from local mirror.
4. fetch from actual remote repository if local mirror exists and fetch
   from local mirror.
'''

import sys
import os
import re
import subprocess

DEBUG_ON = os.environ.get('DEBUG_ON', None)
if DEBUG_ON is not None:
    DEBUG_ON = True
GIT_PATH = "/usr/bin/git"
HOME_DIR = os.path.expanduser("~")
MIRROR_ROOT = os.path.join(HOME_DIR, ".git-mirror")

options = [
    # https:// request will be redirected to MIRROR_ROOT local path
    "-c", f"url.{MIRROR_ROOT}/.insteadOf=https://",

    # http:// request will be redirected to MIRROR_ROOT local path
    "-c", f"url.{MIRROR_ROOT}/.insteadOf=http://",

    # git:// request will be redirected to MIRROR_ROOT local path
    "-c", f"url.{MIRROR_ROOT}/.insteadOf=git://",
]

hook_commands = (
    "clone",
    "fetch",
    "pull",
    "push",
    "remote",
)

def find_hook_command(argv):
    '''
    Find git subcommand to hook.
    '''
    for arg in argv:
        if arg in hook_commands:
            return arg
    return None

def find_url(argv):
    '''
    Find url parameter from arugments.
    '''
    url = None
    path = None
    for arg in argv:
        match = re.match(r'^((https?|git)://)(.+)', arg)
        if match:
            url = arg
            path   = match.group(3)
    return url, path

def run_git_command_with_pipe(argv):
    '''
    Run git command with pipe.
    '''
    command = argv.copy()
    command.insert(0, GIT_PATH)
    if DEBUG_ON:
        print("DEBUG: run", command, file=sys.stderr)
    with subprocess.Popen(command) as process:
        exit_code = process.wait()
        return exit_code

def run_command_with_pipe_and_return_output(command):
    '''
    Run command with pipe and return output.
    '''
    if DEBUG_ON:
        print("DEBUG: run", command, file=sys.stderr)
    with subprocess.Popen(command, stdout=subprocess.PIPE, text=True) as process:
        stdout, _ = process.communicate()
        return stdout.splitlines()
    return None

def get_git_remote_name():
    '''
    Get git remote name.
    '''
    return run_command_with_pipe_and_return_output([GIT_PATH, 'remote'])

def get_git_remote_url(remote_name):
    '''
    Get git remote url.
    '''
    return run_command_with_pipe_and_return_output([GIT_PATH, 'remote', 'get-url', remote_name])

def mirror_or_fetch_to_local(url, path):
    '''
    Mirror or fetch to local repository.
    '''
    mirror_path = MIRROR_ROOT + "/" + path

    if not os.path.exists(mirror_path):
        params = ["clone", "--mirror", url, mirror_path]
    else:
        params = ["-C", mirror_path, "remote", "update", "-p"]
    exit_code = run_git_command_with_pipe(params)
    if exit_code != 0:
        if DEBUG_ON:
            print("FAILED: run", "git", params, file=sys.stderr)
        sys.exit(exit_code)
    else:
        if DEBUG_ON:
            print("SUCCESS: run", "git", params, file=sys.stderr)

def main(argv):
    '''
    Main function.
    '''
    exit_code = 1
    url, path = find_url(argv)
    if url is not None and path is not None:
        mirror_or_fetch_to_local(url, path)
    command = find_hook_command(argv)
    if command == "clone":
        mirror_or_fetch_to_local(url, path)
    elif command in ('fetch', 'pull'):
        remote_names = get_git_remote_name()
        for remote_name in remote_names:
            urls = get_git_remote_url(remote_name)
            url, path = find_url(urls)
            mirror_or_fetch_to_local(url, path)

    if command in ('clone', 'fetch', 'pull'):
        params = options.copy()
        params.extend(argv)
    else:
        params = argv

    exit_code = run_git_command_with_pipe(params)
    sys.exit(exit_code)

if __name__ == "__main__":
    main(sys.argv[1:])
