#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アンケートCSVマージプログラム
convert_toyama.py, convert_ishikawa.py, convert_fukui.pyを順に実行し、
その結果のCSVファイルをマージするプログラム
"""

import csv
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

class SurveyMerger:
    def __init__(self, input_dir: str = "output", output_dir: str = "output_merge"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
    def run_conversion_scripts(self) -> bool:
        """3つの変換スクリプトを順に実行"""
        scripts = [
            "convert_toyama.py",
            "convert_ishikawa.py", 
            "convert_fukui.py"
        ]
        
        print("=== 変換スクリプトの実行 ===")
        
        for script in scripts:
            print(f"\n{script} を実行中...")
            try:
                # スクリプトを実行
                result = subprocess.run([sys.executable, script], 
                                      capture_output=True, 
                                      text=True, 
                                      encoding='utf-8')
                
                if result.returncode == 0:
                    print(f"✓ {script} が正常に完了しました")
                    if result.stdout:
                        print(f"  出力: {result.stdout.strip()}")
                else:
                    print(f"✗ {script} でエラーが発生しました")
                    if result.stderr:
                        print(f"  エラー: {result.stderr.strip()}")
                    return False
                    
            except Exception as e:
                print(f"✗ {script} の実行に失敗しました: {e}")
                return False
        
        print("\n✓ すべての変換スクリプトが正常に完了しました")
        return True
        
    def check_directories(self) -> bool:
        """ディレクトリの存在確認"""
        if not self.input_dir.exists():
            print(f"エラー: 入力ディレクトリ '{self.input_dir}' が見つかりません。")
            return False
            
        # 出力ディレクトリが存在しない場合は作成
        self.output_dir.mkdir(exist_ok=True)
        print(f"出力ディレクトリ '{self.output_dir}' を確認/作成しました。")
            
        return True
    
    def find_csv_files(self) -> List[Path]:
        """outputフォルダ配下のCSVファイルを再帰的に検索"""
        csv_files = []
        for file_path in self.input_dir.rglob("*.csv"):
            csv_files.append(file_path)
        
        if not csv_files:
            print(f"エラー: '{self.input_dir}' 配下にCSVファイルが見つかりません。")
            return []
        
        print(f"見つかったCSVファイル: {len(csv_files)}件")
        for file_path in csv_files:
            print(f"  - {file_path}")
        
        return csv_files
    
    def read_csv_data(self, file_path: Path) -> Tuple[List[str], List[List[str]]]:
        """CSVファイルのヘッダーとデータを読み込み（BOM対応）"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader)
                data = list(reader)
                return headers, data
        except Exception as e:
            print(f"エラー: ファイル '{file_path}' の読み込みに失敗しました: {e}")
            return [], []
    
    def merge_csv_files(self, csv_files: List[Path]) -> bool:
        """CSVファイルをマージ"""
        if not csv_files:
            return False
        
        # 最初のファイルのヘッダーを基準とする
        first_file = csv_files[0]
        base_headers, base_data = self.read_csv_data(first_file)
        
        if not base_headers:
            print(f"エラー: 最初のファイル '{first_file}' の読み込みに失敗しました。")
            return False
        
        print(f"基準ヘッダー: {base_headers}")
        
        # マージされたデータを格納
        merged_data = []
        
        # 最初のファイルのデータを追加
        merged_data.extend(base_data)
        print(f"'{first_file.name}' から {len(base_data)} 行を追加")
        
        # 残りのファイルのデータを追加
        for file_path in csv_files[1:]:
            headers, data = self.read_csv_data(file_path)
            
            if not headers:
                print(f"警告: ファイル '{file_path}' の読み込みに失敗しました。スキップします。")
                continue
            
            # ヘッダーが一致するかチェック
            if headers != base_headers:
                print(f"警告: ファイル '{file_path}' のヘッダーが基準と異なります。")
                print(f"  基準: {base_headers}")
                print(f"  実際: {headers}")
                print("  スキップします。")
                continue
            
            merged_data.extend(data)
            print(f"'{file_path.name}' から {len(data)} 行を追加")
        
        # マージされたデータをCSVファイルに出力
        output_file = self.output_dir / "merged_survey.csv"
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(base_headers)  # ヘッダー行を書き込み
                writer.writerows(merged_data)  # データ行を書き込み
            
            print(f"マージ完了: '{output_file}' に {len(merged_data)} 件の回答を保存しました。")
            return True
            
        except Exception as e:
            print(f"エラー: 出力ファイルの作成に失敗しました: {e}")
            return False
    
    def run(self):
        """メイン処理"""
        print("=== アンケートCSVマージプログラム ===")
        print()
        
        # 1. 変換スクリプトの実行
        if not self.run_conversion_scripts():
            return False
        
        print("\n=== CSVファイルのマージ ===")
        
        # 2. ディレクトリの確認
        if not self.check_directories():
            return False
        
        # 3. CSVファイルの検索
        csv_files = self.find_csv_files()
        if not csv_files:
            return False
        
        # 4. マージ実行
        success = self.merge_csv_files(csv_files)
        return success

def main():
    """メイン関数"""
    merger = SurveyMerger()
    success = merger.run()
    
    if success:
        print("\nプログラムが正常に完了しました。")
    else:
        print("\nプログラムがエラーで終了しました。")
        sys.exit(1)

if __name__ == "__main__":
    main() 