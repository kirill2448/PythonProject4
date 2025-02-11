import unittest
from app import create_app, db
from app.models import User
from app.services import send_coins

class TestTransactions(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.user1 = User(username="alice", coins=1000)
        self.user2 = User(username="bob", coins=500)
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_send_coins(self):
        send_coins("alice", "bob", 200)
        self.assertEqual(self.user1.coins, 800)
        self.assertEqual(self.user2.coins, 700)

if __name__ == "__main__":
    unittest.main()
