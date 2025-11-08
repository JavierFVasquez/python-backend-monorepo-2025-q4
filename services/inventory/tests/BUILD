python_test_utils(
    name="test_utils",
    sources=["conftest.py"],
    dependencies=[
        "//services/inventory:inventory_lib",
    ],
)

python_tests(
    name="tests",
    sources=["**/*_test.py", "**/test_*.py", "**/tests.py"],
    dependencies=[
        "//services/inventory:inventory_lib",
    ],
)

