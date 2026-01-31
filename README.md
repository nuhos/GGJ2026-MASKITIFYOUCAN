{ MASK IT IF YOU CAN 🎭 }
A Real-Time AI-Powered Facial Expression Challenge.
it's an interactive game built using Computer Vision and Deep Learning.
The core concept challenges players to mirror specific facial expressions (Masks) displayed on the screen. By utilizing high-fidelity facial tracking,
the game bridges the gap between human emotion and machine perception.
_____________________
Key Features:

- High-Precision Tracking: Powered by the MediaPipe Face Landmarker model, tracking 52 unique facial movements (Blendshapes) in real-time.
- Intelligent Calibration: A neutral-state calibration system that adapts the AI sensitivity to the user's specific facial structure and environment lighting.
- Dynamic HUD: Features a real-time progress bar, live expression feedback, and an automated scoring system.
- Responsive UI: Includes hover-reactive buttons and smooth transitions between game states (Menu, Countdown, Playing, Game Over).
- Diverse Challenge Set: Detects 5 complex states: Smile, Sad, Surprised, Left Eye Blink (Wink), and Smiling with Eyes Closed.
_____________________
Tech Stack:
Python 3.x

- OpenCV: For real-time video stream processing and image manipulation.
- MediaPipe: For extracting high-level facial landmarks and blendshape scores.
- Pillow (PIL): To render high-quality text, emojis, and UI elements.
- NumPy: For calculating geometric distances between eyelids and lips.
_____________________
How to Play:

1- Launch: Click the "Start Game" button on the main menu.

2- Calibrate: Keep a neutral face for a few seconds to let the AI learn your "Baseline" expression.

3- The Challenge: A target mask will appear in the corner. Mimic that expression as fast as possible!

4- Score: You earn 10 points for every successful match before the timer runs out

______________________
Controls:
- Mouse Left Click	Interact with Menu / Start Game
- R Key	Reset Game / Return to Menu 
- Esc Key	/ Exit Application

______________________
Judge’s Setup Instructions
To ensure a smooth experience during the evaluation:

1- Keep all .png image files and the face_landmarker.task file in the same directory as the executable.
2- Run the Run_Game.bat file. This script automatically checks for and installs any missing dependencies.
3- If the batch file does not execute, you can launch the game directly via the terminal. Open your command prompt in the project folder and run: python Maskitifyoucan.py
or double click on the Maskitifyoucan.py file.
4- Python 3.10+ must be installed on the system.
5- A functional webcam is required.
   - For optimal AI performance, please ensure the user's face is well-lit and clearly visible to the camera.
______________________
Developed by NUHA SABER
nuha.os.866@gmail.com










