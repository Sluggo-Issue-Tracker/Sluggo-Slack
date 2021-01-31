import requests, json
from . import models, exceptions, config


class AuthRequests:
    auth_root = "/dj-rest-auth"
    oauth = "/slack/"

    # keys
    kACCESS_TOKEN = "access_token"
    kKEY = "key"

    @classmethod
    def authenticate_oauth(cls, oauth_token: str) -> str:
        url = config.API_ROOT + cls.auth_root + cls.oauth
        response = requests.post(url, data={
            cls.kACCESS_TOKEN: oauth_token
        })

        if not (key := response.json().get(cls.kKEY)):
            raise exceptions.InvalidOAuthToken(
                f"Invalid response {json.dumps(response.json(), indent=4)}"
            )
        return key


class AuthorizedRequest:
    cache = {}

    kACCEPT = "accept"
    kAUTHORIZATION = "authorization"

    def _fetch_user_key_(self, user_id: str) -> str:
        if (token := self.cache.get(user_id)) is None:
            try:
                oauth_token = models.authed_user.objects.get(pk=user_id).access_token
                token = AuthRequests.authenticate_oauth(oauth_token)
                self.cache[user_id] = token

            except models.authed_user.DoesNotExist:
                raise exceptions.MissingOAuthToken("User needs to authenticate through slack")

        return token

    def __init__(self, user_id: str):
        self.key = self._fetch_user_key_(user_id)

    def __getattr__(self, attr):
        if not hasattr(requests, attr):
            raise AttributeError("requests has no such method")

        def wrapper(*args, **kwargs):
            headers = requests.models.CaseInsensitiveDict()
            headers[self.kACCEPT] = "application/json"
            headers[self.kAUTHORIZATION] = f"Bearer {self.key}"
            kwargs.update(headers=headers)
            return getattr(requests, attr)(*args, **kwargs)

        return wrapper
