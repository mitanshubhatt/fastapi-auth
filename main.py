import uvicorn

def main():
    uvicorn.run(
        app="app.server:app",
        host="localhost",
        port=8000
    )


if __name__ == "__main__":
    main()