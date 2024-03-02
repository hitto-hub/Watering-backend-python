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

# valを使ってグラフを表示する
@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>Watering</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1>Watering</h1>
            <div id="graph"></div>
            <script>
                fetch('/api/val')
                .then(response => response.json())
                .then(data => {
                    const x = data.data.slice(-300).map(v => new Date(v.timestamp));
                    const y = data.data.slice(-300).map(v => v.val);
                    const trace = {
                        x: x,
                        y: y,
                        type: 'scatter'
                    };
                    fetch('/api/notice')
                    .then(response => response.json())
                    .then(noticeData => {
                        const notice = noticeData.data.filter(v => v.notice === 1);
                        const noticeX = notice.map(v => new Date(v.timestamp));
                        const noticeY = notice.map(v => 0);
                        const noticeTrace = {
                            x: noticeX,
                            y: noticeY,
                            mode: 'markers',
                            type: 'scatter',
                            name: 'Notice'
                        };
                        const layout = {
                            title: 'Graph',
                            xaxis: {
                                title: 'Time',
                                automargin: true
                            },
                            yaxis: {
                                title: 'Value'
                            }
                        };
                        Plotly.newPlot('graph', [trace, noticeTrace], layout);
                    });
                });
            </script>
        </body>
    </html>
    '''


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
# /flag?id=1
# でid=1のデータを取得
# idがない場合は全てのデータを取得
@app.route('/api/flag', methods=['GET'])
def get_flag():
    id = request.args.get('id')
    if id is None:
        flag = FlagData.query.all()
        return {
            "num_results": f"{len(flag)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "flag": v.flag
                }
                for v in flag
            ]
        }
    else:
        flag = FlagData.query.filter_by(id=id).all()
        return {
            "num_results": f"{len(flag)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "flag": v.flag
                }
                for v in flag
            ]
        }

# GETメソッドで最新のデータを取得
@app.route('/api/flag/last', methods=['GET'])
def get_flag_last():
    flag = FlagData.query.all()
    if flag:
        # 1 or 0で返す
        return f"{flag[-1].flag}"
    else:
        return "No data available"

# GETメソッドでデータの個数を取得
@app.route('/api/flag/count', methods=['GET'])
def get_flag_count():
    flag = FlagData.query.all()
    return f"{len(flag)}"

# POSTメソッドでデータを追加
@app.route('/api/flag', methods=['POST'])
def post_flag():
    data = request.json["flag"] #POSTメソッド のデータを取得
    timestamp = datetime.now(pytz.timezone("Asia/Tokyo"))
    cre = FlagData(flag = data, timestamp = timestamp)
    db.session.add(cre)
    db.session.commit()
    return {
        "status": "success",
    }

if __name__ == '__main__':
    app.run()
