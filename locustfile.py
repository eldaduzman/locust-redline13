from itertools import count
from locust import HttpUser, between, task

USER_NUMBERS = count(1)


class WebsiteUser(HttpUser):
    wait_time = between(10, 12)
    host = "https://postman-echo.com"

    def __init__(self, *args, **kwargs):
        self._user_number = next(USER_NUMBERS)
        super().__init__(*args, **kwargs)

    @task
    def index(self):
        response = self.client.get(f"/get?var={self._user_number}", name="get_usr_num")
        var = response.json()['args']['var']
        response = self.client.get(f"/get?var={var}", name="get_var")