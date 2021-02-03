import re


class ArgumentParser:
    @classmethod
    def parse_args(cls, text: str) -> dict:
        """ takes the text from a slack command and parses the arguments """
        arg_pattern = re.compile(r'--(\w+) *["@]?([^-"]*)\"?')
        return dict(arg_pattern.findall(text))
