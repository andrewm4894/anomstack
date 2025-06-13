# Contributing guidelines

## Before contributing

Welcome to [Anomstack](https://github.com/andrewm4894/anomstack)! Before submitting your pull requests, please ensure that you __read the whole guidelines__. If you have any doubts about the contributing guide, please feel free to [state it clearly in an issue](https://github.com/andrewm4894/anomstack/issues/new).

## Contributing

### Contributor

We are delighted that you are considering contributing to Anomstack!
By being one of our contributors, you agree and confirm that:

- You did your work - no plagiarism allowed.
  - Any plagiarized work will not be merged.
- Your work will be distributed under [MIT License](LICENSE) once your pull request is merged.
- Your submitted work fulfills or mostly fulfills our styles and standards.

__New implementation__ is welcome!

__Improving comments__ and __writing proper tests__ are also highly welcome.

### Contribution

We appreciate any contribution, from fixing a grammar mistake in a comment to implementing complex features. Please read this section if you are contributing your work.

#### Issues

If you are interested in resolving an [open issue](https://github.com/andrewm4894/anomstack/issues), simply make a pull request with your proposed fix.

__Do not__ create an issue to contribute a feature. Please submit a pull request instead.

Please help us keep our issue list small by adding `Fixes #{$ISSUE_NUMBER}` to the description of pull requests that resolve open issues.
For example, if your pull request fixes issue #10, then please add the following to its description:
```
Fixes #10
```
GitHub will use this tag to [auto-close the issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) if and when the PR is merged.

#### Pre-commit plugin
Use [pre-commit](https://pre-commit.com/#installation) to automatically format your code to match our coding style:

```bash
python3 -m pip install pre-commit  # only required the first time
pre-commit install
```
That's it! The plugin will run every time you commit any changes. If there are any errors found during the run, fix them and commit those changes. You can even run the plugin manually on all files:

```bash
pre-commit run --all-files --show-diff-on-failure
```

#### Coding Style

We want your work to be readable by others; therefore, we encourage you to note the following:

- Please write in Python 3.12+. For instance: `print()` is a function in Python 3 so `print "Hello"` will *not* work but `print("Hello")` will.
- Please focus hard on the naming of functions, classes, and variables.  Help your reader by using __descriptive names__ that can help you to remove redundant comments.
  - Single letter variable names are *old school* so please avoid them unless their life only spans a few lines.
  - Expand acronyms because `gcd()` is hard to understand but `greatest_common_divisor()` is not.
  - Please follow the [Python Naming Conventions](https://pep8.org/#prescriptive-naming-conventions) so variable_names and function_names should be lower_case, CONSTANTS in UPPERCASE, ClassNames should be CamelCase, etc.

- We encourage the use of Python [f-strings](https://realpython.com/python-f-strings/#f-strings-a-new-and-improved-way-to-format-strings-in-python) where they make the code easier to read.

- All submissions will need to pass the test `ruff .` before they will be accepted so if possible, try this test locally on your Python file(s) before submitting your pull request.

  ```bash
  python3 -m pip install ruff  # only required the first time
  ruff .
  ```

- Original code submission require docstrings or comments to describe your work.

- More on docstrings and comments:

  If you used a Wikipedia article or some other source material to create your algorithm, please add the URL in a docstring or comment to help your reader.

  The following are considered to be bad and may be requested to be improved:

  ```python
  x = x + 2	# increased by 2
  ```

  This is too trivial. Comments are expected to be explanatory. For comments, you can write them above, on or below a line of code, as long as you are consistent within the same piece of code.

  We encourage you to put docstrings inside your functions but please pay attention to the indentation of docstrings. The following is a good example:

  ```python
  def sum_ab(a, b):
      """
      Return the sum of two integers a and b.
      """
      return a + b
  ```

- Write tests (especially [__doctests__](https://docs.python.org/3/library/doctest.html)) to illustrate and verify your work.  We highly encourage the use of _doctests on all functions_.

  ```python
  def sum_ab(a, b):
      """
      Return the sum of two integers a and b
      >>> sum_ab(2, 2)
      4
      >>> sum_ab(-2, 3)
      1
      >>> sum_ab(4.9, 5.1)
      10.0
      """
      return a + b
  ```

  These doctests will be run by pytest as part of our automated testing so please try to run your doctests locally and make sure that they are found and pass:

  ```bash
  python3 -m doctest -v my_submission.py
  ```

  The use of the Python built-in `input()` function is __not__ encouraged:

  ```python
  input('Enter your input:')
  # Or even worse...
  input = eval(input("Enter your input: "))
  ```

  However, if your code uses `input()` then we encourage you to gracefully deal with leading and trailing whitespace in user input by adding `.strip()` as in:

  ```python
  starting_value = int(input("Please enter a starting value: ").strip())
  ```

  The use of [Python type hints](https://docs.python.org/3/library/typing.html) is encouraged for function parameters and return values.

  ```python
  def sum_ab(a: int, b: int) -> int:
      return a + b
  ```

- [__List comprehensions and generators__](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) are preferred over the use of `lambda`, `map`, `filter`, `reduce` but the important thing is to demonstrate the power of Python in code that is easy to read and maintain.

- Avoid importing external libraries for basic algorithms. Only use those libraries for complicated algorithms.
- If you need a third-party module that is not in the file __requirements.txt__, please add it to that file as part of your submission.

#### Testing and Coverage

- All new code should include appropriate tests. See the [`tests/README.md`](./tests/README.md) for detailed testing guidelines.
- Run the full test suite before submitting: `pytest tests/`
- Check test coverage: `pytest tests/ --cov=anomstack --cov-report=term-missing`
- The project currently maintains **47% test coverage**. Contributions that increase coverage are especially welcome!

#### Updating the Coverage Badge

### Automatic Updates (Recommended) ✨

The coverage badge is **automatically updated** by GitHub Actions whenever code is pushed to the main branch:

1. **The pytest workflow** runs all tests with coverage analysis
2. **Extracts the coverage percentage** from the results  
3. **Updates the badge** in README.md with the correct percentage and color
4. **Commits the changes** back to the repository with message: `🔄 Auto-update coverage badge to XX% [skip ci]`

This ensures the badge is always accurate and up-to-date without manual intervention.

### Pull Request Coverage Reports

When you create a pull request, the GitHub Action will automatically comment with:
- Current coverage percentage and color
- Whether coverage improved or decreased from baseline (47%)
- Link to detailed coverage report

### Manual Updates (If Needed)

If you need to update the coverage manually for any reason:

1. Run coverage analysis: `pytest tests/ --cov=anomstack --cov-report=term-missing`
2. Note the new coverage percentage from the output
3. Update the badge in `README.md` by changing the coverage percentage:
   ```markdown
   ![Coverage](https://img.shields.io/badge/Coverage-XX%25-color?logo=pytest)
   ```
4. Update the coverage percentage in `tests/README.md` as well
5. Use appropriate colors:
   - Red: < 30%
   - Orange: 30-49% 
   - Yellow: 50-69%
   - Green: 70-89%
   - Bright Green: ≥ 90%

#### Other Requirements for Submissions
- The file extension for code files should be `.py`.
- Strictly use snake_case (underscore_separated) in your file_name, as it will be easy to parse in future using scripts.
- If possible, follow the standard *within* the folder you are submitting to.
- If you have modified/added code work, make sure the code compiles before submitting.
- If you have modified/added documentation work, ensure your language is concise and contains no grammar errors.

- Most importantly,
  - __Be consistent in the use of these guidelines when submitting.__
  - Happy coding!
