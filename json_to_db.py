#!/usr/bin/env python3

from pathlib import Path

class ToFileSystem:
    def __init__(self, base_path):
        self.base_path = base_path

    def make_tree(self, path, value):
        (self.base_path / path).mkdir(exist_ok=True)

    def make_leaf(self, path, value):
        with (self.base_path / path).open('w') as f:
            f.write("{}".format(value))

    def commit(self):
        pass # File systems don't need to commit; we did it already.

class ToGit:
    def __init__(self, git_path, commit_message, branch=None):
        self.git_path = git_path
        self.commit_message = commit_message
        self.branch = branch

    def make_tree(self, path, value):
        # Handle special case if the tree is empty, so that git makes something.
        # By default, git won't add anything to the tree; it only wants to monitor files.
        # We aren't using it for files; we are using it as a database, so this makes some sense.
        if len(value) == 0:
            from subprocess import run, PIPE
            # Make the empty tree node
            command = ["git", "hash-object", "-t", "tree", "/dev/null"] 
            p = run(command, cwd=self.git_path, input="{}".format(value), encoding="ascii", stdout=PIPE)
            sha = p.stdout[:-1]
            # Associate the empty tree with the path
            command = ["git", "update-index", "--add", "--cacheinfo", "100644", sha, str(path)]
            print("command: {}".format(" ".join(command)))
            p = run(command, cwd=self.git_path)


    def make_leaf(self, path, value):
        from subprocess import run, PIPE
        command = ["git", "hash-object", "--stdin", "-w"] 
        p = run(command, cwd=self.git_path, input="{}".format(value), encoding="ascii", stdout=PIPE)
        sha = p.stdout
        command = ["git", "update-index", "--add", "--cacheinfo", "100644", sha, path]
        p = run(command, cwd=self.git_path)

    def commit(self):
        from subprocess import run, PIPE
        command = ["git", "write-tree"]
        p = run(command, cwd=self.git_path, stdout=PIPE)
        tree_sha = p.stdout.decode()[:-1] # Remove '\n'
        command = ["git", "show-ref", "--hash", self.branch]
        p = run(command, cwd=self.git_path, stdout=PIPE)
        previous_head = p.stdout.decode()[:-1] # Remove '\n'
        command = ["git", "commit-tree", tree_sha]
        if previous_head:
            command.append("-p")
            command.append(previous_head)
        p = run(command, cwd=self.git_path, input=self.commit_message.encode(), stdout=PIPE)
        new_head = p.stdout.decode()[:-1] # Remove '\n'

        command = ["git", "update-ref", "refs/heads/" + self.branch, new_head]
        p = run(command, cwd=self.git_path, input=self.commit_message.encode(), stdout=PIPE)
        final = p.stdout.decode()[:-1] # Remove '\n'

class FromJSON:
    custom_types = (
            "ref", # Reference to another part of the tree
    )

    custom_type_prefixes = tuple(v + ":" for v in custom_types)

    def __init__(self, writer):
        self.writer = writer 

    def convert(self, obj):
        self.from_json(obj)
        self.writer.commit()

    def from_json(self, obj, path=Path(), name=None):
        if isinstance(obj, dict):
            self.from_dict(obj, path, name)
        elif isinstance(obj, list):
            self.from_list(obj, path, name)
        else: # Is a value
            self.from_value(obj, path, name)

    def from_iterable(self, obj, path, name, iter_type, iterator):
        if name:
            # Make folder for this object
            key_name = name + "#" + iter_type
            new_path = path / key_name
            self.writer.make_tree(new_path, obj)
        else:
            new_path = path

        for k,v in iterator(obj):
            self.from_json(v, new_path, k)

    def from_dict(self, obj, path, name=None):
        new_path = self.from_iterable(obj, path, name, "dict", lambda obj: obj.items())

    def from_list(self, obj, path, name):
        from hashlib import sha256
        new_path = self.from_iterable(obj, path, name, "set", lambda obj: [(sha256(v.encode()).hexdigest(), v) for v in obj])

    def from_value(self, value, path, name):
        # Check for custom types if string
        if isinstance(value, str) and value.startswith(FromJSON.custom_type_prefixes):
            vtype, value = value.split(':', 1) # Limit to only the first instance
        else:
            vtype = type(value).__name__

        key_name = (name + "#" + vtype)
        new_path = path / key_name
        self.writer.make_leaf(new_path, value)

def main(argv):
    from argparse import ArgumentParser

    ap = ArgumentParser()
    ap.add_argument("json_file", type=str, help="JSON file to parse into output format.")
    ap.add_argument("--fs", type=str, default=None, help="Store JSON in file system format at the given path.")
    ap.add_argument("--git", type=str, default=None, help="Store JSON in git format at the given path.")
    ap.add_argument("--commit-message", type=str, default=None, help="Commit message used for git.")
    ap.add_argument("--branch", type=str, default=None, help="Branch used for git.")

    args = ap.parse_args()

    from json import load
    with open(args.json_file, "r") as f:
        data = load(f)

    if args.fs:
        path = Path(args.fs)
        path.mkdir(exist_ok=True)
        fs_maker = FromJSON(ToFileSystem(path))
        fs_maker.convert(data)

    if args.git:
        if not args.commit_message:
            raise(Error("When using git backend, you must supply a commit message"))
        if not args.branch:
            raise(Error("When using git backend, you must supply a branch name"))
        path = Path(args.git)
        git_maker = FromJSON(ToGit(path, args.commit_message, args.branch))
        git_maker.convert(data)

if __name__ == "__main__":
    main({})

