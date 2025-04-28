import time
import traceback
from datetime import datetime
from GeminiCurator import Curator, is_within_schedule

def main():
    now = datetime.now()
    start_time = now.replace(hour=12, minute=35, second=0, microsecond=0)
    end_time = now.replace(hour=23, minute=36, second=0, microsecond=0)

    CuratorMonitor = Curator(api_key="AIzaSyDgPvBN0glOm1v7OvXXDZC2rhKQEK6VyWc", 
                             save_images_folder="GeneratedImages", 
                             save_texts_folder = "GeneratedTexts",
                             start_time=start_time, 
                             end_time=end_time,
                             )
    while True:
        if is_within_schedule(start_time, end_time):
            try:
                CuratorMonitor.run_exhibition()  # 執行策展
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >>> GeminiCurator 開始執行")
                # GeminiCurator.main()  # 執行 GeminiCurator 裡的 main() 函數
            except Exception as e:
                print("\n" + "=" * 60)
                print("[ERROR] GeminiCurator 崩潰了，錯誤訊息：")
                traceback.print_exc()  # 印出詳細錯誤
                print("=" * 60)
                print(">>> 5 秒後重啟 GeminiCurator...\n")
                time.sleep(5)
            # finally:
            #     # 避免 importlib cache 問題，強制 reload
            #     importlib.reload(GeminiCurator)
        else:
            # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💤 非執行時間，等待 60 秒後再檢查...")
            time.sleep(60)  # 休息 60 秒再檢查一次

if __name__ == "__main__":
    print("===== Gemini Curator Monitor 啟動 =====")
    main()

