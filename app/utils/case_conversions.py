import re
from re import sub


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


def to_kebab(s):
    return "-".join(
        sub(
            r"(\s|_|-)+",
            " ",
            sub(
                r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda mo: " " + mo.group(0).lower(),
                s,
            ),
        ).split()
    )


ADVANCED_CAMEL_PATTERN = re.compile(r"(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])")


def advanced_camel_to_snake(name):
    return re.sub(ADVANCED_CAMEL_PATTERN, r"_\g<0>", name).lower()
