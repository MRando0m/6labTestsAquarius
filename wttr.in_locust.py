from locust import HttpUser, task, between
from requests.exceptions import ConnectionError, Timeout


class Wttr (HttpUser):
    host = "https://wttr.in"
    wait_time = between(1, 2.5)

    headers = {"Accept": "application/json"}
    request_timeout = 10
    
    def make_request(self, method, path, name):
        try:
            with self.client.request(
                method,
                path,
                headers=self.headers,
                timeout=self.request_timeout,
                name=name,
                catch_response=True
            ) as response:
                return response
        except (ConnectionError, Timeout) as e:
            response.failure(f"{type(e).__name__}: {str(e)}")
        except Exception as e:
            response.failure(f"Нераспознанная ошибка: {str(e)}")

    @task(1)
    def test_weather_api(self):
        response = self.make_request("GET", "/Novosibirsk?format=j1", "Get weather")

        if response.status_code != 200:
            response.failure(f"Ожидался статус 200, получен {response.status_code}")
            return
        
        weather_data = response.json()
        if len(weather_data) == 0:
            response.failure("Пустой список погоды")
            return
        
        keys = [
            "current_condition", 
            "nearest_area",
            "weather"
        ]
        for key in keys:
            if key not in weather_data:
                response.failure(f"Пропущен раздел: {key}")
                return         