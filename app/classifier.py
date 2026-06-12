import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# ===== CONSTANTS =====
CLASSES    = ["inorganic", "organic"]
MODEL_PATH = "waste_model.pth"
IMAGE_SIZE = 224
NORM_MEAN  = [0.485, 0.456, 0.406]
NORM_STD   = [0.229, 0.224, 0.225]


def _build_transform():
    """DRY: single definition of image preprocessing pipeline."""
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(NORM_MEAN, NORM_STD),
    ])


def _load_model():
    """Single responsibility: load and return the trained model."""
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, len(CLASSES))
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    return model


# Module-level singletons — loaded once, reused everywhere (DRY + Open/Closed)
_model     = _load_model()
_transform = _build_transform()


def classify_image(file_bytes: bytes) -> dict:
    """
    Single responsibility: classify one image.
    Returns dict with result and confidence.
    Open/Closed: extend CLASSES without changing this function.
    """
    img    = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    tensor = _transform(img).unsqueeze(0)

    with torch.no_grad():
        output = _model(tensor)

    predicted  = output.argmax(1).item()
    confidence = torch.softmax(output, dim=1).max().item() * 100

    return {
        "result":     CLASSES[predicted],
        "confidence": f"{confidence:.1f}%",
    }
