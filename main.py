import cv2
import os
import google.genai as genai
from dotenv import load_dotenv
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables. Please set it in a .env file.")
    print("You can copy .env.example to .env and insert your actual key.")
    exit(1)

client = genai.Client(api_key=api_key)

# The prompt assigned for the persona
PROMPT = (
    "Act as a friendly math teacher. Read the handwritten math problem in this image, "
    "state the problem you see, and then solve it step-by-step while explaining the logic."
)

def solve_math_problem(image_path):
    print("\nSending image to Gemini API...")
    try:
        # Load the image using PIL
        img = Image.open(image_path)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[PROMPT, img]
        )
        
        print("\n" + "="*50)
        print("🧑‍🏫 Teacher's Response:")
        print("="*50)
        print(response.text)
        print("="*50 + "\n")
    except Exception as e:
        print(f"\nError communicating with Gemini API: {e}")

def main():
    # Attempt to open the default webcam (usually index 0)
    # The cv2.CAP_DSHOW flag is sometimes helpful on Windows for faster startup
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Error: Could not access the webcam. Make sure another program is not using it.")
        return

    print("="*50)
    print("Welcome to Smart Chalkboard!")
    print("Controls:")
    print("  [SPACE] - Capture frame and solve math problem")
    print("  [Q]     - Quit the application")
    print("="*50)

    # We use a temporary file to save the captured frame before sending it
    temp_image_path = "temp_capture.jpg"

    while True:
        # Step 1: The Live Feed - Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame. Exiting...")
            break

        # Display the resulting frame
        cv2.imshow('Smart Chalkboard - Live Feed', frame)

        # Wait for user input (1 ms delay ensures smooth video feed)
        key = cv2.waitKey(1) & 0xFF

        # If 'q' is pressed, exit
        if key == ord('q'):
            print("Exiting...")
            break
        
        # Step 2: The Capture Trigger - If 'SPACE' is pressed, capture and process
        elif key == 32:  # 32 is the ASCII value for Space
            print("\nCapturing frame...")
            # Save the frame locally
            cv2.imwrite(temp_image_path, frame)
            
            # Step 3 & 4: Prompt Engineering & Cloud Inference
            solve_math_problem(temp_image_path)
            
            # Clean up the temporary image after processing
            if os.path.exists(temp_image_path):
                try:
                    os.remove(temp_image_path)
                except OSError:
                    pass
                
            print("Resuming live feed. Press [SPACE] to capture again or [Q] to quit.")

    # Clean up the camera resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
