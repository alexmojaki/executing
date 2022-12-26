import subprocess as sp
import os

import shelve
import time

files = ["executing/_position_node_finder.py", "tests/deadcode.py"]

py_version = "py311"


def mutmut_run(num: str | None = None):
    cmd = [
        "mutmut",
        "run",
        "--paths-to-mutate",
        ",".join(files),
        "--runner",
        f"tox -e {py_version} -- --ff",
        *([num] if num is not None else []),
    ]
    print(">", *cmd)
    sp.run(cmd)


def survived() -> set[str]:
    """
    set of all the ids which survived
    """
    nums = sp.check_output(["mutmut", "result-ids", "survived"]).decode().split()
    if not all(num.isnumeric() for num in nums):
        return set()
    return set(nums)


def main():
    # Mutmut is not really build for this kind of integration.
    # This is the reason for some weird code here.

    # make sure that there are no known bugs
    sp.check_call(["git", "checkout", *files])
    sp.check_call(["tox", "-e", py_version])

    # done.db contains all mutmut ids which have been already tried to fix.
    # Useful if this is run multiple times
    with shelve.open("done.db") as done:
        while True:
            todo = survived() - done.keys()

            if not todo:
                # mutmut has to run without id first
                # It also only checks for the first 100 untested mutations,
                # `not todo` does not imply that there is nothing more to test
                mutmut_run()
                todo = survived() - done.keys()

            if not todo:
                break

            print("survived mutations todo:", todo)
            for num in todo:
                # make sure to base this run on clean files
                sp.check_call(["git", "checkout", *files])

                # applies the mutated state to the files and runs the mutation
                mutmut_run(num)

                # skip if the mutation has not survived (is covered by some tests)
                if num not in survived():
                    continue

                header_diff = sp.check_output(["mutmut", "show", num]).decode()

                sp.check_call(["mutmut", "apply", num])

                # generate a sample for the mutmut run
                sp.check_call(
                    ["tox", "-e", f"generate_small_sample-{py_version}"],
                    env=os.environ | {"MUTMUT_HEADER": header_diff},
                )

                sp.check_call(["git", "checkout", *files])

                # The normal tests should pass.
                # There are some cases where generate_small_sample found a different bug
                # and the tests failed.
                # this script will fail in this case and the bug should be fixed by the developer
                result = sp.run(["tox", "-e", py_version])
                if result.returncode != 0:
                    print(
                        "generate_small_sample found a different bug that should be fixed by the developer"
                    )
                    exit(1)

                done[num] = True


if __name__ == "__main__":
    main()
