# Geo Intersection Service
Serviço de processamento espacial com GDAL/OGR para interseção de dados vetoriais. Processa e armazena resultados em SHAPEFILE, CSV e GeoJSON, e entrega o resultado GeoJSON via endpoint FastAPI, utilizando Docker para garantir o isolamento das bibliotecas geoespaciais.

## Tecnologias e versões
- **Python:** 3.12.3
- **FastAPI:** 0.115.6
- **Uvicorn:** 0.34.0
- **GDAL:** 3.10.1
- **PyProj:** 3.7.2
- **Shapely:** 2.1.2

## Estrutura de Arquivos
- `/app`: Código fonte
- `/files`: Armazenamento de arquivos (shapefiles, csv, geojson)
- `/tests`: Scripts de validação

## Como rodar
```bash
docker-compose up
```

##  Endpoints
| Rota | Método | Descrição |
| :--- | :--- | :--- |
| `/` | `GET` | **Server Status:** Verifica se o servidor está online e operacional. |
| `/api/geojson` | `GET` | **Download:** Retorna o GeoJSON dos dados resultantes da intersecção dos arquivos shapefiles. |

> **OBS:** Ao rodar em ambiente local, acesse `http://localhost:8000/docs` para visualizar a documentação interativa (Swagger UI) e testar os endpoints diretamente pelo navegador.
