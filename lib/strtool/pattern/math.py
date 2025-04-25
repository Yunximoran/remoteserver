
INT = r"^(0)$|^([+-]?[1-9]\d*)$"
FLOAT = r"^[+-]?(?:\d+\.\d+|\.\d+|\d+\.(?:\d+)?|\d+[eE][+-]?\d+)$"


if __name__ == "__main__":
    import re
    print(re.match(INT, "8802"))