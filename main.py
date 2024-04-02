import os
import re
import json
from jsonschema import Draft7Validator
from collections import defaultdict
from functools import partial
import gql_schema


type_name_pattern = r'(query|mutation) (.*)'
variables_pattern = r'([^\)]*)'
gql_pattern = re.compile(f'({type_name_pattern}\\s?\\({variables_pattern}\\)[^`]*)')


gql_operation_validator = Draft7Validator(gql_schema.gql_schema['operationSchema'])
gql_type_validator = Draft7Validator(gql_schema.gql_schema['gqlTypeSchema'])


def get_file_names(dir_name, extension=''):
    return (
        dir_content
        for dir_content
        in os.listdir(dir_name) 
        if dir_content.endswith(extension)
    )

def get_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return ''.join(f.readlines())

def get_only_exists(dictionary):
    return {k:v for k, v in dictionary.items() if v}
    

def gen_json_file(path, json_object):
    get_only_exists(json_object)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(json_object, f)

def gen_gql_operation(info, dir_name=None):
    gql, operation_type, name, variables = info

    variables = variables.replace('\n', ' ').strip().lstrip('$').split('$')
    variables_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for var in variables:
        _name, _type = map(lambda x: x.strip(), var.split(':'))

        if _type[-1] == '!':
            _type = _type[:-1]
            variables_schema['required'].append(_name)

        variables_schema['properties'][_name] = {'type':_type}


    gql_operation = get_only_exists({
        'operationName': name,
        'query': gql,
        'operationType': operation_type,
        'variablesSchema': get_only_exists(variables_schema),
    })

    gql_operation_validator.validate(gql_operation)

    if dir_name is not None:
        gen_json_file(f'{dir_name}/{name}.json', gql_operation)

    return gql_operation

def gen_gql_type(content, dir_name=None):
    gql_type = defaultdict(list)

    matches = gql_pattern.findall(content)

    if matches and not os.path.exists(gql_type_path):
        os.makedirs(gql_type_path)

    gen_operation = partial(gen_gql_operation, dir_name = dir_name)
    gql_operations = map(gen_operation, matches)
    
    for gql_operation in gql_operations:
        operation_type = gql_operation['operationType']
        gql_type[operation_type].append(gql_operation)

    gql_type = get_only_exists(gql_type)

    # gql_type_validator.validate(gql_type)

    return gql_type


dir_name = 'velog-client/src/lib/graphql'
for file_name in get_file_names(dir_name, 'ts'):
    file_path = '/'.join((dir_name, file_name))
    content = get_file_content(file_path)
    gql_type_path = f'{gql_schema.dir_name}/{file_name[:-3]}'
    gql_type = gen_gql_type(content, dir_name=gql_type_path)
