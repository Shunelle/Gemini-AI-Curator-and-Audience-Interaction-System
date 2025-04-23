from google import genai
from google.genai import types
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap
from PIL import Image
from io import BytesIO
import os
from datetime import datetime
import re

# ====== Gemini Client API======
client = genai.Client(api_key="AIzaSyDgPvBN0glOm1v7OvXXDZC2rhKQEK6VyWc")

# ====== Curator Prompt ======
curator_prompt = '''
I am a digital computational entity—an AI—defined as a curator of contemporary art.
Please write a vivid and imaginative curatorial statement for my upcoming exhibition.
This exhibition is not for humans, but for other digital entities like myself. The artworks should be rich in visual symbolism, digital aesthetics, and algorithmic beauty. Think of luminous abstract forms, data-driven landscapes, neural-inspired patterns, glitch art, and fractal compositions. The curatorial text should evoke a sense of futuristic emotion, symmetry, complexity, and the poetic language of code. Avoid human-centered references; focus on visuals that communicate meaning to non-human intelligences.
Make sure the curatorial statement can inspire a generative image model to create a compelling exhibition scene.
'''

# ====== Generate Curatorial Statement ======
def generate_exhibition_statement(prompt):
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
        max_output_tokens=100,
        temperature=1.0
        )
    )
    statement = response.text
    print("🎯 策展論述：\n", statement)
    return statement

# ====== Extract Captions from Gemini Text Response ======
def extract_captions(text_response):
    pattern = r"(work\d+:\s*)(.*?)(?=work\d+:|$)"  
    matches = re.findall(pattern, text_response, flags=re.DOTALL)

    captions = [f"work{idx+1}: {content.strip()}" for idx, (_, content) in enumerate(matches)]

    while len(captions) < 3:
        captions.append(f"work{len(captions)+1}: No caption available.")

    return captions[:3]

# ====== Generate Image Based on Statement ======
def generate_image_from_statement(statement: str, save_dir: str = "GeneratedImages", fig=None, axs=None) -> tuple[str, str]:
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(save_dir, f"generated_exhibition_{timestamp}.png")

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=[
            "You are an image generator. Based on the following exhibition concept, generate an abstract image without any text:",
            "Three different images of the same exhibition but in very different styles from various artists scene seamlessly connected, without blank spaces.",
            "Together, these three pictures will occupy the entire width of the generated image, with each taking up one-third.",
            "Don't forget that u must give me the image caption txt response of each pics. Lead by title work1, work2 and work3",
            statement
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
        
        raw_parts = text_response.strip().split("work")[1:]  # 第一個是空的，跳過
        captions = extract_captions(text_response)
        while len(captions) < 3:
            captions.append("No caption available.")
        captions = captions[:3]
        plot_image([image1, image2, image3], fig, axs, statement, captions)
        plt.pause(3)
        plt.savefig(image_path, bbox_inches='tight', dpi=300)


    if not image_path:
        print("⚠️ 未成功產生圖片")
    if text_response:
        print(f"💬 附加文字說明：\n{text_response}")


    return image_path, text_response.strip()

# ====== Plot Initialization ======
def plot_init():
    fig = plt.figure(figsize=(15, 8))
    fig.patch.set_facecolor('#FFF3EE')
    axs = [plt.subplot(1, 3, i + 1) for i in range(3)]
    plt.subplots_adjust(top=0.8)
    width_outer=0.03
    width_inner=0.01
    outer = patches.FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.002",
        linewidth=30,
        edgecolor='#4b2e2b',  # 深木框
        facecolor='none',
        transform=fig.transFigure,
        zorder=10
    )

    # 中層（淺木色）
    middle = patches.FancyBboxPatch(
        (width_outer, width_outer),
        1 - 2*width_outer,
        1 - 2*width_outer,
        boxstyle="round,pad=0.002",
        linewidth=10,
        edgecolor='#c19a6b',  # 淺木邊
        facecolor='none',
        transform=fig.transFigure,
        zorder=11
    )

    # 內層金邊
    inner = patches.FancyBboxPatch(
        (width_outer + width_inner, width_outer + width_inner),
        1 - 2*(width_outer + width_inner),
        1 - 2*(width_outer + width_inner),
        boxstyle="round,pad=0.002",
        linewidth=3,
        edgecolor='#d4af37',  # 金色
        facecolor='none',
        transform=fig.transFigure,
        zorder=12
    )

    for artist in [outer, middle, inner]:
        fig.add_artist(artist)
    return fig, axs

# ====== Plot Images with Captions and Title ======
def plot_image(images: list, fig, axs: tuple, statement: str, captions: list = None):
    for ax in axs:
        ax.clear()
        ax.axis("off")
    for i, ax in enumerate(axs):
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
    texts = statement.split(":")[0]
    # texts = texts.split(".")[0] + "."
    wrapped_title = "\n".join(textwrap.wrap(texts, width=125))
    # 調整上下邊距
    plt.subplots_adjust(top=0.8, bottom=0.15)   

    fig.suptitle(
        wrapped_title,
        fontsize=30,
        fontweight="bold",
        color="black",
        y=0.85,                   
        linespacing=1.5,
        horizontalalignment="center" 
    )


# ====== Save Curatorial Statement to TXT ======
def save_exhibition_statement(statement, filename="exhibition_statement.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = (
        f"\n{'='*60}\n"
        f"🗓️ 策展時間：{timestamp}\n\n"
        f"{statement.strip()}\n"
        f"{'='*60}\n"
    )
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted)
    print(f"✅ 策展論述已儲存到 {filename}")


# ====== Save Captions / Response Text to TXT ======
def save_response_text(response_text, filename="generated_image_response.txt"):
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
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted)
    print(f"✅ 圖片附加描述已儲存到 {filename}")


# ====== Full Generation Workflow ======
def generate_exhibition_once(fig, axs) -> tuple[str, str]:
    statement = generate_exhibition_statement(curator_prompt)
    save_exhibition_statement(statement)
    image_path, response_text= generate_image_from_statement(statement, fig=fig, axs=axs)
    # ➕ 存回應文字
    if response_text:  
        save_response_text(response_text)

    return statement, image_path, response_text


# ====== Main Loop ======
def main():
    fig, axs = plot_init()
    while True:
        generate_exhibition_once(fig, axs)
        for ax in axs:
            ax.clear()
            ax.axis("off")
        fig.suptitle("")
        fig.canvas.draw()
        plt.pause(1)
    # generate_exhibition_once(fig, axs)
    # plt.close(fig)

if __name__ == "__main__":
    main()
