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

class MovieService():
    def __init__(self) -> None:
        self.db = Session()

    def getMovies(self):
        try:
                       
            movie_list = self.db.execute(select(MovieModel)).fetchall()
            result = jsonable_encoder([movie_tuple[0] for movie_tuple in movie_list])
            
            return JSONResponse(status_code=200, content=result)
        except:
            return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})
    
    def getMovie(self, id):
        try:
            movie = self.db.execute(select(MovieModel).where(MovieModel.id == id))

            for row in movie:
                return JSONResponse(content=jsonable_encoder(row[0]))

            
        except:
            return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})
    
    def getByCategory(self, category):
        try:
            tags = category.split(" ")
            list_result = list()
            for tag in tags:
                tag_result =list()
                movie_list = self.db.execute(select(MovieModel).where(MovieModel.category.like(f"%{tag}%")))
                result = jsonable_encoder([movie_tuple[0] for movie_tuple in movie_list])

                for data in result:
                    if any(data['title'] == item['title'] for item in list_result):
                        continue
                    tag_result.append(data)

                list_result.extend(tag_result)
            
            return JSONResponse(status_code=200, content=list_result)
        except:
            return JSONResponse(status_code=400, content={"message":"No hay resultados"})

    def createMovie(self, movie):
        try:
            new_movie = MovieModel(**movie.model_dump())
            self.db.add(new_movie)
            self.db.commit()
            
            return JSONResponse(status_code=201, content={"message":"Pelicula creada"})
        except:
            return JSONResponse(status_code=500, content={"message":"Fallo del servidor"})
    
    def updateMovie(self, id, movie):
        try:
            db = Session()
            result = db.scalar(select(MovieModel).where(MovieModel.id == id))
            
            for item in jsonable_encoder(result).keys():
                setattr(result, item, getattr(movie, item))
            db.commit()
                
            return JSONResponse(status_code=201, content={"message":"Pelicula Modificada"})
        except:
            return JSONResponse(status_code=500, content={"message":"Fallo del servidor"})

    def deleteMovie(self, id):
        try:
            db = Session()
            db.execute(delete(MovieModel).where(MovieModel.id==id))
            db.commit()

            return JSONResponse(status_code=200, content={"message":"Pelicula eliminada"})
        except: 
            return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})

    