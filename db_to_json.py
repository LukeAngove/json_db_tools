#!/usr/bin/env python3

from pathlib import Path

class FromFileSystem:
    def __init__(self, base_path):
        self.base_path = base_path

    def read_tree(self, path):
        return (self.base_path / path).iterdir()

    def read_leaf(self, path):
        with (self.base_path / path).open('r') as f:
            return f.read()

class FromGit:
    def __init__(self, git_path, branch):
        self.git_path = git_path
        self.branch = branch

    def _read_path(self, path):
        from subprocess import run, PIPE
        command = ["git", "show", self.branch + ":" + str(path)]
        p = run(command, cwd=self.git_path, stdout=PIPE)
        values = p.stdout.decode().split('\n')
        return values
 

    def read_tree(self, path):
        values = self._read_path(path)
        return [path / Path(v) for v in values[2:-1]] # First line is 'tree <tree-name>:', 1 and -1 are empty lines.


    def read_leaf(self, path):
        value = self._read_path(path)[0]
        return value

class ToJSON:
    custom_types = (
            "ref", # Reference to another part of the tree
    )

    def __init__(self, reader):
        self.reader = reader

    def convert(self):
        data = self.to_dict("")
        return data

    def to_json(self, path):
        name, ftype = path.name.rsplit("#", 1) # Get the type from the file name
        if ftype == "dict":
            return name, self.to_dict(path)
        elif ftype == "set":
            return name, self.to_list(path)
        else: # Is a value
            return name, self.to_value(path, ftype)

    def to_iterable(self, path, init, action):
        res = init
        for f in self.reader.read_tree(path):
            k, v = self.to_json(f)
            action(res, k, v)
        return res

    def to_dict(self, path):
        return self.to_iterable(path, {}, lambda current, k, v: current.update({k:v}))

    def to_list(self, path):
        return self.to_iterable(path, [], lambda current, k, v: current.append(v))

    def to_value(self, path, ftype):
        data = self.reader.read_leaf(path)
        if ftype == "str":
            return data
        elif ftype == "int":
            return int(data)
        elif ftype in ToJSON.custom_types:
            return ftype + ":" + data

def main():
    from argparse import ArgumentParser
    from pathlib import Path
    from json import dumps

    ap = ArgumentParser()
    ap.add_argument("--fs", type=str, default=None, help="Store JSON in file system format at the given path.")
    ap.add_argument("--git", type=str, default=None, help="Store JSON in git format at the given path.")
    ap.add_argument("--branch", type=str, default=None, help="Branch used for git.")

    args = ap.parse_args()

    if args.fs:
        path = Path(args.fs)
        path.mkdir(exist_ok=True)
        db_to_json = ToJSON(FromFileSystem(path))
    elif args.git:
        if not args.branch:
            raise(Error("When using git backend, you must supply a branch name"))
        path = Path(args.git)
        db_to_json = ToJSON(FromGit(path, args.branch))
    else:
        raise Error("No backend specified.")

    data = db_to_json.convert()
    print(dumps(data, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
