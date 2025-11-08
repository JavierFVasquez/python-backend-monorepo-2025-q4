python_sources(
    name="inventory_lib",
    sources=["**/*.py"],
    dependencies=[
        "//libs/common:common",
    ],
)

pex_binary(
    name="app",
    entry_point="main.py",
    dependencies=[":inventory_lib"],
)
