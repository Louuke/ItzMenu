import uvicorn

if __name__ == '__main__':
    uvicorn.run('itzmenu_service.app:app', host='0.0.0.0', log_level='debug')
