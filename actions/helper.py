import re
import requests
from requests.structures import CaseInsensitiveDict


class ArgumentParser:
    @classmethod
    def parse_args(cls, text: str):
        """ takes the text from a slack command and parses the arguments """
        arg_pattern = re.compile(r'--(\w+) *["@]?([^-"]*)\"?')
        return dict(arg_pattern.findall(text))


class OAuthAuthenticator:
    def __init__(self, token):
        self.user_token = token

    def memoize(func):
        cache = dict()

        def memoized_func(*args):
            if args in cache:
                return cache[args]
            result = func(*args)
            cache[args] = result
            return result

        return memoized_func

    # @memoize
    def authenticate(self, userid):
        data = {"access_token": self.user_token}
        response = requests.post(
            url="http://127.0.0.1:8000/dj-rest-auth/slack/",
            data=data,
        )
        if response.status_code != 200:
            return None
        token = response.json().get("key", None)
        if token is None:
            return None
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {token}"
        return headers


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