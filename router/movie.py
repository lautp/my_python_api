
from service.Movie import MovieService
from fastapi.routing import APIRouter
from fastapi import Path, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from typing import List, Dict

from middleware.JWT_Bearer import JWTBearer

from config.database import Session
from model.movie import Movie as MovieModel

from schema.Movie import Movie

from sqlalchemy import select, delete

MovieRouter = APIRouter()

@MovieRouter.get('/movies', tags=['Movies'], response_model=List[Movie], status_code=200) # , dependencies=[Depends(JWTBearer())] 
async def movies_list() -> List[Movie]:
    result = MovieService().getMovies()
    return result

@MovieRouter.get('/movies/{id}', tags=['Movies'], response_model=Movie, status_code=200)
def movieDetail(status_code=200, id: int = Path(ge=1, le=2000)) -> Movie:
    result = MovieService().getMovie(id)
    return result
         
@MovieRouter.get('/movies/', tags=['Movies'], response_model=List[Movie])
def movieCategory(category: str = Query(min_length=3, max_length=100)) -> List[Movie]:
    result = MovieService().getByCategory(category)
    return result

@MovieRouter.post('/movies', tags=['Movies'], status_code=201)
def createMovie(movie: Movie):
    result = MovieService().createMovie(movie)
    return result

@MovieRouter.put('/movies/{id}', tags=['Movies'], response_model=Dict, status_code=200)
async def updateMovie(id: int, movie: Movie) -> Dict:
    result = MovieService().updateMovie(id, movie)
    return result

    
@MovieRouter.delete('/movies/{id}', tags=['Movies'], response_model=Dict, status_code=200)
def deleteMovie(id: int) -> Dict:
    result = MovieService().deleteMovie(id)
    return result