import datetime
from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# データベースのテーブルを作成
class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    val = db.Column(db.Integer, nullable=False)

def __repr__(self):
    return '<Data %r>' % self.val

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 'Hello!'

# GETメソッドでデータを取得
@app.route('/api', methods=['GET'])
def get_tweet():
    val = Data.query.all()
    return {
        "data": [
            {
                "id": v.id,
                "timestamp": v.timestamp,
                "val": v.val
            }
            for v in val
        ]
    }

# POSTメソッドでデータを追加
@app.route('/api', methods=['POST'])
def post_tweet():
    data = request.json["val"] #POSTメソッド のデータを取得
    cre = Data(val = data)
    db.session.add(cre)
    db.session.commit()
    return 'post ok\n '

if __name__ == '__main__':
    app.run()