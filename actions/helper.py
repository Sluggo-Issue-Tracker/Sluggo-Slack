import re


class ArgumentParser:
    @classmethod
    def parse_args(cls, text: str):
        """ takes the text from a slack command and parses the arguments """
        arg_pattern = re.compile(r"--(\w+)([^-]*)")
        return {k: v for k, v in arg_pattern.findall(text)}
