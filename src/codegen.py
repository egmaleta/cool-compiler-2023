def create_vars(variables: dict, data: str) -> None:
    line = ''
    for name in list(variables.keys()):

        line += name + ' .'

def def_type(var: tuple) -> str:
    var_type = var[0]
    if var_type == 'Str':
        return 'asciiz'
    elif var_type == 'Int' or var_type == 'Bool':
        return 'byte'
    else:
        return None

instances = {}
classes = {}
variables = {}
functions = {}

data = '.data\n'