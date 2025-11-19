import base64
with open("/Users/liang/Downloads/ScreenShot_2025-11-16_173004_542.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
print(b64)
