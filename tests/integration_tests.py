import unittest
import requests

BASE_URL = "http://localhost:8080/api"

class TestIntegrationAPI(unittest.TestCase):
    def setUp(self):
        # Регистрация и получение токена
        self.user1 = {"username": "alice", "password": "password"}
        self.user2 = {"username": "bob", "password": "password"}

        self.token1 = self.authenticate(self.user1)
        self.token2 = self.authenticate(self.user2)

    def authenticate(self, user):
        response = requests.post(f"{BASE_URL}/auth", json=user)
        self.assertEqual(response.status_code, 200)
        return response.json()["token"]

    def test_send_coins_success(self):
        headers = {"Authorization": f"Bearer {self.token1}"}
        data = {"toUser": "bob", "amount": 100}
        response = requests.post(f"{BASE_URL}/sendCoin", json=data, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_send_coins_insufficient_balance(self):
        headers = {"Authorization": f"Bearer {self.token2}"}
        data = {"toUser": "alice", "amount": 10000}
        response = requests.post(f"{BASE_URL}/sendCoin", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_send_coins_to_self(self):
        headers = {"Authorization": f"Bearer {self.token1}"}
        data = {"toUser": "alice", "amount": 50}
        response = requests.post(f"{BASE_URL}/sendCoin", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_buy_item_success(self):
        headers = {"Authorization": f"Bearer {self.token1}"}
        response = requests.get(f"{BASE_URL}/buy/t-shirt", headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_buy_item_insufficient_balance(self):
        headers = {"Authorization": f"Bearer {self.token2}"}
        response = requests.get(f"{BASE_URL}/buy/pink-hoody", headers=headers)
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
