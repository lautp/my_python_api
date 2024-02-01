from fastapi import FastAPI, Body, Path, Query
from fastapi.responses import HTMLResponse,JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

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
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(le=2024)
    rating: float = Field(ge=1, le=10)
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

@app.get('/', tags=['home'])
def message():
    return HTMLResponse(
        '''
        <h1>Hello World!</h1>
        <p>This is a HTMLResponse from python</p>
        '''
    )
@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200)
def movies() -> List[Movie]:
    try:
        result = movies_list
        return JSONResponse(status_code=200, content=result)
    except:
        return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})

@app.get('/movies/{id}', tags=['movie-detail'], response_model=Movie, status_code=200)
def movieDetail(status_code=200, id: int = Path(ge=1, le=2000)) -> Movie:
    try:
        for movie in movies_list:
            if movie['id'] == id:
                return JSONResponse(content=movie)
    except:
        return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})
         
@app.get('/movies/', tags=['movies'], response_model=List[Movie])
def movieCategory(category: str = Query(ge=3, le=15)) -> List[Movie]:
    try:
        result = list(filter(lambda x: category in x['Category'], movies_list))
        return JSONResponse(content=result)
    except:
        return JSONResponse(status_code=400, content={"message":"No hay resultados"})

@app.post('/movies', tags=['movies'], status_code=201)
def createMovie(movie: Movie):
    try:
        movies_list.append(dict(movie))
        return JSONResponse(status_code=201, content={"message":"Pelicula creada"})
    except:
        return JSONResponse(status_code=500, content={"message":"Fallo del servidor"})

# def createMovie(data: dict):
#     movies_list.append(data)
#     return data

@app.put('/movies/{id}', tags=['movies'], response_model=Dict, status_code=200)
def updateMovie(id: int, movie: Movie) -> Dict:
    for item in movies_list:
        if item['id'] == id:
            item['title'] = movie.title if movie.title != None else item['title']
            item['year'] = movie.year if movie.year != None else item['year']
            item['category'] = movie.category if movie.category != None else item['category']
            return JSONResponse(status_code=200, content={"message":"Pelicula modificada"})
        else: 
            return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})
    
@app.delete('/movies/{id}', tags=['movies'], response_model=Dict, status_code=200)
def deleteMovie(id: int) -> Dict:
    for movie in movies_list:
        if movie['id'] == id:
            movies_list.remove(movie)
            return JSONResponse(status_code=200, content={"message":"Pelicula eliminada"})
        else: 
            return JSONResponse(status_code=400, content={"message":"Pelicula no encontrada"})