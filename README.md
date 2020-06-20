# JSON Database Tools

These tools convert JSON data to/from some strange database formats:
- File Systems
- Git

Note that the Git backend expects to work with a bare repository.

## Examples:

### File System:
```
# To file system from json:
./json_to_db.py examples/data.json --fs `pwd`/examples/fs
```

This will create a file system with the same data as in the json file given. Browse at the path above.

```
# From file system from json:
./db_to_json.py --fs `pwd`/examples/fs
```

This will print the data at the file system given above as json to stdout.


### Git:
Note: These example rely on you manually creating a git repo at the listed directory. Do so by running:
```
# Make the directory.
mkdir -p examples/git

# Go there, saving where we are.
pushd examples/git

# Initialise a bare git repository.
git init --bare

# Go back to where we were.
popd
```

```
# To Git from json:
./json_to_db.py examples/data.json --git `pwd`/examples/git --branch master --commit-message "This is the first commit"
```

This will create a file system with the same data as in the json file given. Browse at the path above.

```
# From file system from json:
./db_to_json.py --git `pwd`/examples/git --branch master
```

This will print the data at the git repository given above as json to stdout.

