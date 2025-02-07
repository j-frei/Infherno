import sys
from util import getSchemaForAllowedTypes

if __name__ == "__main__":
    import argparse
    import json
    '''
        root_types: List[str],
        blocked_types: List[str] = None, # Default should be 'Attachment', 'Element', 'BackboneElement'
        blocked_properties: List[str] = None,
        blocked_str_formats: List[str] = None,
        replace_property_names: List[str] = None,
    '''
    argparser = argparse.ArgumentParser(description='Generate FHIR Schema')
    argparser.add_argument('--root-resources', type=str, nargs='+', help='FHIR resources to include in the schema')

    argparser.add_argument('--blocked-types', type=str, nargs='+', default=[
        "Meta",
        ".*Extension.*",
        "Attachment",
        "Annotation",
    ], help='FHIR types to exclude from the schema')

    argparser.add_argument('--blocked-properties', type=str, nargs='+', default=[
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
    ], help='FHIR properties to exclude from the schema')

    argparser.add_argument('--blocked-str-formats', type=str, nargs='+', default=[
            "binary"
    ], help='FHIR string formats to exclude from the schema')

    argparser.add_argument('--replace-property-names', type=str, nargs='+', default=[
        "resource_type->resourceType"
    ], help='FHIR property names to replace in the schema')

    argparser.add_argument('--output', type=str, help='Output file path')
    args = argparser.parse_args()

    blocked_types = args.blocked_types
    blocked_properties = args.blocked_properties
    blocked_str_formats = args.blocked_str_formats
    replace_property_names = { rpn.split("->")[0].strip(): rpn.split("->")[1].strip() for rpn in args.replace_property_names if "->" in rpn }

    print("Generating schema for resources:", ", ".join(args.root_resources), file=sys.stderr)
    print("Blocked types:", ", ".join(blocked_types), file=sys.stderr)
    print("Blocked properties:", ", ".join(blocked_properties), file=sys.stderr)
    print("Blocked string formats:", ", ".join(blocked_str_formats), file=sys.stderr)
    print("Replace property names:", ", ".join([ f"{k} -> {v}" for k, v in replace_property_names.items() ]), file=sys.stderr)

    schema = getSchemaForAllowedTypes(#
        args.root_resources,
        blocked_types=blocked_types,
        blocked_properties=blocked_properties,
        blocked_str_formats=blocked_str_formats,
        replace_property_names=replace_property_names,
        stop_at_new_base_resource=True
    )
    with open(args.output, 'w') as f:
        f.write(json.dumps(schema, indent=2))


