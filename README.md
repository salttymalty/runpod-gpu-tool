# RunPod GPU Control Tool

🚀 A streamlined command-line utility to start and connect to your RunPod GPU instance using a VPS.

## ✅ Features

- Auto-resumes paused pods
- Waits until GPU is ready
- Extracts IP and port automatically
- Works from VPS, deployable on-demand
- SSH key handling with volume-mounted secure storage

## 🔧 Requirements

- Python 3.10+
- `runpod` Python SDK
- RunPod API key and Pod ID
- SSH setup between VPS and pod

## 🚀 Getting Started

1. Clone the repo:
```bash
git clone https://github.com/salttymalty/runpod-gpu-tool.git
cd runpod-gpu-tool