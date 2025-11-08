from libs.common.jsonapi import (
    serialize_resource,
    serialize_collection,
    serialize_error,
    serialize_errors,
)


def test_serialize_resource() -> None:
    result = serialize_resource(
        "products", "123", {"name": "Test", "price": "99.99"}
    )

    assert result["data"]["type"] == "products"
    assert result["data"]["id"] == "123"
    assert result["data"]["attributes"]["name"] == "Test"
    assert result["data"]["attributes"]["price"] == "99.99"


def test_serialize_collection() -> None:
    items = [
        {"id": "1", "name": "Product 1", "price": "10.00"},
        {"id": "2", "name": "Product 2", "price": "20.00"},
    ]

    result = serialize_collection("products", items, page=1, size=10, total=2)

    assert len(result["data"]) == 2
    assert result["data"][0]["type"] == "products"
    assert result["data"][0]["id"] == "1"
    assert result["meta"]["page"]["number"] == 1
    assert result["meta"]["page"]["size"] == 10
    assert result["meta"]["page"]["total"] == 2


def test_serialize_error() -> None:
    result = serialize_error("404", "Not Found", "Resource not found")

    assert len(result["errors"]) == 1
    assert result["errors"][0]["status"] == "404"
    assert result["errors"][0]["title"] == "Not Found"
    assert result["errors"][0]["detail"] == "Resource not found"


def test_serialize_errors() -> None:
    errors = [
        {"status": "400", "title": "Bad Request", "detail": "Invalid input"},
        {"status": "422", "title": "Validation Error", "detail": "Missing field"},
    ]

    result = serialize_errors(errors)

    assert len(result["errors"]) == 2
    assert result["errors"][0]["status"] == "400"
    assert result["errors"][1]["status"] == "422"

