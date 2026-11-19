import pytest


@pytest.fixture
def openapi_paths(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    return response.json()["paths"]


def test_openapi_describes_operations_and_parameters(openapi_paths):
    for path, operations in openapi_paths.items():
        for method, operation in operations.items():
            label = f"{method.upper()} {path}"
            assert operation.get("description"), label
            for parameter in operation.get("parameters", []):
                assert parameter.get("description"), (label, parameter["name"])
            for status, response in operation["responses"].items():
                if status in {"200", "201"}:
                    assert response["content"]["application/json"].get("schema"), label
                elif status == "204":
                    assert "content" not in response, label


@pytest.mark.parametrize(("method", "path", "errors"), [
    ("post", "/auth/login", {"401", "422"}),
    ("get", "/auth/me", {"401"}),
    ("post", "/restaurants", {"401", "403", "422"}),
    ("get", "/restaurants/mine", {"401", "403"}),
    ("put", "/restaurants/{restaurant_id}", {"401", "403", "404", "422"}),
    ("get", "/restaurants/{restaurant_id}/menu-items", {"404", "422"}),
    ("get", "/restaurants/{restaurant_id}/menu-items/{item_id}", {"404", "422"}),
    ("post", "/restaurants/{restaurant_id}/menu-items", {"401", "403", "404", "422"}),
    ("get", "/restaurants/{restaurant_id}/menu-items/manage", {"401", "403", "404", "422"}),
    ("put", "/restaurants/{restaurant_id}/menu-items/{item_id}", {"401", "403", "404", "422"}),
    ("patch", "/restaurants/{restaurant_id}/menu-items/{item_id}/deactivate", {"401", "403", "404", "422"}),
])
def test_openapi_lists_expected_client_errors(openapi_paths, method, path, errors):
    responses = openapi_paths[path][method]["responses"]
    assert {status for status in responses if status.startswith("4")} == errors
