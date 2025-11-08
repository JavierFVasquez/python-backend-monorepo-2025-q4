python_sources(
    name="inventory_lib",
)

pex_binary(
    name="app",
    entry_point="main.py",
    dependencies=[":inventory_lib"],
)

