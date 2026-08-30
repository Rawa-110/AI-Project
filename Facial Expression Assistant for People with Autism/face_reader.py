import cv2
from deepface import DeepFace
from gtts import gTTS
import pygame
import os

# تحديد المسار الكامل للملف haarcascade
face_cascade = cv2.CascadeClassifier('C:/Users/روان/Documents/Facial Expression Assistant for People with Autism/haarcascade_frontalface_default.xml')

# التهيئة للصوت
pygame.mixer.init()

# فتح الكاميرا
cam = cv2.VideoCapture(0)
print("جاري التقاط الصورة...")
ret, frame = cam.read()
img_path = "face.jpg"
cv2.imwrite(img_path, frame)
cam.release()
cv2.destroyAllWindows()
# تحليل التعابير
print("جاري تحليل المشاعر...")
result = DeepFace.analyze(img_path=img_path, actions=['emotion'], enforce_detection=False)
emotion = result[0]['dominant_emotion']
print(f"التعبير المسيطر: {emotion}")

# الترجمة إلى عربي مبسط
translations = {
    "happy": "سعيد",
    "sad": "حزين",
    "angry": "غاضب",
    "surprise": "مندهش",
    "neutral": "محايد",
    "fear": "خائف",
    "disgust": "منزعج"
}
arabic_emotion = translations.get(emotion, "غير معروف")

# توليد الصوت
text = f"الشخص يبدو {arabic_emotion}"
tts = gTTS(text=text, lang='ar')
tts.save("emotion.mp3")

# تشغيل الصوت
pygame.mixer.music.load("emotion.mp3")
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    continue
