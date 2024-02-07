import os
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, Body, Path, Query, HTTPException, status
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Annotated, Optional, List, Dict
from datetime import timedelta

from config.database import Session, engine, Base
from models.movie import Movie as MovieModel
from jwt_manager import Token, User, get_current_active_user, create_access_token, authenticate_user, fake_users_db, JWTBearer

from sqlalchemy import select, delete

load_dotenv()

movies_list = [
    {
        'id': 1,
        'title': 'The Matrix',
        'year': 1999,
        'category':'action,science fiction'
    },
    {
        'id': 2,
        'title': 'Fight Club',
        'year': 1999,
        'category':'action'
    },
    {
        'id': 3,
        'title': 'Star Wars Episode 1: The Phantom Menace',
        'year': 1999,
        'category':'adventure,science fiction'
    },
]

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=100)
    overview: str = Field(min_length=5, max_length=50)
    year: int = Field(le=2024)
    rating: float = Field(ge=0, le=10)
    category: str = Field(min_length=3, max_length=50)

    # esto declara los valores default de la clase movie
    class Config:
        schema_extra = {
            "id" : 1,
            "title": "Mi pelicula",
            "overview": "Descripcion de la pelicula",
            "rating": 8,
            "year": 2022,
            "category": "Adventure"
        }

app = FastAPI()
app.title = 'my-api-boss'
app.version = '0.2b'

Base.metadata.create_all(bind=engine)

@app.get('/', tags=['home'])
def message():
    return HTMLResponse(
        '''
        <h1>Hello World!</h1>
        <p>This is a HTMLResponse from python</p>
        '''
    )
@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200) # ,dependencies=[Depends(JWTBearer())] 
async def movies_list() -> List[Movie]:
    try:
        db = Session()
        
        movie_list = db.execute(select(MovieModel)).fetchall()
        result = jsonable_encoder([movie_tuple[0] for movie_tuple in movie_list])
        
        return JSONResponse(status_code=200, content=result)
    except:
        return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})

@app.get('/movies/{id}', tags=['movie-detail'], response_model=Movie, status_code=200)
def movieDetail(status_code=200, id: int = Path(ge=1, le=2000)) -> Movie:
    try:
        db = Session()
        movie = db.execute(select(MovieModel).where(MovieModel.id == id))

        for row in movie:
            return JSONResponse(content=jsonable_encoder(row[0]))

        
    except:
        return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})
         
@app.get('/movies/', tags=['movies'], response_model=List[Movie])
def movieCategory(category: str = Query(min_length=3, max_length=100)) -> List[Movie]:
    try:
        db = Session()

        tags = category.split(" ")
        list_result = list()
        for tag in tags:
            tag_result =list()
            movie_list = db.execute(select(MovieModel).where(MovieModel.category.like(f"%{tag}%")))
            result = jsonable_encoder([movie_tuple[0] for movie_tuple in movie_list])

            for data in result:
                if any(data['title'] == item['title'] for item in list_result):
                    continue
                tag_result.append(data)

            list_result.extend(tag_result)
        
        return JSONResponse(status_code=200, content=list_result)
    except:
        return JSONResponse(status_code=400, content={"message":"No hay resultados"})

@app.post('/movies', tags=['movies'], status_code=201)
def createMovie(movie: Movie):
    try:
        db = Session()
        new_movie = MovieModel(**movie.model_dump())
        db.add(new_movie)
        db.commit()
        
        return JSONResponse(status_code=201, content={"message":"Pelicula creada"})
    except:
        return JSONResponse(status_code=500, content={"message":"Fallo del servidor"})

@app.put('/movies/{id}', tags=['movies'], response_model=Dict, status_code=200)
async def updateMovie(id: int, movie: Movie) -> Dict:
    try:
        db = Session()
        result = db.scalar(select(MovieModel).where(MovieModel.id == id))
        
        for item in jsonable_encoder(result).keys():
            setattr(result, item, getattr(movie, item))
        db.commit()
            
        return JSONResponse(status_code=201, content={"message":"Pelicula Modificada"})
    except:
        return JSONResponse(status_code=500, content={"message":"Fallo del servidor"})

    
@app.delete('/movies/{id}', tags=['movies'], response_model=Dict, status_code=200)
def deleteMovie(id: int) -> Dict:
        try:
            db = Session()
            db.execute(delete(MovieModel).where(MovieModel.id==id))
            db.commit()

            return JSONResponse(status_code=200, content={"message":"Pelicula eliminada"})
        except: 
            return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})
        

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]