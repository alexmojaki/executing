import subprocess as sp
import os

import shelve
import time

files = ["executing/_position_node_finder.py","tests/deadcode.py"]

py_version="py311"

def mutmut_run(num: int | None = None):
    cmd= [
            "mutmut",
            "run",
            "--paths-to-mutate",
            ",".join(files),
            "--runner",
            f"tox -e {py_version} -- --ff",
            *([str(num)] if num is not None else []),
        ]
    print(">"," ".join(cmd))
    sp.run(cmd)


def survived() -> set[str]:
    nums = sp.check_output(["mutmut", "result-ids", "survived"]).decode().split()
    if not all(num.isnumeric() for num in nums):
        return set()
    return set(nums)

with shelve.open("done.db") as done:
    while True:
        todo = survived() - done.keys()

        if not todo:
            mutmut_run()
            todo = survived() - done.keys()

        if not todo:
            break

        print(todo)
        for num in todo:
            sp.check_call(["git", "checkout", *files])

            mutmut_run(int(num))

            if num not in survived():
                continue


            header=sp.check_output(["mutmut", "show", str(num)]).decode()

            sp.check_call(["mutmut", "apply", str(num)])

            sp.check_call(
                ["tox", "-e", f"generate_small_sample-{py_version}"],
                env=os.environ | {"MUTMUT_HEADER": header},
            )

            sp.check_call(["git", "checkout", *files])
            sp.check_call(["tox","-e", py_version])

            done[num]=True

