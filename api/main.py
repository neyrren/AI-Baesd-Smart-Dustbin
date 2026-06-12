from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
from torchvision import models, transforms
import torch.nn as nn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

classes = ["inorganic", "organic"]

model = models.mobilenet_v2(weights=None)
model.classifier[1] = nn.Linear(model.last_channel, 2)
model.load_state_dict(torch.load("waste_model.pth", map_location="cpu"))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = Image.open(file.file).convert("RGB")
    img_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(img_tensor)
        pred = output.argmax(1).item()
        confidence = torch.softmax(output, dim=1).max().item() * 100

    return {
        "prediction": classes[pred],
        "confidence": round(confidence, 1)
    }