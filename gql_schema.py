import json

dir_name = 'schemas'

gql_schema = {
    "operationSchema": {
      "type": "object",
      "properties": {
          "operationName": {"type": "string"},
          "query": {"type": "string"},
          "operationType": { 
            "type": "string", 
            "enum": ["query", "mutation"]
          },
          "variablesSchema": {"type": "object"}
      },
      "required": ["operationName", "query", "operationType", "variablesSchema"]
    },

    "gqlTypeSchema": {
      "type": "object",
      "properties": {
          "query": {
            "type": "array", 
            "items": {"$ref": "#/operationSchema"}
          },
          "mutation": {
            "type": "array", 
            "items": {"$ref": "#/operationSchema"}
          }
      }
    }
}


if __name__ == '__main__':
    from pprint import pprint
    import os
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(f'{dir_name}/gql_schema.json', 'w', encoding='utf-8') as f:
        json.dump(gql_schema, f)
    with open(f'{dir_name}/gql_schema.json', 'r', encoding='utf-8') as f:
        pprint(json.load(f))