from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/api/")
def api_test():
    return {"test": "success"}

handler = app