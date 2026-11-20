# more-itertools: project guide for Claude

## About the project
- more-itertools is a pure Python library of tools for working with iterables.
- It extends the standard library's `itertools` module with more building blocks.
- The main code lives in two files:
  - `more_itertools/more.py`: original functions and classes written for this library.
  - `more_itertools/recipes.py`: functions based on the recipes in the Python `itertools` docs.
- Type stubs live next to the code in `.pyi` files. Keep them in sync with any signature change.
- There are no runtime dependencies, and there must never be any.

## Supported Python versions
- Check `pyproject.toml` for the minimum supported version before using newer syntax.
- Don't use features that only exist in the newest Python release.
- Use `from __future__ import annotations` only where the module already does.

## Code style
- Follow the existing style in the file you are editing, even if you prefer another one.
- Line length is 79 characters.
- Use single quotes for strings, except where a string contains a single quote.
- Imports are grouped: standard library first, then local imports.
- Within each group, imports are sorted alphabetically.
- Prefer small, readable functions over clever one-liners.
- Prefer generators over building full lists, so functions stay lazy.
- Never consume more of an iterator than needed.
- Avoid recursion; inputs can be very long.
- Don't add type hints in `.py` files: they live in the `.pyi` stubs.
- Add new public names to `__all__` in the module, in alphabetical order.

## Docstrings
- Every public function needs a docstring.
- The first line says what the function returns or yields, in one sentence.
- Include at least one doctest example, using `>>>`.
- Show the edge cases in examples: empty input, `n=0`, and a short final chunk.
- Mention any `ValueError` or `TypeError` the function raises, and when.
- Cross-reference related functions with ``:func:`name` ``.
- Keep examples short: three or four lines each.

## Tests
- Tests live in `tests/test_more.py` and `tests/test_recipes.py`.
- Run the whole suite with `python -m unittest -v`.
- Run one test class with `python -m unittest -v tests.test_more.ChunkedTests`.
- Every bug fix needs a test that fails before the fix and passes after it.
- Every new function needs tests for: normal input, empty input, invalid arguments, and laziness.
- Test laziness by passing an infinite iterator and taking a few items.
- Doctests in docstrings run as part of the suite, so keep them correct.
- Don't use `pytest` features: the suite uses plain `unittest`.

## Error handling
- Raise `ValueError` for a bad value, such as a negative `n`.
- Raise `TypeError` for a bad type, such as a non-iterable.
- Error messages are lower case and don't end with a full stop.
- Validate arguments before consuming any items from the iterator.
- Don't catch broad exceptions: let unexpected errors propagate.

## Performance
- Many functions are used in hot loops, so avoid needless work per item.
- Prefer `itertools` and `collections.deque` over manual loops where it is clearer.
- Benchmark with `python -m timeit` before and after a change that claims to be faster.
- Record benchmark numbers in the pull request description.

## Workflow: fixing a bug
1. Reproduce the bug with a failing test first.
2. Find the smallest change that fixes it.
3. Run the full test suite.
4. Update the docstring if the behaviour changed.
5. Add a line to `docs/versions.rst` under the next release.

## Workflow: adding a new function
1. Check that nothing similar already exists in `more.py` or `recipes.py`.
2. Check that the standard library doesn't already provide it.
3. Write the function in `more.py`, keeping it lazy.
4. Add it to `__all__`.
5. Add type stubs to `more.pyi`.
6. Add tests, including edge cases.
7. Add it to the right section of `docs/api.rst`.
8. Add a line to `docs/versions.rst`.

## Workflow: reviewing a pull request
- Check that the change is small and focused on one thing.
- Check that tests were added and that they test edge cases.
- Check docstrings and doctests.
- Check the type stubs.
- Check that nothing consumes the iterator too early.
- Check the changelog entry.
- Be kind and specific in review comments: suggest code, not just problems.

## Workflow: release
1. Make sure the main branch passes all tests on every supported Python version.
2. Update the version number in `more_itertools/__init__.py`.
3. Move the changelog entries under the new version heading in `docs/versions.rst`.
4. Build the docs and check for warnings.
5. Tag the release as `vX.Y.Z`.
6. Build the sdist and wheel, and upload them with `twine`.
7. Check the release page on PyPI.

## Documentation
- The docs are built with Sphinx from the `docs/` folder.
- Build them with `make -C docs html`.
- Every public function appears in `docs/api.rst`, grouped by purpose.
- Keep section headings short.

## Communication
- When unsure what the user wants, ask one short question.
- Explain changes in plain words, with the file and function names.
- Show diffs for any change before applying it.
- Keep answers short unless the user asks for detail.
