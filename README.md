# Geo Intersection Service

Serviço de processamento espacial com GDAL/OGR que realiza o cálculo de interseção booleana de arquivos shapefiles, efetua o cálculo de média do atributo 'value' e cria novas bandas de metadados. O sistema calcula a área geodésica exata de interseção em metros quadrados e hectares, mitigando distorções de projeções planares.

Processa e armazena resultados em SHAPEFILE, CSV e GeoJSON, entregando os dados via endpoint FastAPI.

**Obs.1:** O processamento e o cálculo de área utilizam o modelo de referência Elipsoide GRS80 (SIRGAS 2000 / EPSG:4674), utilizando as Fórmulas de Karney para garantir paridade com o QGIS 4.0.1. Parâmetros podem ser alterados em `/app/constants.py`.

**Obs.2:** Os arquivos shapefiles devem estar na pasta `/files/shapefiles` e seus nomes inseridos no `/app/constants.py`.

**Obs.3:** Os shapefiles devem conter os atributos: `ID_GBA`, `Área (m²)`, `Área (ha)` e `value`.

## Tecnologias e versões
- **Python:** 3.12.3
- **FastAPI:** 0.115.6
- **Uvicorn:** 0.34.0
- **GDAL:** 3.10.1
- **PyProj:** 3.7.2
- **Shapely:** 2.1.2
- **Leaflet:** 1.9.4

## Estrutura de Arquivos (Padrão Application Factory)
- `/app`: Código fonte e controladores (`main.py`, `geo_controller.py`)
- `/app/static`: Assets estáticos do frontend (CSS, JS)
- `/app/templates`: Templates HTML (Jinja2)
- `/files`: Armazenamento dinâmico (shapefiles, resultados CSV e GeoJSON)
- `/tests`: Scripts de validação

## Como rodar
```bash
    docker-compose up --build
```
##  Endpoints
| Método | Endpoint | Descrição |
|:---|:---|:---|
| `GET`  | `/status`  | Server Status: Retorna o status do serviço em formato JSON. |
| `GET`  | `/api/output_geojson` | Rotina de interseção: Processa todos os arquivos em SHAPEFILE_PATH_LIST, gerando os arquivos de saída (.shp, .csv, .json) e retornando o resultado final em formato GeoJSON.|
| `GET`  | `/api/inputs_geojson` | Retorna uma lista de objetos contendo os nomes e os GeoJSONs dos arquivos em SHAPEFILE_PATH_LIST.|
| `GET`  | `/api/geojson_result` | Retorna estaticamente o arquivo com o resultado resultado da interseção já processado (output_media_bandas.json).|
| `GET`  | `/api/logs `          | Retorna os últimos 100 logs de processamento do serviço (fila circular) em formato JSON. |
| `POST` | `/api/map_intersect`  | Processa a interseção para uma lista específica de 'layers' e retorna uma tabela HTML formatada.|

##  Inteface
| URL 	  | Descrição |
|:--- |:--- |
| `/` 	  | Retorna o status do servidor e informações do SO renderizados em HTML via Jinja2. |
| `/docs` | Swagger: Documentação interativa para teste e validação dos endpoints da API. |
| `/map`  | Geo Preview: Dashboard interativo com dois mapas Leaflet sincronizados, tabelas de atributos formatadas em padrão ABNT com seção de logs para monitoramento. |

