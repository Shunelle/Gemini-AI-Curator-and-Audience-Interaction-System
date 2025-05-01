import time
import traceback
import argparse

from datetime import datetime
from GeminiCurator import Curator, is_within_schedule

def main(args=None):
    now = datetime.now()
    start_time = now.replace(hour=00, minute=00, second=0, microsecond=0)
    end_time = now.replace(hour=23, minute=59, second=0, microsecond=0)

    CuratorMonitor = Curator(api_key=args.api_key, 
                             save_images_folder= args.save_images_folder, 
                             save_texts_folder = args.save_texts_folder,
                             start_time=start_time, 
                             end_time=end_time,
                             )
    while True:
        if is_within_schedule(start_time, end_time):
            try:
                CuratorMonitor.run_exhibition()  # 執行策展
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >>> GeminiCurator 開始執行")
            except Exception as e:
                print("\n" + "=" * 60)
                print("[ERROR] GeminiCurator 崩潰了，錯誤訊息：")
                traceback.print_exc()  # 印出詳細錯誤
                print("=" * 60)
                print(">>> 5 秒後重啟 GeminiCurator...\n")
                time.sleep(5)
        else:
            time.sleep(60)  # 休息 60 秒再檢查一次

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini Audience Monitor")
    parser.add_argument("--api_key", type=str, default="AIzaSyDgPvBN0glOm1v7OvXXDZC2rhKQEK6VyWc", help="with your actual **Google Gemini API key**")
    parser.add_argument("--save_images_folder", type=str, default="GeneratedImages", help="your GeneratedImages folder")
    parser.add_argument("--save_texts_folder", type=str, default="GeneratedTexts", help="your GeneratedTexts folder")
    args = parser.parse_args()

    print("===== Gemini Curator Monitor 啟動 =====")
    main(args)

