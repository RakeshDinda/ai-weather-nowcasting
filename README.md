# AI-Driven Hyper-Local Early Warning System for Severe Weather Nowcasting

This project is a Smart India Hackathon submission designed to predict severe weather events locally and quickly. The goal is to provide early warnings for events like thunderstorms, cloudbursts, and floods using machine learning.

## Project Structure

This project follows a simple, scalable full-stack architecture:

*   **`backend/`**: Contains the FastAPI server code. `main.py` is the entry point.
*   **`data/`**: Used for storing datasets.
    *   **`raw/`**: Unprocessed data files.
    *   **`processed/`**: Cleaned and transformed data ready for model training.
*   **`frontend/`**: The user interface of the application (to be built here).
*   **`models/`**: Machine learning code. `model.py` contains the prediction logic.
*   **`utils/`**: Helper scripts and configuration files, such as `config.py`.

## Getting Started

1.  Navigate to the `backend/` directory.
2.  Run the FastAPI server (you will need to install `fastapi` and `uvicorn`):
    ```bash
    uvicorn main:app --reload
    ```
3.  Check the health endpoint at `http://127.0.0.1:8000/health`.
