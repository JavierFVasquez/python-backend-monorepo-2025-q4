from typing import Any


def serialize_resource(
    resource_type: str, resource_id: str, attributes: dict[str, Any]
) -> dict[str, Any]:
    return {"data": {"type": resource_type, "id": resource_id, "attributes": attributes}}


def serialize_collection(
    resource_type: str, items: list[dict[str, Any]], page: int, size: int, total: int
) -> dict[str, Any]:
    data = []
    for item in items:
        item_id = item.pop("id")
        data.append({"type": resource_type, "id": str(item_id), "attributes": item})

    return {
        "data": data,
        "meta": {"page": {"number": page, "size": size, "total": total}},
    }


def serialize_error(status: str, title: str, detail: str, source: dict[str, Any] | None = None) -> dict[str, Any]:
    error = {"status": status, "title": title, "detail": detail}
    if source:
        error["source"] = source
    return {"errors": [error]}


def serialize_errors(errors: list[dict[str, Any]]) -> dict[str, Any]:
    return {"errors": errors}

