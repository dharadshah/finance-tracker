import subprocess
import sys
import threading


def run_fastapi():
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--reload",
        "--port", "8000"
    ])


def run_gradio():
    subprocess.run([sys.executable, "app/ui/gradio_app.py"])


if __name__ == "__main__":
    fastapi_thread = threading.Thread(target=run_fastapi)
    gradio_thread  = threading.Thread(target=run_gradio)

    fastapi_thread.start()
    gradio_thread.start()

    fastapi_thread.join()
    gradio_thread.join()