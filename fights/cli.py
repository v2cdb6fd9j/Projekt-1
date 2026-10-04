"""python -m fights.cli render fights_projects/<name>/scene.yaml"""
import argparse

from . import render


def main():
    p = argparse.ArgumentParser(prog="fights")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="build a fight short from a scene.yaml")
    r.add_argument("scene")
    a = p.parse_args()
    print(render.render(a.scene))


if __name__ == "__main__":
    main()
