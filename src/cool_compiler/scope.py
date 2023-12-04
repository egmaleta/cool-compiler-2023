from typing import Optional


class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self._vars = {}
        self._functions = {}

        self._parent = parent

    def get_var(self, name: str):
        if name in self._vars:
            return self._vars[name]

        if self._parent != None:
            return self._parent.get_var(name)

        raise Exception('')

    def set_var(self, name: str, value):
        if name in self._vars:
            self._vars[name] = value

        elif self._parent != None:
            self._parent.set_var(name, value)

        raise Exception('')

    def get_function(self, name: str):
        if name in self._functions:
            return self._functions[name]

        if self._parent != None:
            return self._parent.get_function(name)

        raise Exception('')

    def set_function(self, name: str, f):
        if name in self._functions:
            self._functions[name] = f

        raise Exception('')

    def child(self):
        return Scope(self)
