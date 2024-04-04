import os
import re
import json
from jsonschema import Draft7Validator
from collections import defaultdict
from operation_schema import operation_schema


variables_ptrn = r'([^\)]*)'
operation_type_ptrn = r'(query|mutation)'
operation_name_ptrn = r'(.*)'
query_ptrn = re.compile(f'({operation_type_ptrn} {operation_name_ptrn}\\s?\\({variables_ptrn}\\)[^`]*)')

operation_validator = Draft7Validator(operation_schema)



def to_json_type(variable_type:str):
    variable_type = variable_type.lower()
    expected_variable_types = {
        'ID', 
        'JSON', 
        '[ID]', 
        '[String]', 
        'Boolean', 
        'ReadingListOption', 
        'Int', 
        'String'
    }
    expected_variable_types = set(map(lambda x: x.lower(), expected_variable_types))

    if variable_type not in expected_variable_types:
        raise Exception(f'Unexpected Variable Type: {variable_type}')



    if variable_type[0] == '[':
        return {'type': 'arr', 'items': to_json_type(variable_type[1:-1])}
    
    if variable_type in ('id', 'string'):
        return {'type': 'string'}

    if variable_type in ('int',):
        return {'type': 'integer'}

    if variable_type in ('boolean',):
        return {'type':'boolean'}

    return {'type':'object'}

def get_file_names(dir_name, extension=''):
    return (name for name in os.listdir(dir_name) if name.endswith(extension))


def content_from(path):
    with open(path, 'r', encoding='utf-8') as f:
        return ''.join(f.readlines())


def get_only_exists(dictionary):
    return {k:v for k, v in dictionary.items() if v}
    

def dict_to_json(dictionary, path):
    dirname = os.path.dirname(path)

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f)


def operation_from_matches(match):
    query, operation_type, operation_name, variables = match

    variables = variables.replace('\n', ' ').strip().lstrip('$').split('$')
    variables_schema = {'type': 'object', 'properties': {}, 'required': []}

    for var in variables:
        variable_name, variable_type = map(lambda x: x.strip().strip(','), var.split(':'))

        if variable_type[-1] == '!':
            variable_type = to_json_type(variable_type[:-1])
            variables_schema['required'].append(variable_name)
        else:
            variable_type = to_json_type(variable_type)

        variables_schema['properties'][variable_name] = variable_type

    operation = get_only_exists({
        'operationName': operation_name,
        'operationType': operation_type,
        'query': query,
        'variablesSchema': get_only_exists(variables_schema),
    })

    operation_validator.validate(operation)
    
    return operation


def gql_type_from_ts_file(path):
    content = content_from(path)
    matches = query_ptrn.findall(content)
    operations = map(operation_from_matches, matches)

    gql_type = defaultdict(dict)    
    for operation in operations:
        operation_name = operation['operationName']
        operation_type = operation['operationType']
        gql_type[operation_type][operation_name] = operation

    return get_only_exists(gql_type)

def gql_dictionary_to_json(gql:dict, dir_name='schemas'):
    gql_types = {}

    for type_name, gql_type in gql.items():
        gql_types[type_name] = defaultdict(list)
        for operation_type, operations in gql_type.items():
            for operation_name, operation in operations.items():
                gql_types[type_name][operation_type].append(operation_name)
                dict_to_json(operation, path=f'{dir_name}/{type_name}/{operation_name}.json')
    
    dict_to_json(gql_types, f'{dir_name}/types.json')

def main():
    dir_name = 'velog-client/src/lib/graphql'
    gql = {}
    for file_name in get_file_names(dir_name, 'ts'):
        type_name= file_name[:-3]
        gql[type_name] = gql_type_from_ts_file(path=f'{dir_name}/{file_name}')
    
    gql_dictionary_to_json(gql)


if __name__ == '__main__':
    main()