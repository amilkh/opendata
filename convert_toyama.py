import csv
import json
import os
import codecs
from datetime import datetime

def format_date_string(date_str):
    """
    日付文字列を yyyy/MM/dd hh:mm:ss 形式に統一
    """
    if not date_str or date_str.strip() == "":
        return ""
    
    try:
        # 既存の形式を解析（例: 2025/04/18）
        date_obj = datetime.strptime(date_str.strip(), '%Y/%m/%d')
        # yyyy/MM/dd 00:00:00 形式に変換
        return date_obj.strftime('%Y/%m/%d 00:00:00')
    except ValueError:
        # 解析できない場合は元の値をそのまま返す
        return date_str

def format_information_source(row):
    """
    情報源（デジタル）と情報源（デジタル以外）を連結して処理
    """
    digital_source = row.get('情報源（デジタル）', '').strip()
    non_digital_source = row.get('情報源（デジタル以外）', '').strip()
    
    # 元のダブルクォーテーションを除去
    digital_source = digital_source.strip('"')
    non_digital_source = non_digital_source.strip('"')
    
    # 両方の情報源を連結（ダブルクォーテーションなしで連結）
    if digital_source and non_digital_source:
        combined = f"{digital_source}, {non_digital_source}"
    elif digital_source:
        combined = digital_source
    elif non_digital_source:
        combined = non_digital_source
    else:
        combined = ""
    
    # 先頭と最後尾のカンマを削除
    combined = combined.strip()
    if combined.startswith(','):
        combined = combined[1:].strip()
    if combined.endswith(','):
        combined = combined[:-1].strip()
    
    # 空文字の場合は空文字を返す
    if not combined:
        return ""
    
    # ダブルクォーテーションで囲まずにそのまま返す
    return combined

def check_information_source_flags(information_source):
    """
    情報源の文字列を解析して、各フラグ項目に0または1を設定
    """
    # 情報源の文字列を取得（ダブルクォートを除去）
    source_str = information_source.strip('"') if information_source else ""
    
    # 各フラグ項目の定義
    flags = {
        "Facebook": ["Facebook"],
        "Google": ["Google"],
        "Googleマップ": ["Googleマップ"],
        "Instagram": ["Instagram"],
        "TikTok": ["TikTok"],
        "X（旧Twitter）": ["X（旧Twitter）", "X(旧：Twitter)", "Twitter"],
        "YouTube": ["YouTube", "YOUTUBE"],
        "SNS広告": ["SNS広告"],
        "ブログ": ["ブログ"],
        "まとめサイト": ["まとめサイト"],
        "インターネット・アプリ": ["インターネット・アプリ", "蜃気楼マラソン公式ページ"],
        "デジタルニュース": ["デジタルニュースサイト"],
        "宿泊予約Webサイト": ["宿泊予約Webサイト", "OTA"],
        "宿泊施設": ["宿泊施設", "宿泊施設のウェブサイト"],
        "TV・ラジオ番組やCM": ["TV・ラジオ番組やCM"],
        "ラブライブのスタンプラリー": ["ラブライブのスタンプラリー"],
        "新聞・雑誌・ガイドブック": ["新聞", "雑誌", "ガイドブック"],
        "旅行会社": ["旅行会社"],
        "友人・知人": ["友人", "知人"],
        "地元の人": ["タクシードライバー", "地元の人"],
        "観光パンフレット・ポスター": ["観光パンフレット", "ポスター"],
        "観光案内所": ["観光案内所", "観光協会等の案内所"],
        "観光展・物産展": ["観光展", "物産展"],
        "観光連盟やDMOのHP": ["観光連盟やDMOのHP", "富山県内市町村の観光公式サイト", "富山県観光公式サイト「とやま観光ナビ」"]
    }
    
    # 各フラグをチェック
    result = {}
    matched_keywords = set()
    
    for flag_name, keywords in flags.items():
        flag_value = 0
        for keyword in keywords:
            if keyword in source_str:
                flag_value = 1
                matched_keywords.add(keyword)
                break
        result[flag_name] = flag_value
    
    # "その他"の判定（上記以外の文字列が含まれる場合）
    # 情報源に何か文字列が含まれていて、かつ上記のキーワードにマッチしない場合
    if source_str and not matched_keywords:
        result["その他"] = 1
    else:
        result["その他"] = 0
    
    return result

def convert_toyama_csv():
    # ファイルパス
    input_csv = "input/toyama/toyama.csv"
    mapping_json = "input/toyama/column_mapping_toyama.json"
    output_csv = "output/toyama/toyama_converted.csv"
    
    # JSONマッピングファイルを読み込み
    with open(mapping_json, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    # 出力用のヘッダー（JSONのキー順）
    output_headers = list(mapping.keys())
    
    # 入力CSVを読み込み（BOMを自動除去）
    with codecs.open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        input_headers = reader.fieldnames
        rows = list(reader)

    # 出力CSVを作成
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー行を書き込み
        writer.writerow(output_headers)
        
        # データ行を処理
        for row in rows:
            output_row = []
            
            for header in output_headers:
                # 1項目目の"対象県（富山/石川/福井）"は"富山"を出力
                if header == "対象県（富山/石川/福井）":
                    output_row.append("富山")
                # 「情報源」項目の特別処理
                elif header == "情報源":
                    value = format_information_source(row)
                    output_row.append(value)
                # 情報源関連のフラグ項目の処理
                elif header in ["Facebook", "Google", "Googleマップ", "Instagram", "TikTok", 
                               "X（旧Twitter）", "YouTube", "SNS広告", "ブログ", "まとめサイト",
                               "インターネット・アプリ", "デジタルニュース", "宿泊予約Webサイト",
                               "宿泊施設", "TV・ラジオ番組やCM", "ラブライブのスタンプラリー",
                               "新聞・雑誌・ガイドブック", "旅行会社", "友人・知人", "地元の人",
                               "観光パンフレット・ポスター", "観光案内所", "観光展・物産展",
                               "観光連盟やDMOのHP", "その他"]:
                    # 情報源の文字列を取得
                    information_source = format_information_source(row)
                    # フラグをチェック
                    flags = check_information_source_flags(information_source)
                    # 該当するフラグの値を設定
                    value = flags.get(header, 0)
                    output_row.append(value)
                else:
                    # マッピングから対応する入力項目名を取得
                    input_field = mapping[header]
                    
                    if input_field == "":
                        # マッピングが空文字の場合は空文字を出力
                        output_row.append("")
                    elif input_field in row:
                        # 入力CSVに項目が存在する場合はその値を出力
                        value = row[input_field]
                        
                        # 「アンケート回答日」の場合は日付形式を統一
                        if header == "アンケート回答日":
                            value = format_date_string(value)
                        
                        output_row.append(value)
                    else:
                        # 入力CSVに項目が存在しない場合は空文字を出力
                        output_row.append("")
            
            writer.writerow(output_row)
    
    print(f"変換完了: {output_csv}")
    print(f"出力行数: {len(rows)}")

if __name__ == "__main__":
    convert_toyama_csv()
