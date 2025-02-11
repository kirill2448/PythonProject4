from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/shop'
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    coins = db.Column(db.Integer, default=1000)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    to_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, default=1)

merch_prices = {
    "t-shirt": 80, "cup": 20, "book": 50, "pen": 10, "powerbank": 200,
    "hoody": 300, "umbrella": 200, "socks": 10, "wallet": 50, "pink-hoody": 500
}
with app.app_context():
    db.create_all()

@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    token = create_access_token(identity=username)
    return jsonify(token=token)

@app.route('/api/info', methods=['GET'])
@jwt_required()
def get_info():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(errors="User not found"), 404
    transactions = Transaction.query.filter((Transaction.from_user == user.id) | (Transaction.to_user == user.id)).all()
    inventory = Inventory.query.filter_by(user_id=user.id).all()
    return jsonify({
        "coins": user.coins,
        "inventory": [{"type": item.item, "quantity": item.quantity} for item in inventory],
        "coinHistory": {
            "received": [{"fromUser": tx.from_user, "amount": tx.amount} for tx in transactions if tx.to_user == user.id],
            "sent": [{"toUser": tx.to_user, "amount": tx.amount} for tx in transactions if tx.from_user == user.id]
        }
    })

@app.route('/api/sendCoin', methods=['POST'])
@jwt_required()
def send_coin():
    data = request.get_json()
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    recipient = User.query.filter_by(username=data['toUser']).first()
    amount = data['amount']
    if not recipient or user.coins < amount or amount <= 0:
        return jsonify(errors="Invalid transaction"), 400
    user.coins -= amount
    recipient.coins += amount
    transaction = Transaction(from_user=user.id, to_user=recipient.id, amount=amount)
    db.session.add(transaction)
    db.session.commit()
    return jsonify(success=True)

@app.route('/api/buy/<string:item>', methods=['GET'])
@jwt_required()
def buy_item(item):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if item not in merch_prices or user.coins < merch_prices[item]:
        return jsonify(errors="Invalid purchase"), 400
    user.coins -= merch_prices[item]
    inventory = Inventory.query.filter_by(user_id=user.id, item=item).first()
    if inventory:
        inventory.quantity += 1
    else:
        db.session.add(Inventory(user_id=user.id, item=item))
    db.session.commit()
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)