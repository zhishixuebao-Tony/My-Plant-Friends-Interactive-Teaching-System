import uvicorn

if __name__ == "__main__":
    # 0.0.0.0 允许局域网平板访问
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)