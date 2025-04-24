import time
import traceback
import importlib

def main():
    while True:
        try:
            # 動態匯入 GeminiCurator.py
            GeminiCurator = importlib.import_module("GeminiCurator")
            print(">>> GeminiCurator 開始執行")
            GeminiCurator.main() # 執行 GeminiCurator 裡的 main() 函數
        except Exception as e:
            print("\n" + "=" * 60)
            print("[ERROR] GeminiCurator 崩潰了，錯誤訊息：")
            traceback.print_exc() # 印出詳細錯誤
            print("=" * 60)
            print(">>> 5 秒後重啟 GeminiCurator...\n")
            time.sleep(5)
        finally:
            # 避免 importlib cache 問題，強制 reload
            importlib.reload(GeminiCurator)

if __name__ == "__main__":
    print("===== Gemini Curator Monitor 啟動 =====")
    main()


