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

class NoticeData(db.Model):
    __tablename__ = 'notice_data'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    notice = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<NoticeData %r>' % self.notice

class FlagData(db.Model):
    __tablename__ = 'flag_data'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    flag = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<FlagData %r>' % self.flag


with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 'Hello!'

# GETメソッドでデータを取得
@app.route('/api/val', methods=['GET'])
def get_val():
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
@app.route('/api/val', methods=['POST'])
def post_val():
    data = request.json["val"] #POSTメソッド のデータを取得
    cre = Data(val = data)
    db.session.add(cre)
    db.session.commit()
    return 'post val ok\n '

# GETメソッドでデータを取得
@app.route('/api/notice', methods=['GET'])
def get_notice():
    notice = NoticeData.query.all()
    return {
        "data": [
            {
                "id": v.id,
                "timestamp": v.timestamp,
                "notice": v.notice
            }
            for v in notice
        ]
    }

# POSTメソッドでデータを追加
@app.route('/api/notice', methods=['POST'])
def post_notice():
    data = request.json["notice"] #POSTメソッド のデータを取得
    cre = NoticeData(notice = data)
    db.session.add(cre)
    db.session.commit()
    return 'post notice ok\n '


# GETメソッドでデータを取得
# 変更するかも
@app.route('/api/flag', methods=['GET'])
def get_flag():
    flag = FlagData.query.all()
    return {
        "data": [
            {
                "id": v.id,
                "timestamp": v.timestamp,
                "flag": v.flag
            }
            for v in flag
        ]
    }

# POSTメソッドでデータを追加
@app.route('/api/flag', methods=['POST'])
def post_flag():
    data = request.json["flag"] #POSTメソッド のデータを取得
    cre = FlagData(flag = data)
    db.session.add(cre)
    db.session.commit()
    return 'post flag ok\n '

if __name__ == '__main__':
    app.run()