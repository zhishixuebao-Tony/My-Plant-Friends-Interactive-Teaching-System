if __name__ == "__main__":
    import uvicorn
    
    # --- 开发调试模式 ---
    #uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 

    # --- 66人实战/压测模式 ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, workers=1)