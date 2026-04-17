# geo-intersection-service
Serviço de processamento espacial com GDAL/OGR para interseção de dados vetoriais. Processa e armazena resultados em SHAPEFILE, CSV e GeoJSON, e entrega o resultado GeoJSON via endpoint FastAPI, utilizando Docker para garantir o isolamento das bibliotecas geoespaciais.


## Tecnologias e Versões
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
docker build -t geo_intersection_service .
docker run geo_intersection_service
