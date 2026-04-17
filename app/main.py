# -*- coding: UTF-8 -*-

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import app.constants as ct

app = FastAPI(
    title="Geo Intersection Service",
    description="Serviço que interseciona dados geoespaciais e retorna o GeoJSON com atributos atualizados",
    version="1.0.0"
)


@app.get("/")
def read_root():
    return {
        "status": "Online",
        "message": "Service running."
    }


@app.get("/api/geojson")
def get_geojson():
    try:
        file_path = Path(ct.SAMPLE_GEOJSON_PATH)

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Arquivo não encontrado: {ct.SAMPLE_GEOJSON_PATH}"
            )

        return FileResponse(
            path=file_path,
            media_type='application/json',
            filename=ct.SAMPLE_GEOJSON_PATH
        )
    except Exception as e:
        print(f'Erro: {e}')
