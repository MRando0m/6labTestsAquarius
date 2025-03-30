from locust import HttpUser, task, between
from requests.exceptions import ConnectionError, Timeout


class JsonPlaceholder (HttpUser):
    host = "https://jsonplaceholder.typicode.com"
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
    def get_posts(self):
        response = self.make_request("GET", "/posts", "Get Posts")

        if response.status_code != 200:
            response.failure(f"Ожидался статус 200, получен {response.status_code}")
            return
        
        posts = response.json()
        if len(posts) == 0:
            response.failure("Пустой список posts")
            return
        
        first_post = posts[0]
        required_fields = ["userId", "id", "title", "body"]
        for field in required_fields:
            if field not in first_post:
                response.failure(f"Пропущено поле: {field}")
                return          