from app.database import db
from app.models import User, Transaction, Inventory

def send_coins(sender_username, receiver_username, amount):
    sender = User.query.filter_by(username=sender_username).first()
    receiver = User.query.filter_by(username=receiver_username).first()

    if not sender or not receiver:
        raise ValueError("User not found")

    if sender.coins < amount:
        raise ValueError("Insufficient funds")

    sender.coins -= amount
    receiver.coins += amount

    transaction = Transaction(sender_id=sender.id, receiver_id=receiver.id, amount=amount)
    db.session.add(transaction)
    db.session.commit()

def buy_item(username, item_name):
    user = User.query.filter_by(username=username).first()

    item_price = 80  # Фиксированная цена товара

    if user.coins < item_price:
        raise ValueError("Insufficient funds")

    user.coins -= item_price
    inventory_item = Inventory.query.filter_by(user_id=user.id, item_name=item_name).first()

    if inventory_item:
        inventory_item.quantity += 1
    else:
        inventory_item = Inventory(user_id=user.id, item_name=item_name)
        db.session.add(inventory_item)

    db.session.commit()
