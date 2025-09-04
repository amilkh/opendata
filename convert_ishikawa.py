import csv
import json
import os
import codecs
from datetime import datetime

def remove_unwanted_linebreaks(input_file_path):
    """
    改行コードLFと単独のCRを削除する（CRLFは保持）
    """
    try:
        # バイナリモードでファイルを読み込み（改行コードを正規化しない）
        with open(input_file_path, 'rb') as f:
            content_bytes = f.read()
        
        # デバッグ情報：バイナリレベルでの改行コードの数を確認
        lf_count = content_bytes.count(b'\n')
        cr_count = content_bytes.count(b'\r')
        
        # CRLFの数を正しくカウント
        crlf_count = 0
        for i in range(len(content_bytes) - 1):
            if content_bytes[i] == ord('\r') and content_bytes[i + 1] == ord('\n'):
                crlf_count += 1
        
        # 単独のCRとLFの数を計算
        standalone_cr = cr_count - crlf_count
        standalone_lf = lf_count - crlf_count
        
        print(f"デバッグ: 処理前の改行コード数")
        print(f"  LF (\\n): {lf_count}")
        print(f"  CRLF (\\r\\n): {crlf_count}")
        print(f"  CR (\\r): {cr_count}")
        print(f"  単独のLF: {standalone_lf}")
        print(f"  単独のCR: {standalone_cr}")
        
        # 文字列に変換（BOMを除去）
        if content_bytes.startswith(b'\xef\xbb\xbf'):
            content_bytes = content_bytes[3:]  # BOMを除去
        
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
        
        # 不要な改行コードを削除（CRLFは保持）
        # \r\n (CRLF) を一時的に特殊文字に置換
        content = content.replace('\r\n', '___CRLF___')
        
        # 単独のLF (\n) を削除
        content = content.replace('\n', '')
        
        # 単独のCR (\r) を削除
        content = content.replace('\r', '')
        
        # 一時的な特殊文字をCRLFに戻す
        content = content.replace('___CRLF___', '\r\n')
        
        # 修正した内容をフォーマット済みファイルに出力
        formatted_file_path = input_file_path.replace('.csv', '_formatted.csv')
        with open(formatted_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"不要な改行コードの削除完了: {formatted_file_path}")
        return True
        
    except Exception as e:
        print(f"改行コード削除エラー: {e}")
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
    MM/dd/yyyy hh:mm:ss 形式から変換
    """
    if not date_str or date_str.strip() == "":
        return ""
    
    try:
        # MM/dd/yyyy hh:mm:ss 形式を解析
        date_obj = datetime.strptime(date_str.strip(), '%m/%d/%Y %H:%M:%S')
        # yyyy/MM/dd hh:mm:ss 形式に変換
        return date_obj.strftime('%Y/%m/%d %H:%M:%S')
    except ValueError:
        try:
            # 別の形式も試す（例: MM/dd/yyyy）
            date_obj = datetime.strptime(date_str.strip(), '%m/%d/%Y')
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

def convert_ishikawa_csv():
    # ファイルパス
    input_csv = "input/ishikawa/ishikawa_formatted.csv"
    mapping_json = "input/ishikawa/column_mapping_ishikawa.json"
    output_csv = "output/ishikawa/ishikawa_converted.csv"
    
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
                # 1項目目の"対象県（富山/石川/福井）"は"石川"を出力
                if header == "対象県（富山/石川/福井）":
                    output_row.append("石川")
                # 情報源関連のフラグ項目の処理
                elif header in ["Facebook", "Google", "Googleマップ", "Instagram", "TikTok", 
                               "X（旧Twitter）", "YouTube", "SNS広告", "ブログ", "まとめサイト",
                               "インターネット・アプリ", "デジタルニュース", "宿泊予約Webサイト",
                               "宿泊施設", "TV・ラジオ番組やCM", "ラブライブのスタンプラリー",
                               "新聞・雑誌・ガイドブック", "旅行会社", "友人・知人", "地元の人",
                               "観光パンフレット・ポスター", "観光案内所", "観光展・物産展",
                               "観光連盟やDMOのHP", "その他"]:
                    # 情報源の文字列を取得（石川の場合は「今回   当施設   を訪れる際に参考にした情報源は何ですか？（複数選択可）」を使用）
                    information_source = row.get('今回   当施設   を訪れる際に参考にした情報源は何ですか？（複数選択可）', '')
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
    # 不要な改行コードの削除を実行
    input_csv = "input/ishikawa/ishikawa.csv"
    if os.path.exists(input_csv):
        print("不要な改行コードの削除を開始します...")
        if remove_unwanted_linebreaks(input_csv):
            print("不要な改行コードの削除が完了しました。")
        else:
            print("不要な改行コードの削除に失敗しました。")
    else:
        print(f"入力ファイルが見つかりません: {input_csv}")
        return
    
    # CSV変換を実行
    print("CSV変換を開始します...")
    convert_ishikawa_csv()

if __name__ == "__main__":
    main()