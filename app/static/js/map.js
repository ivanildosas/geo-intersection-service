// 1. Variáveis Globais
let mapInput, mapOutput;
let layerInputGroup, layerOutputGroup;


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


document.addEventListener('DOMContentLoaded', init);