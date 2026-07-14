"""Tool schemas shown to the model by Hermes."""

MANTLE_STATUS = {
    "name": "mantle_status",
    "description": (
        "Inspect the bundled Mantle OS reference implementation and report its "
        "version and available command surface. This operation is read-only."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
}
