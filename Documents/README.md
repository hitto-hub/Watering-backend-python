# Watering System API ドキュメント

不完全なdocumentationを含んでいます。

## 概要

このプログラムは、システムに関連するデータの管理を行うWebアプリケーションです。Flaskを使用しており、SQLAlchemyによるデータベース操作、APSschedulerを使用した定期実行タスクが含まれています。主に湿度、温度、湿気などのセンサーデータとそれに関連する給水指示を管理するAPIを提供します。

## 使用技術

- **Flask**: Webアプリケーションフレームワーク
- **SQLAlchemy**: ORM (Object Relational Mapping) ツール
- **SQLite**: データベース
- **APScheduler**: 定期実行タスクのスケジューラー
- **Plotly**: グラフ描画ライブラリ
- **ZoneInfo**: タイムゾーン管理
- **Flask-SQLAlchemy**: Flask用のSQLAlchemy拡張モジュール

## データベースモデル

### `wetness_value`
土壌の湿度を記録します。

| フィールド名  | 型           | 説明       |
|------------|--------------|-----------|
| `id`       | `Integer`    | 主キー      |
| `timestamp`| `String`     | 記録時刻     |
| `value`    | `Integer`    | 湿度値      |
| `address`  | `Integer`    | 関連する住所 |

### `temperature_value`
温度データを記録します。

| フィールド名  | 型           | 説明       |
|------------|--------------|-----------|
| `id`       | `Integer`    | 主キー      |
| `timestamp`| `String`     | 記録時刻     |
| `value`    | `Integer`    | 温度値      |
| `address`  | `Integer`    | 関連する住所 |

### `humidity_value`
湿度データを記録します。

| フィールド名  | 型           | 説明       |
|------------|--------------|-----------|
| `id`       | `Integer`    | 主キー      |
| `timestamp`| `String`     | 記録時刻     |
| `value`    | `Integer`    | 湿度値      |
| `address`  | `Integer`    | 関連する住所 |

### `addresses`
住所に関連する名前を保存します。

| フィールド名  | 型           | 説明       |
|------------|--------------|-----------|
| `address`  | `Integer`    | 主キー      |
| `name`     | `String`     | 住所の名前  |

### `water_supply`
給水の履歴データを記録します。

| フィールド名  | 型           | 説明       |
|------------|--------------|-----------|
| `id`       | `Integer`    | 主キー      |
| `timestamp`| `String`     | 記録時刻     |
| `type`     | `Integer`    | 給水の種類  |
| `address`  | `Integer`    | 関連する住所 |

### `watering_regular`
定期的な水やりスケジュールを記録します。

| フィールド名  | 型           | 説明       |
|------------|--------------|-----------|
| `id`       | `Integer`    | 主キー      |
| `timestamp`| `String`     | 記録時刻     |
| `time_hour`| `Integer`    | 時間（24時間制） |
| `time_minutes` | `Integer` | 分         |
| `weekday`  | `String`     | 曜日       |
| `address`  | `Integer`    | 関連する住所 |

### `instructions`
給水指示を記録します。

| フィールド名  | 型           | 説明       |
|------------|--------------|-----------|
| `id`       | `Integer`    | 主キー      |
| `timestamp`| `String`     | 記録時刻     |
| `address`  | `Integer`    | 関連する住所 |
| `instruction` | `Integer`  | 指示内容（例：給水） |

## API エンドポイント

### `/api/addresses` - 全アドレスの取得
- **GET**: 全アドレス情報を取得します。

#### レスポンス例:
```json
{
    "status": true,
    "message": "successfully get all address",
    "num_results": "5",
    "data": [
        {
            "address": 1,
            "name": "office"
        },
        {
            "address": 2,
            "name": "warehouse"
        }
    ]
}
```

### `/api/addresses/<int:address>` - 特定のアドレス情報を取得
- **GET**: 指定したアドレスに関連する情報を取得します。

#### レスポンス例:
```json
{
    "status": true,
    "message": "successfully get address",
    "address": 1,
    "name": "office"
}
```

### `/api/instructions` - 全給水指示の取得
- **GET**: 全給水指示を取得します。

#### レスポンス例:
```json
{
    "status": true,
    "message": "successfully get all instructions",
    "num_results": "10",
    "data": [
        {
            "id": 1,
            "timestamp": "2025/04/03 12:00:00",
            "address": 1,
            "instruction": 1
        }
    ]
}
```

### `/api/watering_regular` - 定期水やり設定の取得
- **GET**: 定期水やり設定を取得します。

#### レスポンス例:
```json
{
    "status": true,
    "message": "successfully get all watering regular",
    "num_results": "3",
    "data": [
        {
            "id": 1,
            "timestamp": "2025/04/03 12:00:00",
            "time_hour": 6,
            "time_minutes": 30,
            "weekday": "mon",
            "address": 1
        }
    ]
}
```

### `/api/supply` - 全給水履歴の取得
- **GET**: 全給水履歴を取得します。

#### レスポンス例:
```json
{
    "status": true,
    "message": "successfully get all supply",
    "num_results": "20",
    "data": [
        {
            "id": 1,
            "timestamp": "2025/04/03 12:00:00",
            "type": 1,
            "address": 1
        }
    ]
}
```

## リクエストボディ

### `/api/addresses` - アドレスの新規登録
- **POST**: 新しいアドレスを配布します。

  - `name`: 住所の名前

  #### リクエスト例:
  ```json
  {
    "name": "new_office"
  }
  ```

### `/api/instructions/<int:address>` - 給水指示
- **POST**: 指定されたアドレスに給水指示を出します。

  - `instruction`: 指示内容（例：1は給水）

  #### リクエスト例:
  ```json
  {
    "instruction": 1
  }
  ```

### `/api/watering_regular/<int:address>` - 定期水やり設定
- **POST**: 定期的な水やりを設定します。

  - `time_hour`: 水やりの時刻（24時間制）
  - `time_minutes`: 水やりの分
  - `weekday`: 水やりを実行する曜日（例：`mon`）

  #### リクエスト例:
  ```json
  {
    "time_hour": 6,
    "time_minutes": 30,
    "weekday": "mon"
  }
  ```

## 実行方法

1. **依存関係のインストール**
   必要なライブラリをインストールします。

   ```bash
   pip install -r requirements.txt
   ```

2. **アプリケーションの実行**
   アプリケーションを起動します。

   ```bash
   python app.py
   ```

3. **スケジューラーの動作**
   定期的に給水タスクが実行されるように設定されています。これにより、毎分実行されるタスクが適切に機能します。

## その他

- アドレスの名前変更や削除などの機能も実装されていますが、削除時は関連するすべてのデータ（指示、湿度データなど）も削除されることに注意してください。
- 定期的な水やり設定は曜日と時刻に基づき、指定されたタイミングで給水指示を出します。
