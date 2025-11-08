python_sources(
    name="products_lib",
    sources=["**/*.py"],
    dependencies=[
        "//libs/common:common",
    ],
)

pex_binary(
    name="app",
    entry_point="main.py",
    dependencies=[":products_lib"],
)
