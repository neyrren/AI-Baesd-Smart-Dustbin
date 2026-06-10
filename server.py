from flask import Flask, request, jsonify
from torchvision import models, transforms
from PIL import Image
import torch
import torch.nn as nn
import io

app = Flask(__name__)

# Load YOUR trained model
model = models.mobilenet_v2(weights=None)
model.classifier[1] = nn.Linear(model.last_channel, 2)
model.load_state_dict(torch.load("waste_model.pth", map_location="cpu"))
model.eval()

CLASSES = ["inorganic", "organic"]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

@app.route('/classify', methods=['POST'])
def classify():
    file = request.files['image']
    img  = Image.open(io.BytesIO(file.read())).convert('RGB')
    tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)

    predicted  = output.argmax(1).item()
    confidence = torch.softmax(output, dim=1).max().item() * 100
    result     = CLASSES[predicted]

    print(f"Result: {result.upper()} ({confidence:.1f}% confidence)")
    return jsonify({"result": result, "confidence": f"{confidence:.1f}%"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)