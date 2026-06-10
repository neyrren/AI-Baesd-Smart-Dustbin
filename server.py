from flask import Flask, request, jsonify
from torchvision import models, transforms
from PIL import Image
import torch, io, urllib.request, json

app = Flask(__name__)

# Load model
model = models.mobilenet_v2(weights="IMAGENET1K_V1")
model.eval()

# Load ImageNet labels
url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
labels = json.loads(urllib.request.urlopen(url).read())

# Organic keywords
ORGANIC = ['banana','apple','orange','broccoli','carrot','mushroom',
           'strawberry','lemon','pineapple','pizza','sandwich','egg',
           'bread','corn','garlic','cabbage','cauliflower','tomato']

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

@app.route('/classify', methods=['POST'])
def classify():
    file = request.files['image']
    img = Image.open(io.BytesIO(file.read())).convert('RGB')
    tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)

    idx = output.argmax().item()
    label = labels[idx].lower()
    result = "organic" if any(w in label for w in ORGANIC) else "inorganic"

    print(f"Detected: {label} --> {result}")
    return jsonify({"result": result, "label": label})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)