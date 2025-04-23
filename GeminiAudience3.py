from PIL import Image
from google import genai
from datetime import datetime
import os
import time

client = genai.Client(api_key="AIzaSyDgPvBN0glOm1v7OvXXDZC2rhKQEK6VyWc")

# ---------- 找出最新圖片 ----------
def get_latest_image(folder="GeneratedImages"):
    os.makedirs(folder, exist_ok=True)
    image_files = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not image_files:
        raise FileNotFoundError("⚠️ 找不到圖片檔案，請先生成圖片")
    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
    return os.path.join(folder, image_files[0])

# ---------- 檢查是否已經評論過 ----------
def has_already_commented(image_path, filename="audience_feedback3.txt"):
    if not os.path.exists(filename):
        return False
    image_name = os.path.basename(image_path)
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
        return image_name in content

# ---------- 儲存觀眾回應 ----------
def save_audience_response(response_text, image_path, filename="audience_feedback3.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    image_name = os.path.basename(image_path)
    formatted = (
        f"\n{'-'*60}\n"
        f"🖼️ 圖片：{image_name}\n"
        f"🕒 時間：{timestamp}\n\n"
        f"{response_text.strip()}\n"
        f"{'-'*60}\n"
    )
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted)
    print(f"✅ 回應已儲存到 {filename}")

# ---------- 單次評論流程 ----------
def audience_comment_once():
    image_path = get_latest_image()

    if has_already_commented(image_path):
        print(f"⚠️ 已對圖片 {os.path.basename(image_path)} 評論過，跳過本輪。")
        return

    image = Image.open(image_path)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            image,
            "As an AI audience, how is your feeling when you look at this work?"
        ]
    )

    response_text = response.text.strip()
    print("🎤 AI 觀眾回應：\n", response_text)
    save_audience_response(response_text, image_path)
    return response_text

# ---------- 主程式 ----------
def main():
    while True:
        print("\n👁️ Audience 正在觀看最新作品並留下回饋...")
        audience_comment_once()
        time.sleep(5)  # 等待 5 秒再執行下一輪

if __name__ == "__main__":
    main()
