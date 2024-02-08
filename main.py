import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from config.database import engine, Base
from middleware.error_handler import ErrorHandler

from router.movie import MovieRouter
from router.auth import AuthRouter

load_dotenv()

app = FastAPI()
app.title = 'my-api-boss'
app.version = '0.2b'

app.add_middleware(ErrorHandler)
app.include_router(AuthRouter)
app.include_router(MovieRouter)

Base.metadata.create_all(bind=engine)

@app.get('/', tags=['Home'])
def message():
    return HTMLResponse(
        '''
        <h1>Hello World!</h1>
        <p>This is a HTMLResponse from python</p>
        '''
    )

