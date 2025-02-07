import re, sys
from functools import reduce
from typing import List, Tuple, Optional, Dict, Union

from fhir.resources import get_fhir_model_class
from fhir.resources.fhirtypesvalidators import MODEL_CLASSES


FHIR_SCHEMAS = None
def loadFHIRSchemas() -> Dict[str, Dict]:
    global FHIR_SCHEMAS
    if FHIR_SCHEMAS is not None:
        return FHIR_SCHEMAS

    FHIR_SCHEMAS = {}
    for mc in MODEL_CLASSES:
        if mc in MODEL_CLASSES.keys():
            fhir_item = get_fhir_model_class(mc)
            assert fhir_item is not None, f"Model class {mc} not found."
            # get ordered schema
            schema = fhir_item.schema()
            if "properties" in schema:
                props = schema["properties"]
                props_order = fhir_item.elements_sequence()
                if "resourceType" in props_order:
                    props_order.remove("resourceType")
                    props_order.insert(0, "resource_type")
                else:
                    props_order.insert(0, "resource_type")
                props = dict(list(sorted(
                    props.items(),
                    key=lambda x: props_order.index(x[0]) if x[0] in props_order else 1000
                )))
                schema["properties"] = props
            FHIR_SCHEMAS[fhir_item.get_resource_type()] = schema
    return FHIR_SCHEMAS

def getSchemaForAllowedTypes(
        root_resources: List[str],
        blocked_types: List[str] = None,
        blocked_properties: List[str] = None,
        blocked_str_formats: List[str] = None,
        replace_property_names: List[str] = None,
        stop_at_new_base_resource: bool = True
    ) -> Dict:
    fhir_schemas = loadFHIRSchemas()

    if blocked_types is None:
        blocked_types = [
            "Meta",
            ".*Extension.*",
            "Attachment",
            "Annotation",
        ]

    if blocked_properties is None:
        blocked_properties = [
            "^\_.*",
            "extension",
            "fhir_comments",
            "renderedDosageInstruction",
            "contained",
            "text",
            "modifierExtension",
            "meta",
            "language",
            "id",
            "implicitRules"
        ]

    if blocked_str_formats is None:
        blocked_str_formats = [
            "binary"
        ]

    if replace_property_names is None:
        replace_property_names = {
            "resource_type": "resourceType",
        }


    definitions_with_dependencies = {
        resource_type: __schema_expand(
            schema,
            replace_property_names=replace_property_names,
            blocked_properties=blocked_properties,
            blocked_types=blocked_types,
            blocked_str_formats=blocked_str_formats,
            ref_prefix="#/$defs/",
            with_ref_items=True,
            stop_at_new_base_resource=stop_at_new_base_resource)
        for resource_type, schema
        in fhir_schemas.items()
    }
    definitions = { k: v[0] for k,v in definitions_with_dependencies.items() }

    # Reorder the properties

    def get_defs_for_resource_name(resource_name: str, known_items: List[str]=None) -> List[str]:
        if known_items is None:
            known_items = []

        if resource_name in known_items:
            return []

        new_items = [resource_name]
        for rn in definitions_with_dependencies[resource_name][1]:
            new_items += get_defs_for_resource_name(rn, known_items=known_items + new_items)

        return new_items

    dependencies = reduce(lambda x,y: x+y, [
        get_defs_for_resource_name(rn)
        for rn in root_resources
    ])
    unique_dependencies = list(set(dependencies))

    root_schema = {}
    root_schema["$schema"] = "https://json-schema.org/draft/2020-12/schema",

    root_schema = {
        "oneOf": [
            { "$ref": "#/$defs/" + resource_type }
            for resource_type in root_resources
        ]
    }

    root_schema["$defs"] = { k:v for k,v  in definitions.items() if k in unique_dependencies }
    return root_schema

def __schema_expand(
        schema: str,
        replace_property_names: Optional[List[str]] = None,
        blocked_properties: Optional[List[str]] = None,
        blocked_types: Optional[List[str]] = None,
        blocked_str_formats: Optional[List[str]] = None,
        in_properties: bool = False,
        ref_prefix: str = "#/$defs/",
        with_ref_items: bool = False,
        stop_at_new_base_resource: bool = False
    ) -> Union[Dict, Tuple[Dict, List[str]]]:

    if blocked_types is None:
        blocked_types = []
    if blocked_str_formats is None:
        blocked_str_formats = []
    if replace_property_names is None:
        replace_property_names = {}

    # Skip the expansion for the base types
    if isinstance(schema, str):
        return schema if not with_ref_items else (schema, [])
    if isinstance(schema, bool):
        return schema if not with_ref_items else (schema, [])
    if isinstance(schema, int):
        return schema if not with_ref_items else (schema, [])
    if isinstance(schema, float):
        return schema if not with_ref_items else (schema, [])
    # Expand along list items
    if isinstance(schema, list):
        sub_schema = [
            __schema_expand(
                entry,
                replace_property_names,
                blocked_properties,
                blocked_types,
                blocked_str_formats,
                in_properties=False,
                ref_prefix=ref_prefix,
                with_ref_items=with_ref_items,
                stop_at_new_base_resource=stop_at_new_base_resource,
            )
            for entry in schema
        ]
        if with_ref_items:
            sub_schema, ref_items = zip(*sub_schema)
            return list(sub_schema), list(reduce(lambda x,y: x+y, ref_items))
        else:
            return sub_schema

    # Dict is more complex...
    if isinstance(schema, dict):
        ref_items = []
        # If we are in a 'properties' declaration, a property could be named 'type' as well, but does not refer to a JSON schema 'type'
        if "type" in schema and not in_properties:
            # Stop early if the item is blocked
            stype = schema.get("type")

            for blocked_item in blocked_types:
                if re.match(blocked_item, stype):
                    print("Blocking Type: ", stype, file=sys.stderr)
                    if with_ref_items:
                        return {**schema, "type": "null"}, []
                    else:
                        return {**schema, "type": "null"}, []

            if schema.get("type") == "string":
                # We need to treat string differently than other base types to filter certain format types
                if schema.get("format") in blocked_str_formats:
                    # Return similar to the default, but remove the format property, since Outlines does not support some (e.g. 'binary')
                    string_format = schema.get("format")
                    # Remove unsupported format
                    print("Removing string format: ", string_format, file=sys.stderr)
                    schema.pop("format")

                if schema.get("pattern"):
                    pattern = schema.get("pattern")
                    if pattern.startswith("^") and pattern.endswith("$"):
                        # The pattern is supported
                        # But it appears that some patterns - even if they start with ^ and end with $, are not supported by the Llama.cpp conversion script.
                        # e.g. "^[^\\s]+(\\s[^\\s]+)*$"
                        schema.pop("pattern")
                    else:
                        # The Llama.cpp conversion script does not support certain pattern, so we need to remove it.
                        replaced_schema = schema.copy()
                        replaced_schema.pop("pattern")

                        # TODO: What happens if we just add the '^' and '$' to the pattern?
                        # print("Unsupported pattern: ", pattern, file=sys.stderr)
                        #if not pattern.startswith("^"): pattern = "^" + pattern
                        #if not pattern.endswith("$"): pattern = pattern + "$"
                        #replaced_schema["pattern"] = pattern
                        schema = replaced_schema

            elif schema.get("type") not in ["object", "array", "number", "integer", "boolean", "null"]:
                # We assume to have a special FHIR class here only refered to by its string class name
                # -> We expand the class here into a full JSON schema
                schema_type = schema.get("type")
                fhir_schemas = loadFHIRSchemas()
                assert schema_type in fhir_schemas, f"Schema type {schema_type} not found in FHIR schemas."

                if stop_at_new_base_resource and get_fhir_model_class(schema_type).has_resource_base():
                    # We stop here and do not expand further -> set to null
                    print("Stopping at new base resource: ", schema_type, file=sys.stderr)
                    schema = {
                        "type": "null"
                    }
                else:
                    ref_items.append(schema_type)
                    replaced_schema = schema.copy()
                    replaced_schema.pop("type")
                    replaced_schema["$ref"] = ref_prefix + schema_type
                    schema = replaced_schema

        if in_properties:
            # Remove blocked properties
            cleaned_schema = {}
            for k, v in schema.items():
                should_block = False
                for bp in blocked_properties:
                    if k == bp or re.match(bp, k):
                        should_block = True
                        break

                if should_block:
                    print("Blocking property: ", k, file=sys.stderr)
                else:
                    cleaned_schema[k] = v

            schema = cleaned_schema

            # Rename the properties
            schema = { replace_property_names.get(k, k): v for k,v in schema.items() }

        # Just proceed along the items recursively
        sub_schema = {
            k: __schema_expand(
                v,
                replace_property_names,
                blocked_properties,
                blocked_types,
                blocked_str_formats,
                in_properties=(k == "properties"),
                ref_prefix=ref_prefix,
                with_ref_items=with_ref_items,
                stop_at_new_base_resource=stop_at_new_base_resource
            )
            for k,v in schema.items()
        }
        if with_ref_items:
            return (
                { k: v[0] for k,v in sub_schema.items() },
                ref_items + list(reduce(lambda x,y: x+y, [ v[1] for k, v in sub_schema.items() ]))
            )
        else:
            return sub_schema
    else:
        # Remaining, unknown base type
        raise NotImplementedError("Unexpected base type: ", type(schema))