from pydantic import BaseModel, field_validator
import numpy as np

class MatrixModel(BaseModel):
    matrix: list[list[float]]

    @field_validator('matrix')
    @classmethod
    def check_square_and_positive(cls, v):
        arr = np.array(v)
        if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
            raise ValueError("Матрица должна быть квадратной (N x N)")
        if np.any(arr <= 0):
            raise ValueError("Все элементы матрицы должны быть > 0")
        return v