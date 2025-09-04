import csv
import json
import os
import codecs
import re
from datetime import datetime

def process_fukui_csv(input_file_path):
    """
    福井CSVファイルの前処理
    1. 会員ID（6桁数字）を"000000"に置換
    2. LFを空文字に置換
    3. "000000"の前にCRLFを挿入
    """
    try:
        # バイナリモードでファイルを読み込み
        with open(input_file_path, 'rb') as f:
            content_bytes = f.read()
        
        # BOMを除去
        if content_bytes.startswith(b'\xef\xbb\xbf'):
            content_bytes = content_bytes[3:]
        
        # バイト列を文字列に変換（複数のエンコーディングを試す）
        encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp']
        content = None
        
        for encoding in encodings:
            try:
                content = content_bytes.decode(encoding)
                print(f"エンコーディング検出: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise UnicodeDecodeError("すべてのエンコーディングでデコードに失敗しました")
        
        print(f"処理前のファイルサイズ: {len(content)} 文字")
        
        # 1. 会員ID（6桁数字）を"000000"に置換
        content = re.sub(r'\b[0-9]{6}\b', '000000', content)
        print("会員IDの置換完了")
        
        # 2. LFを空文字に置換
        content = content.replace('\n', '')
        print("LFの削除完了")
        
        # 3. "000000"の前にCRLFを挿入（最初の"000000"は除く）
        # 最初の"000000"を一時的に置換
        content = content.replace('000000', '___FIRST_000000___', 1)
        
        # 残りの"000000"の前にCRLFを挿入
        content = content.replace('000000', '\r\n000000')
        
        # 最初の"000000"を元に戻す
        content = content.replace('___FIRST_000000___', '000000')
        
        print("CRLFの挿入完了")
        print(f"処理後のファイルサイズ: {len(content)} 文字")
        
        # 修正した内容をフォーマット済みファイルに出力
        formatted_file_path = input_file_path.replace('.csv', '_formatted.csv')
        with open(formatted_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"福井CSVファイルの前処理完了: {formatted_file_path}")
        return True
        
    except Exception as e:
        print(f"福井CSVファイル前処理エラー: {e}")
        return False

def convert_satisfaction_to_number(satisfaction_str):
    """
    満足度の文字列を数値に変換
    とても満足=5, 満足=4, どちらでもない=3, 不満=2, とても不満=1
    """
    if not satisfaction_str or satisfaction_str.strip() == "":
        return ""
    
    satisfaction_str = satisfaction_str.strip()
    
    satisfaction_mapping = {
        "とても満足": 5,
        "満足": 4,
        "どちらでもない": 3,
        "不満": 2,
        "とても不満": 1
    }
    
    return satisfaction_mapping.get(satisfaction_str, satisfaction_str)

def format_date_string(date_str):
    """
    日付文字列を yyyy/MM/dd hh:mm:ss 形式に統一
    yyyy-MM-dd hh:mm:ss 形式から変換
    """
    if not date_str or date_str.strip() == "":
        return ""
    
    try:
        # yyyy-MM-dd hh:mm:ss 形式を解析
        date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d %H:%M:%S')
        # yyyy/MM/dd hh:mm:ss 形式に変換
        return date_obj.strftime('%Y/%m/%d %H:%M:%S')
    except ValueError:
        try:
            # 別の形式も試す（例: yyyy-MM-dd）
            date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d')
            # yyyy/MM/dd 00:00:00 形式に変換
            return date_obj.strftime('%Y/%m/%d 00:00:00')
        except ValueError:
            # 解析できない場合は元の値をそのまま返す
            return date_str

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
        "観光連盟やDMOのHP": ["観光連盟やDMOのHP"]
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

def convert_fukui_csv():
    # ファイルパス
    input_csv = "input/fukui/fukui_formatted.csv"
    mapping_json = "input/fukui/column_mapping_fukui.json"
    output_csv = "output/fukui/fukui_converted.csv"
    
    # JSONマッピングファイルを読み込み
    with open(mapping_json, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    # 出力用のヘッダー（JSONのキー順）
    output_headers = list(mapping.keys())
    
    # 入力CSVを読み込み（複数のエンコーディングを試す）
    encodings = ['utf-8-sig', 'utf-8', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp']
    reader = None
    input_headers = None
    rows = None
    
    for encoding in encodings:
        try:
            with codecs.open(input_csv, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                input_headers = reader.fieldnames
                rows = list(reader)
            print(f"CSV読み込み成功 - エンコーディング: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    
    if reader is None:
        raise UnicodeDecodeError("すべてのエンコーディングでCSVファイルの読み込みに失敗しました")
    
    # 出力CSVを作成
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー行を書き込み
        writer.writerow(output_headers)
        
        # データ行を処理
        for row in rows:
            output_row = []
            
            for header in output_headers:
                # 1項目目の"対象県（富山/石川/福井）"は"福井"を出力
                if header == "対象県（富山/石川/福井）":
                    output_row.append("福井")
                # 情報源関連のフラグ項目の処理
                elif header in ["Facebook", "Google", "Googleマップ", "Instagram", "TikTok", 
                               "X（旧Twitter）", "YouTube", "SNS広告", "ブログ", "まとめサイト",
                               "インターネット・アプリ", "デジタルニュース", "宿泊予約Webサイト",
                               "宿泊施設", "TV・ラジオ番組やCM", "ラブライブのスタンプラリー",
                               "新聞・雑誌・ガイドブック", "旅行会社", "友人・知人", "地元の人",
                               "観光パンフレット・ポスター", "観光案内所", "観光展・物産展",
                               "観光連盟やDMOのHP", "その他"]:
                    # 情報源の文字列を取得（福井の場合は「情報収集ALL」を使用）
                    information_source = row.get('情報収集ALL', '')
                    # フラグをチェック
                    flags = check_information_source_flags(information_source)
                    # 該当するフラグの値を設定
                    value = flags.get(header, 0)
                    output_row.append(value)
                # 満足度項目の処理
                elif header in ["交通の満足度", 
                               "満足度（食べ物・料理）", "満足度（宿泊施設）", 
                               "満足度（買い物（工芸品・特産品など））", "満足度買い物（観光・体験）", 
                               "満足度（旅行全体）", "満足度（商品・サービス）"]:
                    # マッピングから対応する入力項目名を取得
                    input_field = mapping[header]
                    
                    if input_field == "":
                        # マッピングが空文字の場合は空文字を出力
                        output_row.append("")
                    elif input_field in row:
                        # 入力CSVに項目が存在する場合は満足度を数値に変換
                        value = row[input_field]
                        converted_value = convert_satisfaction_to_number(value)
                        output_row.append(converted_value)
                    else:
                        # 入力CSVに項目が存在しない場合は空文字を出力
                        output_row.append("")
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

def main():
    """
    メイン処理
    """
    # 福井CSVファイルの前処理を実行
    input_csv = "input/fukui/fukui.csv"
    if os.path.exists(input_csv):
        print("福井CSVファイルの前処理を開始します...")
        if process_fukui_csv(input_csv):
            print("福井CSVファイルの前処理が完了しました。")
        else:
            print("福井CSVファイルの前処理に失敗しました。")
            return
    else:
        print(f"入力ファイルが見つかりません: {input_csv}")
        return
    
    # CSV変換を実行
    print("CSV変換を開始します...")
    convert_fukui_csv()

if __name__ == "__main__":
    main()