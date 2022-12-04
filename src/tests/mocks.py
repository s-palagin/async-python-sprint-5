BASE_URL = 'http://localhost'


class CustomTestUser():
    def __init__(self) -> None:
        self.name: str = 'Test user'
        self.password: str = 'P@ssw0rd'
        self.token: str = ""

    def set_token(self, token: str) -> None:
        self.token = token
