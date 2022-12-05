from test_main import TestFiles
from pathlib import Path
import hashlib

from pysource_minimize import minimize
import sys
import subprocess as sp
import textwrap
import os
import linecache
from executing import Source
from multiprocessing import Pool,get_context
import tempfile
import hashlib
import time

last_samples_dir = Path(__file__).parent / "last_samples"
last_samples_dir.mkdir(exist_ok=True)
samples_dir = Path(__file__).parent / "samples"


# big_samples = (Path(__file__).parent / "samples").glob("*.py")
# big_samples = list(Path.home().rglob("*.py"))
small_samples = Path(__file__).parent / "small_samples"


def big_samples():
    yield from last_samples_dir.rglob("*.py")
    yield from samples_dir.rglob("*.py")

    hashes = set()
    root = Path.home()
    # root = Path(__file__).parent / "samples"
    for p in root.rglob("*.py"):
        try:
            content = p.read_text()
        except:
            continue

        if content.count("\n") > 100000:
            continue

        h = hashlib.sha256(content.encode()).hexdigest()
        if h in hashes:
            continue
        hashes.add(h)
        yield p


def test_file(filename: Path):

    if filename.read_text().count("\n") > 50000:
        return True, filename

    # clear caches
    linecache.clearcache()
    for cache_name in ("__source_cache_with_lines", "__executing_cache"):
        if hasattr(Source, cache_name):
            delattr(Source, cache_name)

    test = TestFiles()
    try:
        test.check_filename(filename, check_names=True)
    except:
        return False, filename

    return True, filename


def main():

    end_time=time.time()+60*60

    with get_context("spawn").Pool(maxtasksperchild=100) as p:

        for result, filename in p.imap_unordered(test_file, big_samples()):

            break_file=Path(__file__).parent/"break_generate"
            if break_file.exists():
                break_file.unlink()
                sys.exit(0)

            if time.time()>end_time:
                print("Timeout")
                sys.exit(0)


            if not result:
                try:
                    failing_code = filename.read_text()
                except:
                    continue
                print(f"{filename} fails the tests -> minimize")
                break
        else:
            print("no failing tests")
            return

        p.terminate()

    (
        last_samples_dir / f"{hashlib.sha256(failing_code.encode()).hexdigest()}.py"
    ).write_text(failing_code)

    def checker(source: str):
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(source.encode())
            tmp_file.flush()
            return not test_file(Path(tmp_file.name))[0]

    min_code = minimize(failing_code, checker)
    name = f"{hashlib.sha256(min_code.encode()).hexdigest()}.py"

    mutmut_header = os.environ.get("MUTMUT_HEADER", None)
    header = ""
    if mutmut_header != None:
        header = (
            "This sample was generated for the following code mutation detected by mutmut:\n\n"
            + mutmut_header
        )

        header = textwrap.indent(header, "# ", lambda s: True) + "\n"
        name = f"{hashlib.sha256(header.encode()).hexdigest()}.py"

    min_code = header + min_code

    print(min_code)
    (small_samples / name).write_text(min_code)


if __name__ == "__main__":
    main()
