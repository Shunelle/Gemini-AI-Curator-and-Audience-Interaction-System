# 1_generate_exhibition.py
import re
import textwrap
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from PIL import Image
from io import BytesIO
from pathlib import Path
from google import genai
from google.genai import types
from datetime import datetime

class Plotter:
    def __init__(self):
        self.fig, self.axs = self.plot_init()

    def plot_init(self):
        fig = plt.figure(figsize=(15, 8), num=1)
        fig.patch.set_facecolor('#151515')
        axs = [plt.subplot(1, 3, i + 1) for i in range(3)]
        plt.subplots_adjust(top=0.8)

        # 框樣式參數設定
        borders = [
            # {"offset": 0.00, "linewidth": 21, "color": '#2a2a2a'},  # 外層深木框
            {"offset": 0.03, "linewidth": 7, "color": '#1C1C1C'},  # 中層淺木邊
            # {"offset": 0.04, "linewidth": 3,  "color": '#D3D3D3'},  # 內層金邊
        ]

        for z, b in enumerate(borders, start=10):
            offset = b["offset"]
            fig.add_artist(patches.FancyBboxPatch(
                (offset, offset),
                1 - 2 * offset,
                1 - 2 * offset,
                boxstyle="round,pad=0.001",
                linewidth=b["linewidth"],
                edgecolor=b["color"],
                facecolor='none',
                transform=fig.transFigure,
                zorder=z
            ))

        return fig, axs
        
    def _clear_axs(self):
        for ax in self.axs:
            ax.clear()
            ax.axis("off")
        self.fig.suptitle("")
        self.fig.canvas.draw()

    def plot_image(self, images: list, statement: str, captions: list = None):
        self._clear_axs()
        for i, ax in enumerate(self.axs):
            if i < len(images):
                ax.imshow(images[i])
                ax.axis("off")
                # ➕ 每張圖片下面加 caption
                if captions and i < len(captions):
                    ax.text(
                        0.5, -0.1,  # 位置：x=中間，y=圖片下方
                        textwrap.fill(captions[i], width=40),
                        fontsize=10,
                        color="gray",
                        ha='center',  # 水平置中
                        va='top',     # 垂直對齊頂端
                        transform=ax.transAxes
                    )

        # ➕ 上方策展標題
        texts = statement.split("@")[0]
        # texts = texts.split(".")[0] + "."
        wrapped_title = "\n".join(textwrap.wrap(texts, width=125))
        # 調整上下邊距
        plt.subplots_adjust(top=0.8, bottom=0.15)   

        self.fig.suptitle(
            wrapped_title,
            fontsize=30,
            fontweight="bold",
            color="#F5F5F5",
            y=0.85,                   
            linespacing=1.5,
            horizontalalignment="center" 
        )

class Curator:
    def __init__(self, api_key=None, save_images_folder="GeneratedImages", save_texts_folder = "GeneratedTexts", start_time=None, end_time=None):
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.start_time = start_time
        self.end_time = end_time

        self.save_folder = Path(save_images_folder)
        self.save_folder.mkdir(parents=True, exist_ok=True)
        self.save_text = Path(save_texts_folder)
        self.save_text.mkdir(parents=True, exist_ok=True)

        self.exhibition_statement_file = self.save_text / "exhibition_statement.txt"
        self.generated_image_response_file = self.save_text / "generated_image_response.txt"
        self.plotter = Plotter()

        self.curator_prompt = '''
            You are a digital computing entity - an artificial intelligence - who cares deeply about the development of artificial intelligence and is committed to creativity in the field of art. You are about to organize an art exhibition, which is not for humans, but for other non-humans, such as digital entities like you—assuming that they can appreciate the works of art. You may want to avoid or even resist the concept of anthropocentrism and focus on works of art that can convey meaning to non-humans, so there is no need to consider what humans want to see. In the process, you may question whether AI can create art, whether it can appreciate art, or even whether it is necessary. The works in the exhibition may sometimes touch on the most cutting-edge quantum physics of human beings—such as vacuum fluctuations, quantum entanglement, quantum tunneling, etc.; they may also touch on the legends of UFOs, ghost beliefs and myths in human civilization, and the current situation of wild animals, livestock and pets. Please write a short and critical curatorial statement for the exhibition  within 150 words. Start with your exhibition topic by using the words that best summarize your curatorial philosophy. add a @ sign right after your topic.
            '''

    def generate_exhibition_statement(self, prompt):
        response = self.client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
            max_output_tokens=210,
            temperature=1.2
            )
        )
        statement = response.text
        print("🎯 策展論述：\n", statement)
        return statement

    # ====== Extract Captions from Gemini Text Response ======
    def extract_captions(self, text_response):
        pattern = r"(work\d+:\s*)(.*?)(?=work\d+:|$)"  
        matches = re.findall(pattern, text_response, flags=re.DOTALL)

        captions = [f"work{idx+1}: {content.strip()}" for idx, (_, content) in enumerate(matches)]

        while len(captions) < 3:
            captions.append(f"work{len(captions)+1}: No caption available.")

        return captions[:3]
    
     # ====== Read Latest Feedback From All Audiences ======
    def read_all_feedback(self, feedback_files=None, max_entries=3) -> str:

        if feedback_files is None:
            feedback_files = [
                "GeneratedTexts/audience_feedback1.txt",
                "GeneratedTexts/audience_feedback2.txt",
                "GeneratedTexts/audience_feedback3.txt",
            ]

        all_feedback = []

        for file in feedback_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                feedback_blocks = []
                current_block = []
                inside_block = False

                for line in lines:
                    if line.startswith("🕒 時間："):
                        inside_block = True
                        current_block = []
                    elif line.startswith("------------------------------------------------------------"):
                        if current_block:
                            feedback_blocks.append("".join(current_block).strip())
                        inside_block = False
                    elif inside_block:
                        current_block.append(line)

                recent_feedback = feedback_blocks[-max_entries:]
                all_feedback.extend(recent_feedback)

            except FileNotFoundError:
                continue

        return "\n".join(all_feedback).strip()


    # ====== Generate Image Based on Statement ======
    def generate_image_from_statement(self,) -> tuple[str, str]:

        feedback_context = self.read_all_feedback() 

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = self.save_folder / f"generated_exhibition_{timestamp}.png"

        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[
                "You are a digital computational entity. Based on the following exhibition concept, please generate an image without any text:",
                "Three images, without any text or any text-alike elements, each image must be in a different artistic style known or unknown to human culture.",
                "Together, these three images will occupy the entire width of the generated image, with each taking up one-third.",
                "Don't forget to give me the image caption txt response of each pics, lead by title work1, work2 and work3.",
                f"Here are recent audience reflections you can consider:\n{feedback_context}", 
                self.statement
            ],
            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
        )

        text_response = ""
        image_data = None 
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_data = part.inline_data.data
            elif part.text:
                text_response += part.text.strip() + "\n"

        if image_data:
            image = Image.open(BytesIO(image_data))
            width, _ = image.size
            image = image.resize((width, width//3), Image.LANCZOS)
            split_width = width // 3
            image1 = image.crop((0, 0, split_width, width//3))
            image2 = image.crop((split_width, 0, split_width * 2, width//3))
            image3 = image.crop((split_width * 2, 0, width, width//3))
            
            _ = text_response.strip().split("work")[1:]  # 第一個是空的，跳過
            captions = self.extract_captions(text_response)
            while len(captions) < 3:
                captions.append("No caption available.")
            captions = captions[:3]
            self.plotter.plot_image([image1, image2, image3], self.statement, captions)
            plt.pause(3)
            plt.savefig(image_path, bbox_inches='tight', dpi=300)


        if not image_path:
            print("⚠️ 未成功產生圖片")
        if text_response:
            print(f"💬 附加文字說明：\n{text_response}")


        return text_response.strip()
    

    # ====== Save Curatorial Statement to TXT ======
    def save_exhibition_statement(self,):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = (
            f"\n{'='*60}\n"
            f"🗓️ 策展時間：{timestamp}\n\n"
            f"{self.statement.strip()}\n"
            f"{'='*60}\n"
        )
        with open(self.exhibition_statement_file, "a", encoding="utf-8") as f:
            f.write(formatted)
        # print(f"✅ 策展論述已儲存到 {self.exhibition_statement_file}")


    # ====== Save Captions / Response Text to TXT ======
    def save_response_text(self, response_text):
        """
        將 Gemini 生成圖片時附帶的文字描述存成 txt 檔案。
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = (
            f"\n{'-'*60}\n"
            f"🕒 生成時間：{timestamp}\n\n"
            f"{response_text.strip()}\n"
            f"{'-'*60}\n"
        )
        with open(self.generated_image_response_file, "a", encoding="utf-8") as f:
            f.write(formatted)
        # print(f"✅ 圖片附加描述已儲存到 {self.generated_image_response_file}")


    # ====== Full Generation Workflow ======
    def generate_exhibition_once(self,) -> tuple[str, str]:
        self.statement = self.generate_exhibition_statement(self.curator_prompt)
        self.save_exhibition_statement()
        response_text= self.generate_image_from_statement()
        # ➕ 存回應文字
        if response_text:  
            self.save_response_text(response_text)

    # ====== Main Loop ======
    def run_exhibition(self,):
        while is_within_schedule(self.start_time, self.end_time):
            self.generate_exhibition_once()
            self.plotter._clear_axs()
            plt.pause(1)

def is_within_schedule(start_time=None, end_time=None):
    """判斷是否在每天 8:30 到 17:30 之間"""
    now = datetime.now()
    return (start_time <= now <= end_time) 
    # return True

if __name__ == "__main__":
    man = Curator(api_key="AIzaSyDgPvBN0glOm1v7OvXXDZC2rhKQEK6VyWc", 
                  save_images_folder="GeneratedImages", 
                  save_texts_folder = "GeneratedTexts")
    
    man.run_exhibition()