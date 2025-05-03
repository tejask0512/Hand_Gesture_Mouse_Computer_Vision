# Hand Gesture Mouse Control Using Computer Vision

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.8+-orange.svg)
![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-0.9+-red.svg)

## Project Overview

This project implements a hand gesture-based mouse control system using computer vision techniques. The application allows users to control their computer mouse cursor through hand movements and gestures captured by a webcam, providing a touchless interaction experience.

## Features

- **Real-time Hand Tracking**: Accurate detection and tracking of hand landmarks
- **Gesture Recognition**: Identify different hand gestures for various mouse functions
- **Mouse Control**: Move cursor, perform clicks, scroll, and drag operations
- **Customizable Gestures**: Define custom gestures for specific actions
- **Low Latency**: Optimized for real-time performance with minimal delay
- **Accessibility**: Enables computer control without physical contact

## Demo

![Demo GIF](https://i.imgur.com/placeholder.gif)

## Supported Gestures

| Gesture | Action |
|---------|--------|
| Index finger pointing | Move cursor |
| Index + Middle finger extended | Right-click |
| Thumb + Index finger pinch | Left-click |
| Closed fist | Pause tracking |
| Three fingers extended | Scroll mode |
| Open palm | Drag and drop |

## Requirements

- Python 3.7+
- Webcam
- Good lighting conditions for optimal performance

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tejask0512/Hand_Gesture_Mouse_Computer_Vision.git
   cd Hand_Gesture_Mouse_Computer_Vision
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:

```bash
python main.py
```

### Command Line Arguments

```bash
python main.py --camera 0 --threshold 0.7 --smoothing 5
```

- `--camera`: Camera index (default: 0)
- `--threshold`: Confidence threshold for hand detection (default: 0.7)
- `--smoothing`: Cursor movement smoothing factor (default: 5)
- `--flip`: Flip the camera horizontally (add flag if needed)

## How It Works

### 1. Hand Detection and Tracking

The system uses MediaPipe's hand detection model to identify hands in the webcam feed. The model provides 21 landmarks for each detected hand, which are tracked in real-time.

### 2. Gesture Recognition

Custom algorithms analyze the spatial relationships between hand landmarks to recognize specific gestures. The system calculates distances between key points and angles between fingers to identify gesture patterns.

### 3. Mouse Control Mapping

Detected gestures are mapped to mouse operations:
- The tip of the index finger controls cursor movement
- Various finger combinations trigger clicks, scrolls, and other actions
- A smoothing algorithm ensures fluid cursor movement

### 4. Calibration System

The application includes an automatic calibration process that adapts to different users and lighting conditions, ensuring reliable performance across various environments.

## Project Structure

```
Hand_Gesture_Mouse_Computer_Vision/
├── src/
│   ├── hand_detector.py
│   ├── gesture_recognizer.py
│   ├── mouse_controller.py
│   └── utils.py
├── models/
│   └── hand_landmark_model.tflite
├── config/
│   └── settings.json
├── main.py
├── calibration.py
├── requirements.txt
└── README.md
```

## Performance Optimization

- Frame rate optimization for smooth operation
- Gesture detection confidence thresholds to prevent false positives
- Movement smoothing to eliminate jitter
- Region of interest processing to reduce computational load

## Troubleshooting

**Issue**: Hand detection is not working correctly
**Solution**: Ensure adequate lighting and a clean background

**Issue**: Cursor movement is too sensitive
**Solution**: Adjust the smoothing factor using the `--smoothing` parameter

**Issue**: Gestures are not being recognized
**Solution**: Run the calibration script and follow the on-screen instructions

## Future Improvements

- Additional gesture support for more complex operations
- Machine learning-based gesture customization
- Support for two-handed operations
- Integration with specific applications like presentation software
- Optimized algorithms for improved performance on low-end hardware

## Technical Details

- Hand landmark detection using MediaPipe's hand tracking model
- Gesture classification based on landmark spatial relationships
- Kalman filtering for smooth cursor movement
- PyAutoGUI for system-level mouse control
- OpenCV for image processing and visualization

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MediaPipe team for their hand tracking model
- OpenCV community for computer vision tools
- PyAutoGUI developers for mouse control capabilities

## Contact

Tejas Kamble - [tejaskamble.com](https://tejaskamble.com)

Project Link: [https://github.com/tejask0512/Hand_Gesture_Mouse_Computer_Vision](https://github.com/tejask0512/Hand_Gesture_Mouse_Computer_Vision)
