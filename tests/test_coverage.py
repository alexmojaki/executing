import os
import subprocess
import sys
from pathlib import Path

import coverage

ROOT = Path(__file__).resolve().parents[1]


def test_coverage_includes_package(tmp_path):
    script = tmp_path / "sample.py"
    script.write_text("import executing\n", encoding="utf-8")
    data_file = tmp_path / ".coverage"
    env = dict(os.environ, COVERAGE_FILE=str(data_file))
    # The temporary script must import the checkout, not a non-editable install.
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(ROOT)
    if pythonpath:
        env["PYTHONPATH"] += os.pathsep + pythonpath
    # Keep this measurement independent of an outer coverage run.
    env.pop("COVERAGE_PROCESS_START", None)
    env.pop("COVERAGE_PROCESS_CONFIG", None)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--rcfile=" + str(ROOT / "pyproject.toml"),
            str(script),
        ],
        cwd=ROOT,
        env=env,
        check=True,
    )

    cov = coverage.Coverage(
        config_file=str(ROOT / "pyproject.toml"), data_file=str(data_file)
    )
    cov.combine()
    cov.load()
    measured = {
        Path(filename).as_posix() for filename in cov.get_data().measured_files()
    }
    expected = {
        filename.relative_to(ROOT).as_posix()
        for filename in (ROOT / "executing").glob("*.py")
    }
    assert measured == expected
    assert cov.get_data().lines(str(Path("executing") / "__init__.py"))
    if sys.version_info >= (3, 11):
        assert cov.get_data().lines(str(Path("executing") / "_position_node_finder.py"))
