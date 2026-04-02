import cv2
import os
import google.genai as genai
from dotenv import load_dotenv
from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.text import Text

# Initialize Rich console
console = Console()

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    console.print("[bold red]Error: GEMINI_API_KEY not found in environment variables.[/bold red]")
    console.print("Please set it in a .env file.")
    exit(1)

client = genai.Client(api_key=api_key)

# The prompt assigned for the persona
PROMPT = (
    "Act as a friendly math teacher. Read the handwritten math problem in this image, "
    "state the problem you see, and then solve it step-by-step while explaining the logic.\n\n"
    "CRITICAL FORMATTING RULES FOR TERMINAL:\n"
    "1. Do NOT use complex LaTeX (like $$ or \\frac). Many terminals cannot render them.\n"
    "2. Use clear ASCII math or simple Markdown. For example:\n"
    "   - Use ^ for exponents: x^2\n"
    "   - Use / for fractions: (x+1)/(x-1)\n"
    "   - Use d/dx for derivatives\n"
    "   - Use 'integral of ... dx' for integrals\n"
    "   - Use SQRT() for square roots\n"
    "3. Use **bold** for key terms and steps.\n"
    "4. Keep the explanation conversational and easy to read in a console window."
)

def solve_math_problem(image_path):
    console.print("\n[bold cyan]🔍 Sending image to Gemini AI...[/bold cyan]")
    try:
        # Load the image using PIL
        img = Image.open(image_path)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[PROMPT, img]
        )
        
        # Clean up any accidental LaTeX/MathJax delimiters if Gemini still uses them
        clean_text = response.text.replace("$$", "").replace("$", "")
        
        # Format the response using Markdown
        md = Markdown(clean_text)
        panel = Panel(
            md,
            title="[bold green]🧑‍🏫 Teacher's Response[/bold green]",
            subtitle="[italic white]Smart Chalkboard Assistant[/italic white]",
            border_style="bright_blue",
            padding=(1, 2)
        )
        console.print(panel)
        console.print("\n")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error communicating with Gemini API:[/bold red] {e}")

def main():
    # Attempt to open the default webcam
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        console.print("[bold red]Error: Could not access the webcam.[/bold red]")
        console.print("Make sure another program is not using it.")
        return

    # Welcome screen
    welcome_text = Text.from_markup(
        "Welcome to [bold magenta]Smart Chalkboard[/bold magenta]! 🎓\n\n"
        "Controls:\n"
        "  [reverse white] SPACE [/reverse white] - Capture and Solve\n"
        "  [reverse red]   Q   [/reverse red] - Quit Application"
    )
    console.print(Panel(welcome_text, border_style="cyan", padding=(1, 5)))

    temp_image_path = "temp_capture.jpg"

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                console.print("[bold red]Failed to grab frame. Exiting...[/bold red]")
                break

            cv2.imshow('Smart Chalkboard - Live Feed', frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                console.print("\n[bold yellow]👋 Exiting...[/bold yellow]")
                break
            
            elif key == 32:  # Space
                console.print("\n[bold green]📸 Capturing frame...[/bold green]")
                cv2.imwrite(temp_image_path, frame)
                
                # Process the problem
                solve_math_problem(temp_image_path)
                
                # Clean up
                if os.path.exists(temp_image_path):
                    try:
                        os.remove(temp_image_path)
                    except OSError:
                        pass
                    
                console.print("[italic blue]Feed resumed. Press [SPACE] to capture or [Q] to quit.[/italic blue]")

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
