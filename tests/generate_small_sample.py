from test_main import TestFiles
from pathlib import Path
import hashlib

from pysource_minimize import minimize
import sys
import textwrap
import os
import linecache
from executing import Source
from multiprocessing import get_context
import tempfile
import hashlib
import time
import contextlib
import os
from rich.progress import Progress, track
from rich.syntax import Syntax
from rich.console import Console
import argparse

last_samples_dir = Path(__file__).parent / "last_samples"
last_samples_dir.mkdir(exist_ok=True)


small_samples = Path(__file__).parent / "small_samples"


def source_hash(source_code):
    return hashlib.sha256(source_code.encode("utf8")).hexdigest()


def big_samples(folder):
    yield from last_samples_dir.rglob("*.py")

    hashes = set()

    for p in folder.rglob("*.py"):
        try:
            content = p.read_text()
        except:
            continue

        if content.count("\n") > 50000:
            # Long files take too much time to check and are most likely generated code or repetitive
            continue

        h = source_hash(content)
        if h in hashes:
            continue
        hashes.add(h)
        yield p


def test_file(filename: Path):
    code = filename.read_text()

    # Clear caches to avoid accumulating too much data in memory.
    # This is usually not a problem for executing, but this usage scenario is different
    linecache.clearcache()
    for cache_name in ("__source_cache_with_lines", "__executing_cache"):
        if hasattr(Source, cache_name):
            delattr(Source, cache_name)

    test = TestFiles()
    try:
        with open(os.devnull, "w") as dev_null:
            with contextlib.redirect_stderr(dev_null):
                with contextlib.redirect_stdout(dev_null):
                    test.check_filename(filename, check_names=True)
    except:
        return False

    return True


def map_file(filename: Path):
    return test_file(filename), filename


def main():

    parser = argparse.ArgumentParser(prog="generate_small_samples")
    parser.add_argument("source_folder", default="tests/samples", nargs="?")

    args = parser.parse_args()

    folder = Path(args.source_folder)

    if not (folder.exists() and folder.is_dir()):
        print("source_folder has to be an existing directory")
        exit(1)

    console = Console()

    end_time = time.time() + 60 * 60

    console.print()
    console.print(f"Check files in tests/last_samples and {folder}:")
    console.print()

    with Progress() as progress:

        task_collect = progress.add_task(description="collect files ...", total=None)

        with get_context("spawn").Pool(maxtasksperchild=100) as p:
            files = list(
                progress.track(
                    big_samples(folder),
                    task_id=task_collect,
                    description="collect files...",
                )
            )
            progress.reset(task_collect, description="check files...", total=len(files))

            for result, filename in progress.track(
                p.imap_unordered(map_file, files), task_id=task_collect
            ):

                break_file = Path(__file__).parent / "break_generate"
                if break_file.exists():
                    break_file.unlink()
                    sys.exit(0)

                if time.time() > end_time:
                    print("Timeout")
                    sys.exit(0)

                if not result:
                    print(f"{filename} is failing the tests -> minimize\n")
                    failing_code = filename.read_text()
                    break
            else:
                progress.stop()
                console.print()
                console.print(
                    f"  :fireworks: checked {len(files)} files and everything was ok :fireworks:"
                )
                console.print()
                return

            p.terminate()

        (last_samples_dir / f"{source_hash(failing_code)}.py").write_text(failing_code)

        def check_for_error(source: str):
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(source.encode("utf8"))
                tmp_file.flush()
                test_ok = test_file(Path(tmp_file.name))
                return not test_ok

        task_minimize = progress.add_task("minimize...")

        def update(current, total):
            progress.update(task_minimize, completed=total - current, total=total)

        min_code = minimize(failing_code, check_for_error, progress_callback=update)

    name = f"{source_hash(min_code)}.py"

    mutmut_header = os.environ.get("MUTMUT_HEADER", None)
    header = ""
    if mutmut_header != None:
        header = (
            "This sample was generated for the following code mutation detected by mutmut:\n\n"
            + mutmut_header
        )

        header = textwrap.indent(header, "# ", lambda _: True) + "\n"
        name = f"{source_hash(header)}.py"

    min_code = header + min_code

    result_location = small_samples / name
    result_location.write_text(min_code)

    console.print()
    console.print("This is the minimal example to reproduce the bug:")
    console.print(Syntax.from_path(result_location, line_numbers=True))
    console.print()

    console.print(f"The example was saved under:\n  [blue]{result_location}")
    console.print()

    console.print("This example is now part of the test and can be run with:")
    console.print(
        f" > tox -e py{sys.version_info.major}{sys.version_info.minor} -- -k {name[:10]}"
    )
    console.print()

    console.print(
        "Have fun debugging :smiley: and dont forget to run me again,"
        " if you think you fixed everything."
    )


if __name__ == "__main__":
    main()
