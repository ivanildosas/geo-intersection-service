// 1. Variáveis Globais
let mapInput, mapOutput;
let layerInputGroup, layerOutputGroup;
let layerOutput = null;


function init() {
    console.log("Iniciando...");
    
    const centroBrasil = [-15.78, -47.93];
    const zoomInicial = 4;

    // Inicializa objetos Leaflet
    mapInput = L.map('map-input').setView(centroBrasil, zoomInicial);
    mapOutput = L.map('map-output').setView(centroBrasil, zoomInicial);

    const tileLayerUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    const attribution = '© OpenStreetMap';

    L.tileLayer(tileLayerUrl, { attribution }).addTo(mapInput);
    L.tileLayer(tileLayerUrl, { attribution }).addTo(mapOutput);

    // Inicializa grupos de camadas
    layerInputGroup = L.layerGroup().addTo(mapInput);
    layerOutputGroup = L.layerGroup().addTo(mapOutput);

    setTimeout(() => {
        mapInput.invalidateSize();
        mapOutput.invalidateSize();
        carregarCamadasBase();
    }, 400);
}


async function carregarCamadasBase() {
    const badge = document.getElementById('status-badge');
    try {
        const res = await fetch('/api/inputs_geojson');
        if (!res.ok) throw new Error("Falha na API");
        
        const data = await res.json();
        layerInputGroup.clearLayers();

        Object.keys(data).forEach(key => {
            const geojsonLayer = L.geoJSON(data[key], {
                style: { color: '#3498db', weight: 2, fillOpacity: 0.2 }
            });
            layerInputGroup.addLayer(geojsonLayer);
        });

        const bounds = L.featureGroup(layerInputGroup.getLayers()).getBounds();
        if (bounds.isValid()) mapInput.fitBounds(bounds);

    } catch (err) {
        console.error("Erro ao carregar bases:", err);
        if (badge) badge.innerText = "❌ Erro ao carregar bases";
    }
}

document.body.addEventListener('atualizarMapa', async () => {
    console.log("Evento 'atualizarMapa' Iniciando carga do Mapa 2...");
    const badge = document.getElementById('status-badge');

    try {
        if (badge) badge.innerText = "Carregando geometrias...";

        const response = await fetch('/api/read_output_geojson'); 
        if (!response.ok) throw new Error("Erro ao buscar dados do mapa");
        
        const data = await response.json();

        if (layerOutput) {
            layerOutputGroup.clearLayers();
        }

        layerOutput = L.geoJSON(data, {
            style: {
                color: '#e74c3c', 
                weight: 3,
                fillOpacity: 0.4
            }
        }).addTo(layerOutputGroup);

        // Ajusta o zoom para enquadrar o resultado
        mapOutput.fitBounds(layerOutput.getBounds());

        if (badge) badge.innerText = "Mapa atualizado";

    } catch (err) {
        console.error("Erro ao renderizar mapa 2:", err);
        if (badge) badge.innerText = "Erro na renderização";
    }
});

document.addEventListener('DOMContentLoaded', init);