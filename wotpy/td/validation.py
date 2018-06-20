#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Schemas following the JSON Schema specification used to validate the shape of Thing Description documents.
"""

import copy
import re

from wotpy.td.enums import InteractionTypes

REGEX_SAFE_NAME = r"^[a-zA-Z0-9_-]+$"
REGEX_ANY_URI = r"^((\w+:(\/?\/?)[^\s]+)|((..\/)+)[^\s]*)$"

DATA_TYPES_ENUM = [
    "array",
    "boolean",
    "number",
    "integer",
    "object",
    "string",
    "null"
]

SCHEMA_DATA_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "id": "http://fundacionctic.org/schemas/data-schema.json",
    "oneOf": [
        {
            "type": "string",
            "enum": DATA_TYPES_ENUM
        },
        {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "type": {
                    "type": "string",
                    "enum": DATA_TYPES_ENUM
                },
                "const": {},
                "enum": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": [
                "type"
            ]
        }
    ]
}

SCHEMA_SECURITY_SCHEME = {
    "$schema": "http://json-schema.org/schema#",
    "id": "http://fundacionctic.org/schemas/security-scheme.json",
    "type": "object",
    "properties": {
        "scheme": {"type": "string"}
    },
    "required": [
        "scheme"
    ]
}

SCHEMA_LINK = {
    "$schema": "http://json-schema.org/schema#",
    "id": "http://fundacionctic.org/schemas/link.json",
    "type": "object",
    "properties": {
        "rel": {"type": "string"},
        "href": {"type": "string"},
        "mediaType": {
            "type": "string",
            "default": "application/json"
        },
        "anchor": {"type": "string"}
    },
    "required": [
        "href"
    ]
}

SCHEMA_FORM = {
    "$schema": "http://json-schema.org/schema#",
    "id": "http://fundacionctic.org/schemas/form.json",
    "type": "object",
    "properties": {
        "href": {"type": "string"},
        "mediaType": {
            "type": "string",
            "default": "application/json"
        },
        "rel": {"type": "string"},
        "security": SCHEMA_SECURITY_SCHEME
    },
    "required": [
        "href"
    ]
}

SCHEMA_PROPERTY = {
    "$schema": "http://json-schema.org/schema#",
    "id": "http://fundacionctic.org/schemas/property.json",
    "allOf": [
        SCHEMA_DATA_SCHEMA,
        {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "observable": {
                    "type": "boolean",
                    "default": False
                },
                "writable": {
                    "type": "boolean",
                    "default": False
                },
                "forms": {
                    "type": "array",
                    "items": SCHEMA_FORM
                }
            }
        }
    ]
}

SCHEMA_EVENT = copy.deepcopy(SCHEMA_PROPERTY)
SCHEMA_EVENT.update({"id": "http://fundacionctic.org/schemas/event.json"})

SCHEMA_ACTION = {
    "$schema": "http://json-schema.org/schema#",
    "id": "http://fundacionctic.org/schemas/action.json",
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "forms": {
            "type": "array",
            "items": SCHEMA_FORM
        },
        "input": SCHEMA_DATA_SCHEMA,
        "output": SCHEMA_DATA_SCHEMA,
        "label": {"type": "string"}
    }
}

SCHEMA_THING = {
    "$schema": "http://json-schema.org/schema#",
    "id": "http://fundacionctic.org/schemas/thing.json",
    "type": "object",
    "properties": {
        "security": {
            "type": "array",
            "items": SCHEMA_SECURITY_SCHEME
        },
        "id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "support": {"type": "string"},
        "base": {
            "type": "string",
            "pattern": REGEX_ANY_URI
        },
        "properties": {
            "type": "object",
            "patternProperties": {REGEX_SAFE_NAME: SCHEMA_PROPERTY},
            "additionalProperties": False
        },
        "actions": {
            "type": "object",
            "patternProperties": {REGEX_SAFE_NAME: SCHEMA_ACTION},
            "additionalProperties": False
        },
        "events": {
            "type": "object",
            "patternProperties": {REGEX_SAFE_NAME: SCHEMA_EVENT},
            "additionalProperties": False
        },
        "links": {
            "type": "array",
            "items": SCHEMA_LINK
        }
    },
    "required": [
        "id",
        "name"
    ]
}


def interaction_schema_for_type(interaction_type):
    """Returns the JSON schema that describes an
    interaction for the given interaction type."""

    type_schema_dict = {
        InteractionTypes.PROPERTY: SCHEMA_PROPERTY,
        InteractionTypes.ACTION: SCHEMA_ACTION,
        InteractionTypes.EVENT: SCHEMA_EVENT
    }

    assert interaction_type in type_schema_dict

    return type_schema_dict[interaction_type]


def is_valid_uri(val):
    """Returns True if the given value is a valid URI."""

    return False if re.match(REGEX_ANY_URI, val) is None else True


def is_valid_safe_name(val):
    """Returns True if the given value is a safe machine-readable name."""

    return False if re.match(REGEX_SAFE_NAME, val) is None else True


class InvalidDescription(Exception):
    """Exception raised when a document for an object
    in the TD hierarchy has an invalid format."""

    pass
