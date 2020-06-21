#!/usr/bin/env python3

import flask

app = flask.Flask(__name__)

def is_valid_path(value):
    import re
    print(value)
    search = re.compile(r'[^a-zA-Z0-9_#/.-]').search
    return not bool(search(value))

@app.route('/', methods=['GET'])
def get_branch():
    from db_to_json import ToJSON, FromGit
    from flask import request, jsonify
    from pathlib import Path

    if 'branch' in request.args:
        branch = request.args['branch']
        if not is_valid_path(branch):
            return "Error: branch name is invalid."
    else:
        return "Error: No id field provided. Please specify an id."

    if 'subtree' in request.args:
        subtree = request.args['subtree']
    else:
        subtree = ""

    if is_valid_path(subtree):
        subtree = Path(subtree)
    else:
        return "Error: subtree path is invalid."

    path = Path.cwd() / "examples/git"
    reader = ToJSON(FromGit(path, branch), init_path=subtree)
    data = reader.convert()

    return jsonify(data)


def main():
    from argparse import ArgumentParser

    ap = ArgumentParser()
    ap.add_argument("--debug", action="store_true", default=False, help="Enable Flask debuging.")

    args = ap.parse_args()

    if args.debug:
        app.config["DEBUG"] = True

    app.run()


if __name__ == "__main__":
    main()
