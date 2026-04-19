# -*- coding: UTF-8 -*-

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager
from os import path
import platform
from app.geo_controller import GeoController
import app.constants as ct

# Configura diretório de templates
templates = Jinja2Templates(directory=path.join(ct.APP_PATH, 'templates'))


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando api-geo...")
    app.state.controller = GeoController()
    yield
    print("Desligando api-geo...")


def configure_static(app: FastAPI):
    app.mount(
        '/static', 
        StaticFiles(
            directory=path.join(ct.APP_PATH, 'static')
        ), name='static'
    )


def create_status_template(request: Request):
    return templates.TemplateResponse(
        'status.html', {
            'request': request,
            'description': 'Serviço que intersecciona e atualiza atributos de dados geoespaciais e retorna o resultado em formato GeoJSON.',
            'os_info': 'Ubuntu 24.04.4 LTS',
            'python_version': platform.python_version(),
            'gdal_version': '3.10.1'
        })


def configure_routes(app: FastAPI):

    @app.get('/', response_class=HTMLResponse)
    @app.get('/status', response_class=HTMLResponse)
    def read_root(request: Request):
        return create_status_template(request)

    @app.get('/api/geojson')
    def get_geojson():
        try:
            geojson_data = app.state.controller.intersect_pipeline()
            if not geojson_data:
                raise HTTPException(status_code=500, detail="Erro ao processar geometrias.")

            return JSONResponse(content=geojson_data)

        except Exception as e:
            print(f'Erro no Endpoint: {e}')
            raise HTTPException(status_code=500, detail=str(e))


def create_app() -> FastAPI:
    app = FastAPI(
        title="Geo Intersection Service", 
        version="1.0.0",
        lifespan=lifespan
    )

    configure_static(app)
    configure_routes(app)

    return app


app = create_app()
