from datetime import datetime
from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# データベースのテーブルを作成
class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    val = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Data %r>' % self.val

class NoticeData(db.Model):
    __tablename__ = 'notice_data'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    notice = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<NoticeData %r>' % self.notice

class FlagData(db.Model):
    __tablename__ = 'flag_data'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    flag = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<FlagData %r>' % self.flag


with app.app_context():
    db.create_all()

# このAPIは以下のようなエンドポイントを持つ
# それぞれのエンドポイントに対してGETとPOSTメソッドを用意する
#  api/
#   val
#   notice
#   flag
# apiの説明
@app.route('/')
def index():
    return (
        "api/val: GETでデータを取得, POSTでデータを追加\n"
        "api/notice: GETでデータを取得, POSTでデータを追加\n"
        "api/flag: GETでデータを取得, POSTでデータを追加\n"
    )


# GETメソッドでデータを取得
@app.route('/api/val', methods=['GET'])
def get_val():
    val = Data.query.all()
    return {
        "num_results": f"{len(val)}",
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
    timestamp = datetime.now(pytz.timezone("Asia/Tokyo"))
    cre = Data(val = data, timestamp = timestamp)
    db.session.add(cre)
    db.session.commit()
    return 'post val ok\n '

# GETメソッドでデータを取得
@app.route('/api/notice', methods=['GET'])
def get_notice():
    notice = NoticeData.query.all()
    return {
        "num_results": f"{len(notice)}",
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
    timestamp = datetime.now(pytz.timezone("Asia/Tokyo"))
    cre = NoticeData(notice = data, timestamp = timestamp)
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
    timestamp = datetime.now(pytz.timezone("Asia/Tokyo"))
    cre = FlagData(flag = data, timestamp = timestamp)
    db.session.add(cre)
    db.session.commit()
    return 'post flag ok\n '

if __name__ == '__main__':
    app.run()