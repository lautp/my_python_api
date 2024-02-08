from pydantic import BaseModel, Field
from typing import Optional

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=1, max_length=100)
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