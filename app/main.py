# -*- coding: UTF-8 -*-

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from app.geo_controller import GeoController
import app.constants as ct

app = FastAPI(
    title="Geo Intersection Service",
    description="Serviço que interseciona dados geoespaciais e retorna o GeoJSON com atributos atualizados",
    version="1.0.0"
)

controller = GeoController()


@app.get("/")
def read_root():
    return {
        "status": "Online",
        "message": "Service running."
    }


@app.get("/api/geojson")
def get_geojson():
    try:
        result = controller.intersect_pipeline()
        if not result:
            raise HTTPException(status_code=500, detail="Erro ao processar geometrias.")

        # return JSONResponse(content=result)

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
        print(f'Erro no Endpoint: {e}')
        raise HTTPException(status_code=500, detail=str(e))
