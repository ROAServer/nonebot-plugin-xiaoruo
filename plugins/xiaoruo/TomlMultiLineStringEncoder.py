import toml

class TomlMultiLineStringEncoder(toml.TomlEncoder):

    def __init__(self, _dict=dict, preserve=False):
        super().__init__(_dict, preserve)

    def dump_value(self, v):
        if isinstance(v, str) and "\n" in v:
            return f'"""{v}"""'
        return super().dump_value(v)