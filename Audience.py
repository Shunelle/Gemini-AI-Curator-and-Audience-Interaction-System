from PIL import Image
from google import genai
from pathlib import Path
from datetime import datetime

class Audience:
    def __init__(self, api_key=None, folder="GeneratedImages", feedback_file_root="GeneratedTexts", num_audience=1, description="As an AI audience, how is your feeling when you look at this work?"):
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.folder = Path(folder)
        feedback_file = Path(feedback_file_root) / f"audience_feedback{num_audience}.txt"
        self.feedback_file = Path(feedback_file)
        self.folder.mkdir(parents=True, exist_ok=True)

        self.description = description

    def get_latest_image(self):
        images = sorted(
            self.folder.glob("*.[pj][np]g"),  # 支援 jpg, jpeg, png
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        if not images:
            raise FileNotFoundError("⚠️ 找不到圖片檔案，請先生成圖片")
        self.image_name = images[0].name
        return images[0]

    def has_commented(self):
        return self.feedback_file.exists() and self.image_name in self.feedback_file.read_text(encoding="utf-8")

    def save_response(self, response_text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = (
            f"\n{'-'*60}\n"
            f"🖼️ 圖片：{self.image_name}\n"
            f"🕒 時間：{timestamp}\n\n"
            f"{response_text.strip()}\n"
            f"{'-'*60}\n"
        )
        self.feedback_file.write_text(self.feedback_file.read_text(encoding="utf-8") + log if self.feedback_file.exists() else log, encoding="utf-8")
        print(f"✅ 回應已儲存到 {self.feedback_file}")

    def comment_once(self):
        image_path = self.get_latest_image()
        if self.has_commented():
            print(f"⚠️ 已對圖片 {self.image_name} 評論過，跳過本輪。")
            return

        # 轉換 image 為 byte
        image = Image.open(image_path)

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                image,
                self.description,
            ],
        )

        response_text = response.text.strip()
        print("🎤 AI 觀眾回應：\n", response_text)
        self.save_response(response_text)
        return response_text

if __name__ == "__main__":
    audience1 = Audience(api_key="AIzaSyDgPvBN0glOm1v7OvXXDZC2rhKQEK6VyWc", folder="GeneratedImages", feedback_file_root="GeneratedTexts", num_audience=3)
    audience1.comment_once()