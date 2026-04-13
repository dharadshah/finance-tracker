import subprocess
import sys
import threading
import time


def run_fastapi():
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--reload",
        "--port", "8000"
    ])


def run_gradio():
    time.sleep(2)
    subprocess.run(
        [sys.executable, "-m", "app.ui.main"],
        cwd = os.path.dirname(os.path.abspath(__file__))
    )


if __name__ == "__main__":
    import os

    fastapi_thread = threading.Thread(target=run_fastapi)
    gradio_thread  = threading.Thread(target=run_gradio)

    fastapi_thread.start()
    gradio_thread.start()

    fastapi_thread.join()
    gradio_thread.join()