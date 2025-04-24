import time
import traceback
import importlib

def main():
    while True:
        try:
            # 動態匯入 GeminiAudience3.py
            GeminiAudience3 = importlib.import_module("GeminiAudience3")
            print(">>> GeminiAudience3 開始執行")
            GeminiAudience3.main() 
        except Exception as e:
            print("\n" + "=" * 60)
            print("[ERROR] GeminiAudience3 崩潰了，錯誤訊息：")
            traceback.print_exc() # 印出詳細錯誤
            print("=" * 60)
            print(">>> 5 秒後重啟 GeminiAudience3...\n")
            time.sleep(5)
        finally:
            # 避免 importlib cache 問題，強制 reload
            importlib.reload(GeminiAudience3)

if __name__ == "__main__":
    print("===== Gemini Audience2 Monitor 啟動 =====")
    main()


