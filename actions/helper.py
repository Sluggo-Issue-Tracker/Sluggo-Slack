import re
import requests
from requests.structures import CaseInsensitiveDict


class ArgumentParser:
    @classmethod
    def parse_args(cls, text: str) -> dict:
        """ takes the text from a slack command and parses the arguments """
        arg_pattern = re.compile(r'--(\w+) *["@]?([^-"]*)\"?')
        return dict(arg_pattern.findall(text))


def translateError(error_dict):

    error_string = """"""
    for key, value in error_dict.items():
        if isinstance(value, dict):
            error_string += f"\t{key}: {translateError(value)}\n"
        elif isinstance(value, list):
            error_string += f"\t{key}: {' '.join(value)}\n"
        else:
            error_string += f"\t{key}: {error_dict[key]}\n"
    return error_string