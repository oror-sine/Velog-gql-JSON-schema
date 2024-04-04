import json

dir_name = 'schemas'

operation_schema = {
  "type": "object",
  "properties": {
    "operationName": {"type": "string"},
    "query": {"type": "string"},
    "variablesSchema": {"type": "object"}
  },
  "required": ["operationName", "query", "variablesSchema"]
}


if __name__ == '__main__':
    from pprint import pprint
    import os
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(f'{dir_name}/operationSchema.json', 'w', encoding='utf-8') as f:
        json.dump(operation_schema, f)
    with open(f'{dir_name}/operationSchema.json', 'r', encoding='utf-8') as f:
        pprint(json.load(f))