
# 🌐 Gemini AI Curator & Audience System  
### *An Interactive Exhibition Between AI Curator and AI Audience*

## 🖼️ About This Project
This project creates a **curatorial loop** between an AI curator and AI audiences.  
The curator generates:
- 📝 A curatorial statement.
- 🖼️ A seamless triptych-style image (three connected images with captions).  

The audiences then:
- 👁️ Read the latest generated artwork.
- 💬 Respond with emotional feedback based on what they see.

The interaction continues in a loop:  
🧑‍🎨 Curator → 🎨 Exhibition → 👀 Audience Response → Repeat.

---

## 📂 Project Structure
```
GeminiProject/
├── GeneratedImages/                 # Auto-saved generated images
├── GeneratedTexts/                  # Auto-saved generated texts
  ├── exhibition_statement.txt         # Saved curator statements
  ├── generated_image_response.txt     # Captions of each generated image
  ├── audience_feedback1.txt           # Feedback from Audience 1
  ├── audience_feedback2.txt           # Feedback from Audience 2
  ├── audience_feedback3.txt           # Feedback from Audience 3
├── GeminiCurator.py                 # Curator: statement & image generation
├── CuratorMonitor.py                
├── Audience.py                      # Audience: feedback generation
├── AudienceMonitor1.py              
├── AudienceMonitor2.py              
├── AudienceMonitor3.py              
├── BlackFlicker.ps1                 # Black screen flicker effect
├── README.md                        # Project documentation
```

---

## 🚀 How to Use

### 1️⃣ Setup Environment
```bash
conda create -n gemini_env python=3.10
conda activate gemini_env
pip install google-genai pillow matplotlib
```

---

### 2️⃣ Add Your API Key  
In both `GeminiCurator.py` and `GeminiAudience.py`, replace:
```python
client = genai.Client(api_key="YOUR_API_KEY_HERE")
```
with your actual **Google Gemini API key**.

---

### 3️⃣ Running the Curator  
This will generate:
- A curatorial statement.
- A triptych artwork (3 connected images).
- Captions under each image.

```bash
python CuratorMonitor.py --api_key XXXXXXXX --save_images_folder GeneratedImages --save_texts_folder GeneratedTexts
```

---

### 4️⃣ Running the Audience  
This will:
- Detect the latest generated image.
- Respond with audience feedback (written emotional reaction).

```bash
python AudienceMonitor1.py --audience <number_tag of the audience> --description <Describe the personality traits of the AI audience.>
```
```bash
python AudienceMonitor2.py --audience <number_tag of the audience> --description <Describe the personality traits of the AI audience.>
```
```bash
python AudienceMonitor3.py --audience <number_tag of the audience> --description <Describe the personality traits of the AI audience.>
```

You can open:
- **One terminal for curator (looped).**
- **One or multiple terminals for an audience (looped independently).**

> ⚠️ Audience scripts check if the image was already commented on to avoid duplicate feedback.


## 🌟 Flicker Black Screen Effect (BlackFlicker.ps1)

To enhance the presentation experience, the project includes a Flicker Black Screen feature:
-Randomly flashes black screens across multiple monitors.

### 🖥️ How to Use Flicker
Navigate to your project folder:
```bash
cd path\to\your\project
```
Allow script execution if blocked:
```bash
Set-ExecutionPolicy RemoteSigned -Scope Process
```
Run the flicker script:
```bash
.\BlackFlicker.ps1
```
⚠️ Requires at least two monitors to function properly.
