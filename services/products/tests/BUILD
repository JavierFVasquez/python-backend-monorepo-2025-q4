python_test_utils(
    name="test_utils",
    sources=["conftest.py"],
    dependencies=[
        "//services/products:products_lib",
    ],
)

python_tests(
    name="tests",
    sources=["**/*_test.py", "**/test_*.py", "**/tests.py"],
    dependencies=[
        "//services/products:products_lib",
    ],
)

