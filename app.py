from datetime import datetime
from flask import Flask, g, request, render_template
from flask_sqlalchemy import SQLAlchemy
from zoneinfo import ZoneInfo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# データベースのテーブルを作成
class wetness_value(db.Model):
    __tablename__ = 'wetness_value'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    address = db.Column(db.Integer, nullable=False)

class temperature_value(db.Model):
    __tablename__ = 'temperature_value'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    address = db.Column(db.Integer, nullable=False)

class humidity_value(db.Model):
    __tablename__ = 'humidity_value'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    address = db.Column(db.Integer, nullable=False)

class addresses(db.Model):
    __tablename__ = 'addresses'
    address = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String, nullable=False)

class water_supply(db.Model):
    __tablename__ = 'water_supply'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    address = db.Column(db.Integer, nullable=False)

class watering_regular(db.Model):
    __tablename__ = 'watering_regular'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    time_hour = db.Column(db.Integer, nullable=False)
    time_minutes = db.Column(db.Integer, nullable=False)
    weekday = db.Column(db.String, nullable=False)
    address = db.Column(db.Integer, nullable=False)

class instructions(db.Model):
    __tablename__ = 'instructions'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    address = db.Column(db.Integer, nullable=False)
    instruction = db.Column(db.Integer, nullable=False)

# テーブルを作成
with app.app_context():
    db.create_all()

weekdays_set = ["mon", "tue", "wed", "thu", "fri", "sat", "sun", "all"]
# グラフを表示する
@app.route('/')
def index():
    return render_template('index.html')

# timestampを取得 YYYY/MM/DD HH:MM:SS
def get_timestamp():
    timestamp = datetime.now(ZoneInfo("Asia/Tokyo"))
    return timestamp.strftime('%Y/%m/%d %H:%M:%S')

def address_exists(address):
    if addresses.query.filter_by(address=address).first():
        return True
    else:
        return False


# 一番小さい空きアドレスを取得
def get_minimum_free_address():
    addresses_data = get_all_address()
    minimum_free_address = 1
    for data in addresses_data['data']:
        if minimum_free_address == data["address"]:
            minimum_free_address += 1
        else:
            break
    return minimum_free_address

@app.route('/api/', methods=['POST'])
def func():
    return 'hogehoge'

# 全addressの取得
@app.route('/api/addresses', methods=['GET'])
def get_all_address():
    try:
        addresse = addresses.query.all()
        return {
            "status": True,
            "message": "successfully get all address",
            "num_results": f"{len(addresse)}",
            "data": [
                {
                    "address": v.address,
                    "name": v.name
                }
                for v in addresse
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get all address"
        }

# addressの取得
# 使用予定なし
@app.route('/api/addresses/<int:address>', methods=['GET'])
def get_address(address):
    try:
        address = addresses.query.filter_by(address=address).first()
        return {
            "status": True,
            "message": "successfully get address",
            "address": address.address,
            "name": address.name
        }
    except:
        return {
            "status": False,
            "message": "failed get address",
            "address": address
        }

# 新規address配布
@app.route('/api/addresses', methods=['POST'])
def address_distribution():
    name = request.json["name"] #POSTメソッド のnameを取得
    address = get_minimum_free_address()
    try:
        cre = addresses(name = name, address = address)
        db.session.add(cre)
        db.session.commit()
        return {
            "status": True,
            "message": "successfully distributed address",
            "address": address,
            "name": name
        }
    except:
        return {
            "status": False,
            "message": "failed distributed address"
        }

# 特定のaddressのnameを変更
# 使用予定なし discordbotで使うかもしれない
@app.route('/api/addresses/<int:address>', methods=['PUT'])
def change_address_name(address):
    name = request.json["name"] #POSTメソッド のnameを取得
    try:
        # 変更前のnameを取得
        before_name = addresses.query.filter_by(address=address).first().name
        if not address_exists(address): # address存在チェック
            return {
                "status": False,
                "message": "address does not exist",
                "address": address,
                "name": before_name
            }
    except:
        return {
            "status": False,
            "message": "database connection error",
            "address": address,
            "name": before_name
        }
    try:
        addresses.query.filter_by(address=address).update({"name": name}) # addressのnameを変更処理
        db.session.commit()
        return {
            "status": True,
            "message": "successfully changed address name",
            "address": address,
            "name": name
        }
    except:
        return {
            "status": False,
            "message": "failed changed address name",
            "address": address,
            "name": before_name
        }

# addressの削除
# 使用予定なし <- 要検討
# アドレスが足りなくなることがないので、削除する必要ない
# 使う場合は、addressを削除した場合、そのaddressに関連するデータ
# (instructions,wetness_value,temperature_value,humidity_value,water_supply,watering_regular)
# も削除する必要がある
@app.route('/api/addresses/<int:address>', methods=['DELETE'])
def address_delete(address):
    addresses.query.filter_by(address=address).delete()
    db.session.commit()
    instructions.query.filter_by(address=address).delete()
    db.session.commit()
    watering_regular.query.filter_by(address=address).delete()
    db.session.commit()
    temperature_value.query.filter_by(address=address).delete()
    db.session.commit()
    humidity_value.query.filter_by(address=address).delete()
    db.session.commit()
    wetness_value.query.filter_by(address=address).delete()
    db.session.commit()
    water_supply.query.filter_by(address=address).delete()
    db.session.commit()
    return get_all_address()

# 全水やり指示の取得
@app.route('/api/instructions', methods=['GET'])
def get_all_instructions():
    try:
        instruction = instructions.query.all()
        return {
            "status": True,
            "message": "successfully get all instructions",
            "num_results": f"{len(instruction)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "address": v.address,
                    "instruction": v.instruction
                }
                for v in instruction
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get all instructions"
        }

# 特定のaddressの水やり指示の取得
@app.route('/api/instructions/<int:address>', methods=['GET'])
def get_instructions(address):
    try:
        instruction = instructions.query.filter_by(address=address).all()
        return {
            "status": True,
            "message": "successfully get instructions",
            "num_results": f"{len(instruction)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "address": v.address,
                    "instruction": v.instruction
                }
                for v in instruction
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get instructions"
        }

# 特定のaddressの最新の水やり指示の取得
# return 要検討!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.route('/api/instructions/<int:address>/latest', methods=['GET'])
def get_latest_instructions(address):
    try:
        instruction = instructions.query.filter_by(address=address).all()
        if instruction: # データ存在チェック
            return {
                "status": True,
                "message": "successfully get latest instructions",
                "data": {
                    "id": instruction[-1].id,
                    "timestamp": instruction[-1].timestamp,
                    "address": instruction[-1].address,
                    "instruction": instruction[-1].instruction
                }
            }
        else:
            return {
                "status": False,
                "message": "no data available"
            }
    except:
        return {
            "status": False,
            "message": "failed get latest instructions"
        }

# 給水指示
@app.route('/api/instructions/<int:address>', methods=['POST'])
def set_instructions(address):
    instruction = request.json["instruction"] #POSTメソッド のinstructionを取得
    if not address_exists(address): # addressが存在チェック
        return {
            "status": False,
            "message": "address does not exist",
            "address": address
        }
    try:
        cre = instructions(timestamp = get_timestamp(), address = address, instruction = instruction)
        db.session.add(cre)
        db.session.commit()
        return {
            "status": True,
            "message": "successfully water supply instruction",
            "address": address,
            "instruction": instruction
        }
    except:
        return {
            "status": False,
            "message": "failed water supply instruction"
        }

# 全給水履歴の取得
@app.route('/api/supply', methods=['GET'])
def get_all_supply():
    try:
        supply = water_supply.query.all()
        return {
            "status": True,
            "message": "successfully get all supply",
            "num_results": f"{len(supply)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "type": v.type,
                    "address": v.address
                }
                for v in supply
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get all supply"
        }

@app.route('/api/supply/latest', methods=['GET'])
def get_all_latest_supply():
    try:
        supply = water_supply.query.all()
        if supply: # データ存在チェック
            return {
                "status": True,
                "message": "successfully get latest supply",
                "data": {
                    "id": supply[-1].id,
                    "timestamp": supply[-1].timestamp,
                    "type": supply[-1].type,
                    "address": supply[-1].address
                }
            }
        else:
            return {
                "status": False,
                "message": "no data available"
            }
    except:
        return {
            "status": False,
            "message": "failed get latest supply"
        }

# 全給水履歴のカウントを取得
# num_resultsと同じ
# 使わない可能性あり
@app.route('/api/supply/count', methods=['GET'])
def get_all_supply_count():
    supply = water_supply.query.all()
    return {
        "status": True,
        "message": "successfully get all supply count",
        "num_results": f"{len(supply)}"
    }
# 特定のaddressの給水履歴の取得
@app.route('/api/supply/<int:address>', methods=['GET'])
def get_supply(address):
    try:
        supply = water_supply.query.filter_by(address=address).all()
        return {
            "status": True,
            "message": "successfully get supply",
            "num_results": f"{len(supply)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "type": v.type,
                    "address": v.address
                }
                for v in supply
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get supply"
        }

# 特定のaddressの最新の給水履歴の取得
# return 要検討
@app.route('/api/supply/<int:address>/latest', methods=['GET'])
def get_latest_supply(address):
    try:
        supply = water_supply.query.filter_by(address=address).all()
        if supply: # データ存在チェック
            return {
                "status": True,
                "message": "successfully get latest supply",
                "data": {
                    "id": supply[-1].id,
                    "timestamp": supply[-1].timestamp,
                    "type": supply[-1].type,
                    "address": supply[-1].address
                }
            }
        else:
            return {
                "status": False,
                "message": "no data available"
            }
    except:
        return {
            "status": False,
            "message": "failed get latest supply"
        }

# 特定のaddressの給水履歴のカウントを取得
# num_resultsと同じ
# 使わない可能性あり
@app.route('/api/supply/<int:address>/count', methods=['GET'])
def get_supply_count(address):
    supply = water_supply.query.filter_by(address=address).all()
    return {
        "status": True,
        "message": "successfully get supply count",
        "num_results": f"{len(supply)}"
    }

# 全給水履歴の保存
@app.route('/api/supply/<int:address>', methods=['POST'])
def set_supply(address):
    type = request.json["type"]
    if not address_exists(address): # addressが存在チェック
        return {
            "status": False,
            "message": "address does not exist",
            "address": address
        }
    try:
        cre = water_supply(timestamp = get_timestamp(), type = type, address = address)
        db.session.add(cre)
        db.session.commit()
        return {
            "status": True,
            "message": "successfully water supply",
            "address": address,
            "type": type
        }
    except:
        return {
            "status": False,
            "message": "failed water supply"
        }






@app.route('/api/wetness_value', methods=['GET'])
def get_all_wetness_value():
    try:
        wetness = wetness_value.query.all()
        return {
            "status": True,
            "message": "successfully get all wetness value",
            "num_results": f"{len(wetness)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "value": v.value,
                    "address": v.address
                }
                for v in wetness
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get all wetness value"
        }

@app.route('/api/wetness_value/latest', methods=['GET'])
def get_all_latest_wetness_value():
    try:
        wetness = wetness_value.query.all()
        if wetness: # データ存在チェック
            return {
                "status": True,
                "message": "successfully get latest wetness value",
                "data": {
                    "id": wetness[-1].id,
                    "timestamp": wetness[-1].timestamp,
                    "value": wetness[-1].value,
                    "address": wetness[-1].address
                }
            }
        else:
            return {
                "status": False,
                "message": "no data available"
            }
    except:
        return {
            "status": False,
            "message": "failed get latest wetness value"
        }

@app.route('/api/wetness_value/count', methods=['GET'])
def get_all_wetness_value_count():
    wetness = wetness_value.query.all()
    return {
        "status": True,
        "message": "successfully get all wetness value count",
        "num_results": f"{len(wetness)}"
    }

@app.route('/api/wetness_value/<int:address>', methods=['GET'])
def get_wetness_value(address):
    try:
        wetness = wetness_value.query.filter_by(address=address).all()
        return {
            "status": True,
            "message": "successfully get wetness value",
            "num_results": f"{len(wetness)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "value": v.value,
                    "address": v.address
                }
                for v in wetness
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get wetness value"
        }

@app.route('/api/wetness_value/<int:address>/latest', methods=['GET'])
def get_latest_wetness_value(address):
    try:
        wetness = wetness_value.query.filter_by(address=address).all()
        if wetness: # データ存在チェック
            return {
                "status": True,
                "message": "successfully get latest wetness value",
                "data": {
                    "id": wetness[-1].id,
                    "timestamp": wetness[-1].timestamp,
                    "value": wetness[-1].value,
                    "address": wetness[-1].address
                }
            }
        else:
            return {
                "status": False,
                "message": "no data available"
            }
    except:
        return {
            "status": False,
            "message": "failed get latest wetness value"
        }

@app.route('/api/wetness_value/<int:address>/count', methods=['GET'])
def get_wetness_value_count(address):
    wetness = wetness_value.query.filter_by(address=address).all()
    return {
        "status": True,
        "message": "successfully get wetness value count",
        "num_results": f"{len(wetness)}"
    }

@app.route('/api/wetness_value/<int:address>', methods=['POST'])
def set_wetness_value(address):
    value = request.json["value"]
    if not address_exists(address):
        return {
            "status": False,
            "message": "address does not exist",
            "address": address
        }
    try:
        cre = wetness_value(timestamp = get_timestamp(), value = value, address = address)
        db.session.add(cre)
        db.session.commit()
        return {
            "status": True,
            "message": "successfully set wetness value",
            "address": address,
            "value": value
        }
    except:
        return {
            "status": False,
            "message": "failed set wetness value"
        }

@app.route('/api/temperature_value', methods=['GET'])
def get_all_temperature_value():
    try:
        temperature = temperature_value.query.all()
        return {
            "status": True,
            "message": "successfully get all temperature value",
            "num_results": f"{len(temperature)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "value": v.value,
                    "address": v.address
                }
                for v in temperature
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get all temperature value"
        }

@app.route('/api/temperature_value/latest', methods=['GET'])
def get_all_latest_temperature_value():
    try:
        temperature = temperature_value.query.all()
        if temperature: # データ存在チェック
            return {
                "status": True,
                "message": "successfully get latest temperature value",
                "data": {
                    "id": temperature[-1].id,
                    "timestamp": temperature[-1].timestamp,
                    "value": temperature[-1].value,
                    "address": temperature[-1].address
                }
            }
        else:
            return {
                "status": False,
                "message": "no data available"
            }
    except:
        return {
            "status": False,
            "message": "failed get latest temperature value"
        }

@app.route('/api/temperature_value/count', methods=['GET'])
def get_all_temperature_value_count():
    temperature = temperature_value.query.all()
    return {
        "status": True,
        "message": "successfully get all temperature value count",
        "num_results": f"{len(temperature)}"
    }

@app.route('/api/temperature_value/<int:address>', methods=['GET'])
def get_temperature_value(address):
    try:
        temperature = temperature_value.query.filter_by(address=address).all()
        return {
            "status": True,
            "message": "successfully get temperature value",
            "num_results": f"{len(temperature)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "value": v.value,
                    "address": v.address
                }
                for v in temperature
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get temperature value"
        }

@app.route('/api/temperature_value/<int:address>/latest', methods=['GET'])
def get_latest_temperature_value(address):
    try:
        temperature = temperature_value.query.filter_by(address=address).all()
        if temperature: # データ存在チェック
            return {
                "status": True,
                "message": "successfully get latest temperature value",
                "data": {
                    "id": temperature[-1].id,
                    "timestamp": temperature[-1].timestamp,
                    "value": temperature[-1].value,
                    "address": temperature[-1].address
                }
            }
        else:
            return {
                "status": False,
                "message": "no data available"
            }
    except:
        return {
            "status": False,
            "message": "failed get latest temperature value"
        }

@app.route('/api/temperature_value/<int:address>/count', methods=['GET'])
def get_temperature_value_count(address):
    temperature = temperature_value.query.filter_by(address=address).all()
    return {
        "status": True,
        "message": "successfully get temperature value count",
        "num_results": f"{len(temperature)}"
    }

@app.route('/api/temperature_value/<int:address>', methods=['POST'])
def set_temperature_value(address):
    value = request.json["value"]
    if not address_exists(address):
        return {
            "status": False,
            "message": "address does not exist",
            "address": address
        }
    try:
        cre = temperature_value(timestamp = get_timestamp(), value = value, address = address)
        db.session.add(cre)
        db.session.commit()
        return {
            "status": True,
            "message": "successfully set temperature value",
            "address": address,
            "value": value
        }
    except:
        return {
            "status": False,
            "message": "failed set temperature value"
        }

@app.route('/api/humidity_value', methods=['GET'])
def get_all_humidity_value():
    try:
        humidity = humidity_value.query.all()
        return {
            "status": True,
            "message": "successfully get all humidity value",
            "num_results": f"{len(humidity)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "value": v.value,
                    "address": v.address
                }
                for v in humidity
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get all humidity value"
        }

@app.route('/api/humidity_value/latest', methods=['GET'])
def get_all_latest_humidity_value():
    try:
        humidity = humidity_value.query.all()
        if humidity: # データ存在チェック
            return {
                "status": True,
                "message": "successfully get latest humidity value",
                "data": {
                    "id": humidity[-1].id,
                    "timestamp": humidity[-1].timestamp,
                    "value": humidity[-1].value,
                    "address": humidity[-1].address
                }
            }
        else:
            return {
                "status": False,
                "message": "no data available"
            }
    except:
        return {
            "status": False,
            "message": "failed get latest humidity value"
        }

@app.route('/api/humidity_value/count', methods=['GET'])
def get_all_humidity_value_count():
    humidity = humidity_value.query.all()
    return {
        "status": True,
        "message": "successfully get all humidity value count",
        "num_results": f"{len(humidity)}"
    }

@app.route('/api/humidity_value/<int:address>', methods=['GET'])
def get_humidity_value(address):
    try:
        humidity = humidity_value.query.filter_by(address=address).all()
        return {
            "status": True,
            "message": "successfully get humidity value",
            "num_results": f"{len(humidity)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "value": v.value,
                    "address": v.address
                }
                for v in humidity
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get humidity value"
        }

@app.route('/api/humidity_value/<int:address>/latest', methods=['GET'])
def get_latest_humidity_value(address):
    try:
        humidity = humidity_value.query.filter_by(address=address).all()
        if humidity: # データ存在チェック
            return {
                "status": True,
                "message": "successfully get latest humidity value",
                "data": {
                    "id": humidity[-1].id,
                    "timestamp": humidity[-1].timestamp,
                    "value": humidity[-1].value,
                    "address": humidity[-1].address
                }
            }
        else:
            return {
                "status": False,
                "message": "no data available"
            }
    except:
        return {
            "status": False,
            "message": "failed get latest humidity value"
        }

@app.route('/api/humidity_value/<int:address>/count', methods=['GET'])
def get_humidity_value_count(address):
    humidity = humidity_value.query.filter_by(address=address).all()
    return {
        "status": True,
        "message": "successfully get humidity value count",
        "num_results": f"{len(humidity)}"
    }

@app.route('/api/humidity_value/<int:address>', methods=['POST'])
def set_humidity_value(address):
    value = request.json["value"]
    if not address_exists(address):
        return {
            "status": False,
            "message": "address does not exist",
            "address": address
        }
    try:
        cre = humidity_value(timestamp = get_timestamp(), value = value, address = address)
        db.session.add(cre)
        db.session.commit()
        return {
            "status": True,
            "message": "successfully set humidity value",
            "address": address,
            "value": value
        }
    except:
        return {
            "status": False,
            "message": "failed set humidity value"
        }

# 確認用
@app.route('/api/watering_regular', methods=['GET'])
def get_all_watering_regular():
    try:
        watering = watering_regular.query.all()
        return {
            "status": True,
            "message": "successfully get all watering regular",
            "num_results": f"{len(watering)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "time_hour": v.time_hour,
                    "time_minutes": v.time_minutes,
                    "weekday": v.weekday,
                    "address": v.address
                }
                for v in watering
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get all watering regular"
        }

@app.route('/api/watering_regular/<int:address>', methods=['GET'])
def get_watering_regular(address):
    try:
        watering = watering_regular.query.filter_by(address=address).all()
        return {
            "status": True,
            "message": "successfully get watering regular",
            "num_results": f"{len(watering)}",
            "data": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp,
                    "time_hour": v.time_hour,
                    "time_minutes": v.time_minutes,
                    "weekday": v.weekday,
                    "address": v.address
                }
                for v in watering
            ]
        }
    except:
        return {
            "status": False,
            "message": "failed get watering regular"
        }

@app.route('/api/watering_regular/<int:address>', methods=['POST'])
def set_watering_regular(address):
    time_hour = request.json["time_hour"]
    time_minutes = request.json["time_minutes"]
    weekday = request.json["weekday"]
    # 変数チェック
    if time_hour < 0 or time_hour > 23 and time_minutes < 0 or time_minutes > 59:
        return {
            "status": False,
            "message": "time is invalid",
            "time_hour": time_hour,
            "time_minutes": time_minutes
        }
    if weekday not in weekdays_set:
        return {
            "status": False,
            "message": "weekday is invalid",
            "weekday": weekday
        }
    if not address_exists(address):
        return {
            "status": False,
            "message": "address does not exist",
            "address": address
        }
    # かぶりチェック
    watering = watering_regular.query.filter_by(time_hour=time_hour, time_minutes=time_minutes, weekday=weekday, address=address).all()
    if watering:
        return {
            "status": False,
            "message": "watering regular already exists",
            "address": address,
            "time_hour": time_hour,
            "time_minutes": time_minutes,
            "weekday": weekday
        }
    try:
        cre = watering_regular(timestamp = get_timestamp(), time_hour = time_hour, time_minutes = time_minutes, weekday = weekday, address = address)
        db.session.add(cre)
        db.session.commit()
        return {
            "status": True,
            "message": "successfully set watering regular",
            "address": address,
            "time_hour": time_hour,
            "time_minutes": time_minutes,
            "weekday": weekday
        }
    except:
        return {
            "status": False,
            "message": "failed set watering regular"
        }

@app.route('/api/watering_regular/<int:address>', methods=['DELETE'])
def delete_watering_regular(address):
    time_hour = request.json["time_hour"]
    time_minutes = request.json["time_minutes"]
    weekday = request.json["weekday"]
    # address, time_hour, time_minutes, weekdayが一致するデータがない場合
    if not watering_regular.query.filter_by(time_hour=time_hour, time_minutes=time_minutes, weekday=weekday, address=address).first():
        return {
            "status": False,
            "message": "watering regular does not exist",
            "address": address,
            "time_hour": time_hour,
            "time_minutes": time_minutes,
            "weekday": weekday
        }
    try:
        watering_regular.query.filter_by(time_hour=time_hour, time_minutes=time_minutes, weekday=weekday, address=address).delete()
        db.session.commit()
        return {
            "status": True,
            "message": "successfully delete watering regular",
            "address": address,
            "time_hour": time_hour,
            "time_minutes": time_minutes,
            "weekday": weekday
        }
    except:
        return {
            "status": False,
            "message": "failed delete watering regular"
        }

if __name__ == '__main__':
    app.run(threaded=True)
