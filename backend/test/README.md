## How to Run the Test

First, make sure you have Python installed (preferably version 3.10 or higher. But prefer to use version 3.11).  

First make sure to enter the virtual environmet first that have been explained at the root diretory [how to set up the Virtual Environment](/README.md#installing-environment). After you enter the Virtual Environment, you can install pytest.

```bash
pip install pytest
```

Even though we use pytest, but the truth is we use [unittest](https://docs.python.org/3/library/unittest.html) framework to make the unit test case. Pytest is used to run the test. So after success installing the pytest package, just run this to run the test on the root directory of this project

```bash
pytest .
```

This is optional, but if you want to see the coverage test case report install `pytest-cov`:
```bash
pip install pytest-cov
```

then to see the test case report, just run this:
```bash
pytest --cov
```

