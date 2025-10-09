# merged_survey_csv_py

富山県、石川県、福井県のアンケートCSVデータを標準化してマージするPythonスクリプト

## 概要

このプロジェクトは、3つの県（富山県、石川県、福井県）から収集されたアンケートデータを、統一された形式に変換し、1つのCSVファイルにマージするためのツールです。

### 主な機能

- **データ標準化**: 各県の異なる形式のCSVデータを統一された形式に変換
- **列マッピング**: JSONファイルを使用した列名マッピング
- **データ前処理**: 改行コードの正規化、会員IDの匿名化、日付形式の統一
- **情報源フラグ生成**: 情報源データから各種メディア・チャネルのフラグを自動生成
- **CSVマージ**: 変換されたデータを1つのファイルに統合

## ファイル構成

```
merged_survey_csv_py/
├── convert_toyama.py          # 富山県データ変換スクリプト
├── convert_ishikawa.py        # 石川県データ変換スクリプト
├── convert_fukui.py           # 福井県データ変換スクリプト
├── merge_survey.py            # メイン実行スクリプト（変換+マージ）
├── input/                     # 入力データ
│   ├── toyama/
│   │   ├── toyama.csv                    # 富山県アンケートデータ
│   │   └── column_mapping_toyama.json    # 富山県列マッピング定義
│   ├── ishikawa/
│   │   ├── ishikawa.csv                  # 石川県アンケートデータ
│   │   └── column_mapping_ishikawa.json  # 石川県列マッピング定義
│   └── fukui/
│       ├── fukui.csv                     # 福井県アンケートデータ
│       └── column_mapping_fukui.json     # 福井県列マッピング定義
├── output/                    # 変換後のデータ
│   ├── toyama/
│   │   └── toyama_converted.csv
│   ├── ishikawa/
│   │   └── ishikawa_converted.csv
│   └── fukui/
│       └── fukui_converted.csv
└── output_merge/              # マージ後のデータ
    └── merged_survey.csv      # 最終出力ファイル
```

## 実行手順

### 1. 環境準備

#### Pythonのインストール確認

まず、Pythonがインストールされているか確認してください：

```bash
python --version
# または
python3 --version
```

バージョン3.6以上が表示されれば、Pythonは既にインストールされています。

#### MacでのPythonインストール

**方法1: Homebrewを使用（推奨）**

1. Homebrewをインストール（未インストールの場合）：
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Pythonをインストール：
```bash
brew install python
```

**方法2: 公式インストーラーを使用**

1. [Python公式サイト](https://www.python.org/downloads/)から最新版をダウンロード
2. ダウンロードした`.pkg`ファイルをダブルクリックしてインストール
3. インストール時に「Add Python to PATH」にチェックを入れる

#### WindowsでのPythonインストール

**方法1: Microsoft Storeを使用（推奨）**

1. Microsoft Storeを開く
2. 検索で「Python」を検索
3. 最新版（Python 3.11など）をインストール

**方法2: 公式インストーラーを使用**

1. [Python公式サイト](https://www.python.org/downloads/)から最新版をダウンロード
2. ダウンロードした`.exe`ファイルを実行
3. インストール時に「Add Python to PATH」にチェックを入れる
4. 「Install Now」をクリック

#### インストール確認

インストール後、以下のコマンドで確認してください：

```bash
# Pythonのバージョン確認
python --version
# または
python3 --version

# pip（パッケージマネージャー）の確認
pip --version
# または
pip3 --version
```

正常にバージョンが表示されれば、インストールは成功です。

### 2. 実行

ターミナルから、以下のコマンドで変換とマージを一括実行します：

```bash
python merge_survey.py
```

ZIPファイルでダウンロードした場合は、そのZIPを解凍したディレクトリへ移動し実行します

例）ZIPを解凍したディレクトリが、/Users/自身のユーザ名/Desktop/merged_survey_csv_py-mainの場合

```bash
# ディレクトリ移動
cd /Users/自身のユーザ名/Desktop/merged_survey_csv_py-main
# マージ一括実行
python merge_survey.py
```

### 3. 個別実行

各県のデータを個別に変換したい場合は、以下のコマンドを使用できます：

```bash
# 富山県データの変換
python convert_toyama.py

# 石川県データの変換
python convert_ishikawa.py

# 福井県データの変換
python convert_fukui.py
```

### ※入力データを入れ替えたい時の配置

各県のCSVファイルを入れ替えたい、または列マッピングを変更したい場合は各県のcolumn_mapping_xxxx.jsonファイルの内容を更新し、ファイルを以下のように配置してください：

- `input/toyama/toyama.csv` - 富山県のアンケートデータ
- `input/toyama/column_mapping_toyama.json` - 富山県の列マッピング定義
- `input/ishikawa/ishikawa.csv` - 石川県のアンケートデータ
- `input/ishikawa/column_mapping_ishikawa.json` - 石川県の列マッピング定義
- `input/fukui/fukui.csv` - 福井県のアンケートデータ
- `input/fukui/column_mapping_fukui.json` - 福井県の列マッピング定義


## データ変換の詳細

### 共通処理

- **対象県の設定**: 各県のデータに「対象県（富山/石川/福井）」列を追加し、該当する県名を設定
- **BOM除去**: 入力CSVファイルのBOM（Byte Order Mark）を自動除去
- **日付形式統一**: 「アンケート回答日」を `yyyy/MM/dd hh:mm:ss` 形式に統一

### 県別処理

#### 富山県（convert_toyama.py）
- **情報源連結**: 「情報源（デジタル）」と「情報源（デジタル以外）」を連結
- **情報源フラグ生成**: 25種類の情報源フラグを自動生成

#### 石川県（convert_ishikawa.py）
- **改行コード正規化**: LFと単独CRを削除し、CRLFを保持
- **情報源フラグ生成**: 「今回   当施設   を訪れる際に参考にした情報源は何ですか？（複数選択可）」からフラグ生成

#### 福井県（convert_fukui.py）
- **会員ID匿名化**: 6桁数字の会員IDを「000000」に置換
- **改行コード処理**: LFを削除し、レコード区切りとしてCRLFを挿入
- **情報源フラグ生成**: 「情報収集ALL」からフラグ生成

### 情報源フラグ

以下の25種類のフラグが自動生成されます：

- Facebook, Google, Googleマップ, Instagram, TikTok
- X（旧Twitter）, YouTube, SNS広告, ブログ, まとめサイト
- インターネット・アプリ, デジタルニュース, 宿泊予約Webサイト, 宿泊施設
- TV・ラジオ番組やCM, ラブライブのスタンプラリー, 新聞・雑誌・ガイドブック
- 旅行会社, 友人・知人, 地元の人, 観光パンフレット・ポスター
- 観光案内所, 観光展・物産展, 観光連盟やDMOのHP, その他

各フラグは、対応するキーワードが情報源に含まれている場合は1、含まれていない場合は0が設定されます。

## 出力ファイル

### 変換後ファイル
- `output/toyama/toyama_converted.csv`
- `output/ishikawa/ishikawa_converted.csv`
- `output/fukui/fukui_converted.csv`

### マージ後ファイル
- `output_merge/merged_survey.csv` - 全県のデータを統合した最終ファイル

## 注意事項

- 入力CSVファイルはUTF-8エンコーディングである必要があります
- 列マッピングJSONファイルは有効なJSON形式である必要があります
- 出力ディレクトリは自動的に作成されます
- エラーが発生した場合は、コンソールに詳細なエラーメッセージが表示されます

## ライセンス

- [CC-BY（表示）](https://creativecommons.org/licenses/by/4.0/) 北陸インバウンド観光DX・データコンソーシアム 

- 出典元を記載いただければどなたでも自由にお使いいただけます。

## 出典元

（この観光アンケートデータ集約プログラムは以下の著作物を改変して利用しています。）

- 富山県のデータについて： [富山県データ連携基盤CKAN 富山県観光ウェブアンケートデータ](https://ckan.tdcp.pref.toyama.jp/dataset/kanko_data)、富山県、[CC-BY（表示）](https://opendefinition.org/licenses/cc-by/)

- 石川県のデータについて： [いしかわ観光QRアンケートデータ-集約データ-表形式データ-全エリア](https://sites.google.com/view/milli-ishikawa-pref/data)、石川県、[CC-BY（表示） 2.1](http://creativecommons.org/licenses/by/2.1/jp/)

- 福井県のデータについて：[福井県観光データシステム「FTAS」により公開されたオープンデータ](https://github.com/code4fukui/fukui-kanko-survey)、福井県観光連盟、[CC-BY（表示）](https://creativecommons.org/licenses/by/4.0/)

