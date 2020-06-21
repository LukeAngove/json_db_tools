#!/usr/bin/env python3

import flask

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def get_branch():
    from db_to_json import ToJSON, FromGit
    from flask import request, jsonify
    from pathlib import Path

    if 'branch' in request.args:
        branch = request.args['branch']
    else:
        return "Error: No id field provided. Please specify an id."

    path = Path.cwd() / "examples/git"
    reader = ToJSON(FromGit(path, branch))
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
