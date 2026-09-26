import uvicorn

if __name__ == "__main__":
    print("Starting EduGenie Educational Assistant...")
    print("Open your browser at: http://localhost:8000\n")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
