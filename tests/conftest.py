

from typing import Optional, Sequence, Union
from executing._pytest_utils import is_pytest_compatible
import _pytest.assertion.rewrite as rewrite
import importlib.machinery
import types

if not is_pytest_compatible():
    original_find_spec = rewrite.AssertionRewritingHook.find_spec


    def find_spec(
        self,
        name: str,
        path: Optional[Sequence[Union[str, bytes]]] = None,
        target: Optional[types.ModuleType] = None,
    ) -> Optional[importlib.machinery.ModuleSpec]:

        if name == "tests.test_main":
            return None
        return original_find_spec(self, name, path, target)


    rewrite.AssertionRewritingHook.find_spec = find_spec
