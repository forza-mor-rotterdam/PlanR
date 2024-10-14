import re


def pascal_to_camel(name):
    return name[0].lower() + name[1:]


def camel_to_pascal(name):
    return name[0].upper() + name[1:]


def snake_to_pascal(name):
    return "".join(name.title().split("_"))


def snake_to_camel(name):
    return pascal_to_camel(camel_to_pascal(name))


CAMEL_PATTERN = r"(?<!^)(?=[A-Z])"


def camel_to_snake(name):
    return re.sub(CAMEL_PATTERN, "_", name).lower()


ADVANCED_CAMEL_PATTERN = re.compile(r"(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])")


def advanced_camel_to_snake(name):
    return re.sub(ADVANCED_CAMEL_PATTERN, r"_\g<0>", name).lower()
