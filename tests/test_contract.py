def test_api_contract(app):
    schema = app.openapi()

    assert "/health" in schema["paths"]
    assert "/feeds/" in schema["paths"]
    assert "/articles/" in schema["paths"]

    feed_post_schema = schema["paths"]["/feeds/"]["post"]["responses"]["201"]
    assert "application/json" in feed_post_schema["content"]
    assert "$ref" in feed_post_schema["content"]["application/json"]["schema"]
    assert feed_post_schema["content"]["application/json"]["schema"]["$ref"] == "#/components/schemas/FeedRead"
