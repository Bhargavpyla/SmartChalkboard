# The Smart Chalkboard (A Multimodal AI Math Solver)

## 1. Project Objective
The goal of this project is to build an interactive bridge between physical hardware and cloud-based Artificial Intelligence. The application acts as a real-time, intelligent tutor. It captures live video of handwritten mathematical equations through a standard webcam, processes the image using computer vision, and leverages a Large Language Model (LLM) to read, comprehend, and solve the equation step-by-step.

## 2. The Core Technologies (The Tech Stack)
To make this work, the project relies on three distinct technological pillars working together in perfect harmony:

- **The Hardware Interface (OpenCV)**: OpenCV is a powerful computer vision library. In this project, it acts as the "eyes." It interfaces directly with the computer's physical webcam hardware, translating the light hitting the camera lens into a digital matrix of pixels that Python can understand and save as an image file.
- **The Bridge (Python)**: Python acts as the central nervous system or the "digital mailroom." It controls the camera, listens for user input (like pressing a key to snap a photo), formats the image, and securely transmits the data over the internet.
- **The Brain (Google Gemini API)**: The Gemini API provides access to Google's massive AI servers. Specifically, it uses a Multimodal model. Unlike older AI that could only read text, a multimodal model can process text, images, and audio simultaneously.

## 3. Step-by-Step System Architecture (How it Works)
When the application is running, it follows a strict, logical assembly line:

- **Step 1: The Live Feed**: The Python script opens a continuous loop, commanding OpenCV to fetch a new frame from the webcam dozens of times per second. This creates a smooth, live video feed on the user's screen.
- **Step 2: The Capture Trigger**: The program actively listens for a specific keyboard event. When the user holds up their handwritten math problem and presses a designated key, the loop temporarily pauses. OpenCV isolates that exact single frame of video and saves it to the computer's local memory as a high-quality image file.
- **Step 3: Prompt Engineering**: Before sending the image to the AI, the script attaches a highly specific set of text instructions, known as a prompt. Instead of just asking "What is this?", the prompt assigns a persona and a rigid task: *"Act as a friendly math teacher. Read the handwritten math problem in this image, state the problem you see, and then solve it step-by-step while explaining the logic."*
- **Step 4: Cloud Inference**: Python securely packages the image and the text prompt and sends them over the internet to the Gemini API. This is a classic example of Client-Server Architecture. The local computer (the client) requests a heavy computational favor from Google's supercomputers (the server).
- **Step 5: The Output Reveal**: Within seconds, the Gemini server returns a structured text response. The Python script prints this response to the screen, revealing the step-by-step solution to the user's handwritten problem.

## 4. Key Artificial Intelligence Concepts Demonstrated
This project is an excellent demonstration of several major pillars of modern computer science:

- **Optical Character Recognition (OCR)**: This is the AI's ability to look at messy, human handwriting—which are essentially just random lines and curves—and mathematically map those shapes to known digital characters like a "7" or an "x".
- **LLM Reasoning**: Reading the numbers is not enough. The AI must understand the relationship between those numbers. It uses logical reasoning to recognize that the cross shape is a multiplication sign, apply the rules of arithmetic, and generate a factual conclusion.
- **Contextual Generation**: The AI doesn't just output a raw number like "16." Because of our prompt engineering, it contextualizes the answer into a polite, educational paragraph, demonstrating natural language generation.

## How to Run

1. Clone or download this project.
2. Install the necessary Python packages: `pip install -r requirements.txt`
3. Create a `.env` file based on `.env.example` and insert your Google Gemini API Key.
4. Run the script: `python main.py`
5. Show a math problem to your webcam and press **`SPACE`** to capture it. Press **`Q`** to exit the camera feed.
