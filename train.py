import torch
import torch.nn as nn
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader, random_split
import os

# ===== SETTINGS =====
DATA_DIR = "dataset"       # folder with your images
EPOCHS   = 10
BATCH    = 32
LR       = 0.001

# Classes — folder names must match exactly
CLASSES  = ["organic", "inorganic"]

# ===== DATA LOADING =====
transform_train = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

transform_val = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

dataset = datasets.ImageFolder(DATA_DIR, transform=transform_train)
val_size  = int(0.2 * len(dataset))
train_size = len(dataset) - val_size
train_ds, val_ds = random_split(dataset, [train_size, val_size])
val_ds.dataset.transform = transform_val

train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH)

print(f"Training: {train_size} images | Validation: {val_size} images")

# ===== MODEL =====
model = models.mobilenet_v2(weights="IMAGENET1K_V1")

# Freeze all layers except the last
for param in model.features.parameters():
    param.requires_grad = False

# Replace final layer for 2 classes (organic/inorganic)
model.classifier[1] = nn.Linear(model.last_channel, 2)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
print(f"Using: {device}")

# ===== TRAINING =====
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.classifier.parameters(), lr=LR)

best_acc = 0.0

for epoch in range(EPOCHS):
    # Train
    model.train()
    train_loss = 0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    # Validate
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = outputs.max(1)
            correct += (predicted == labels).sum().item()
            total   += labels.size(0)

    acc = 100 * correct / total
    print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {train_loss/len(train_loader):.3f} | Val Accuracy: {acc:.1f}%")

    # Save best model
    if acc > best_acc:
        best_acc = acc
        torch.save(model.state_dict(), "waste_model.pth")
        print(f"  --> Best model saved! ({acc:.1f}%)")

print(f"\nTraining done! Best accuracy: {best_acc:.1f}%")