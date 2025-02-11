import unittest
from app.models import User, Transaction, Inventory
from app.services import send_coins, buy_item
from app.database import db_session
from sqlalchemy.exc import IntegrityError

class TestCoinTransactions(unittest.TestCase):
    def setUp(self):
        self.user1 = User(username='alice', coins=1000)
        self.user2 = User(username='bob', coins=500)
        db_session.add_all([self.user1, self.user2])
        db_session.commit()

    def tearDown(self):
        db_session.query(Transaction).delete()
        db_session.query(Inventory).delete()
        db_session.query(User).delete()
        db_session.commit()

    def test_send_coins_success(self):
        send_coins('alice', 'bob', 200)
        self.assertEqual(self.user1.coins, 800)
        self.assertEqual(self.user2.coins, 700)

    def test_send_coins_insufficient_balance(self):
        with self.assertRaises(ValueError):
            send_coins('bob', 'alice', 600)

    def test_send_coins_to_self(self):
        with self.assertRaises(ValueError):
            send_coins('alice', 'alice', 100)

    def test_buy_item_success(self):
        buy_item('alice', 't-shirt')
        self.assertEqual(self.user1.coins, 920)
        inventory = db_session.query(Inventory).filter_by(user_id=self.user1.id, item_name='t-shirt').first()
        self.assertIsNotNone(inventory)
        self.assertEqual(inventory.quantity, 1)

    def test_buy_item_insufficient_balance(self):
        with self.assertRaises(ValueError):
            buy_item('bob', 'pink-hoody')

    def test_buy_nonexistent_item(self):
        with self.assertRaises(KeyError):
            buy_item('alice', 'spaceship')

    def test_database_error_handling(self):
        db_session.rollback()
        with self.assertRaises(IntegrityError):
            send_coins('alice', 'nonexistent', 100)

if __name__ == '__main__':
    unittest.main()
