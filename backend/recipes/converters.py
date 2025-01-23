
class HexConverter:
    regex = '[0-9a-fA-F]+'

    def to_python(self, value):
        return int(value, 16)

    def to_url(self, value):
        if isinstance(value, str):
            value = int(value)
        return hex(value)[2:]
