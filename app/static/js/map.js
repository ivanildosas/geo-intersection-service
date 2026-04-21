// 1. Variáveis Globais
let mapInput, mapOutput;
let layerInputGroup, layerOutputGroup;
let layerOutput = null;
let logInterval;

const BASE_GEOM_COLOR = "#a08df2";
const SELECTED_GEOM_COLOR = "#ff0000";
const OUTPUT_GEOM_COLOR = "#ff0000";


let inputLayerNames = [];
let selectedLayers = new Set();

// Inicializa mapas
function init() {
    console.log("Iniciando...");
   
    const centroBrasil = [-15.78, -47.93];
    const zoomInicial = 4;

    // Inicializa objetos Leaflet
    mapInput = L.map('map-input').setView(centroBrasil, zoomInicial);
    mapOutput = L.map('map-output').setView(centroBrasil, zoomInicial);

    const tileLayerUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    //const tileLayerUrl = 'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png';
    
    const attribution = '© OpenStreetMap';

    L.tileLayer(tileLayerUrl, { attribution }).addTo(mapInput);
    L.tileLayer(tileLayerUrl, { attribution }).addTo(mapOutput);

    // Inicializa grupos de camadas
    layerInputGroup = L.layerGroup().addTo(mapInput);
    layerOutputGroup = L.layerGroup().addTo(mapOutput);

    configurarSincronizacao();

    setTimeout(() => {
        mapInput.invalidateSize();
        mapOutput.invalidateSize();
        carregarCamadasBase();
    }, 400);
}

// renderiza shapes de entrada
async function carregarCamadasBase() {
    try {
        iniciarMonitoramento();
        atualizarStatusBadge("⏳ Carregando camadas...", "processing");

        const response = await fetch('/api/inputs_geojson');
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            updateIntersectButton()
            throw new Error(errorData.detail || `Erro no endpoint /api/inputs_geojson: ${response.status}`);
        }

        const data = await response.json();

        inputLayerNames = Object.keys(data);
        let todasAsFeatures = [];

        if (inputLayerNames.length === 0) {
            atualizarStatusBadge("⚠️ Nenhuma camada de entrada encontrada.", "processing");
            return;
        }

        Object.keys(data).forEach(key => {
            if (data[key] && data[key].features) {
                data[key].features.forEach(f => {
                    f.properties.layerName = key; 
                });
                todasAsFeatures = todasAsFeatures.concat(data[key].features);

                const geojsonLayer = L.geoJSON(data[key], {
                    style: { color: BASE_GEOM_COLOR, weight: 2, fillOpacity: 0.2 }
                });
                
                geojsonLayer.options.layerName = key;
                layerInputGroup.addLayer(geojsonLayer);
            }
        });

        const bounds = L.featureGroup(layerInputGroup.getLayers()).getBounds();
        if (bounds.isValid()) mapInput.fitBounds(bounds);

        atualizarStatusBadge("✅ Camadas carregadas!", "success");
        renderAttributeTable(todasAsFeatures, 'table-input-container', true);

    } catch (err) {
        console.error("Erro ao carregar bases:", err);
        atualizarStatusBadge("❌ Erro ao carregar camadas de entrada!", "error");

        const btn = document.getElementById('btn-intersect');
        if (btn) btn.disabled = true;

    } finally {
        updateIntersectButton();
        pararMonitoramento(); 
        monitorarLogs();
    }
}

// atualiza mapa resultado
document.body.addEventListener('atualizarMapa', async () => {
    console.log("Evento 'atualizarMapa' Iniciando carga do Mapa 2...");
    const badge = document.getElementById('status-badge');

    try {
        iniciarMonitoramento();

        atualizarStatusBadge("⏳ Carregando geometrias...", "processing");

        const response = await fetch('/api/read_output_geojson'); 

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Erro no endpoint /api/read_output_geojson: ${response.status}`);
        }

        const data = await response.json();

        if (layerOutput) {
            mapOutput.removeLayer(layerOutput);
        }

        if (!data || !data.features || data.features.length === 0) {
            console.log("Resultado vazio, limpando mapa e tabela...");
            if (layerOutput) layerOutputGroup.clearLayers();
            // atualizarStatusBadge(" Sem áreas de interseção!", "processing");
            // document.getElementById('table-results-container').innerHTML = "Sem áreas de interseção encontradas.";
            return;
        }

        layerOutput = L.geoJSON(data, {
            style: {
                color: OUTPUT_GEOM_COLOR, 
                weight: 3,
                fillOpacity: 0.4
            }
        }).addTo(layerOutputGroup);

        mapOutput.fitBounds(layerOutput.getBounds());
        
        // atualizarStatusBadge("✅ Interseção realizada com sucesso!", "success");

    } catch (err) {
        console.error("Erro ao carregar resultado:", err);
        atualizarStatusBadge("❌ Erro ao obter resultado da intersecção!", "error");
    } finally {
        pararMonitoramento(); 
        monitorarLogs();
        updateIntersectButton()
    }
});

function renderAttributeTable(features, containerId, isInputTable = false) {

    iniciarMonitoramento();

    const container = document.getElementById(containerId);
    if (!container || features.length === 0) return;

    let html = `<table class="data-table"><thead><tr>`;
    
    if (isInputTable) {
        html += `<th>Ver</th><th>Intersect</th>`;
    }

    const headers = Object.keys(features[0].properties);
    headers.forEach(header => {
        html += `<th>${header}</th>`;
    });
    html += `</tr></thead><tbody></tbody></table>`;

    container.innerHTML = html;
    const tbody = container.querySelector('tbody');

    features.forEach(feature => {
        const row = document.createElement('tr'); 

        if (isInputTable) {
            const layerId = feature.properties.layerName;

            const visTd = document.createElement('td');
            visTd.innerHTML = `<button class="btn-view" onclick="toggleLayerVisibility(this, '${layerId}')">👁️</button>`;
            row.appendChild(visTd);

            const checkTd = document.createElement('td');
            checkTd.innerHTML = `<input type="checkbox" value="${layerId}" onchange="toggleLayerSelection(this, '${layerId}')">`;
            row.appendChild(checkTd);
        }

        headers.forEach(header => {
            const td = document.createElement('td');
            td.textContent = feature.properties[header];
            row.appendChild(td);
        });

        tbody.appendChild(row);
        pararMonitoramento(); 
    });
}

function toggleLayerSelection(checkbox, layerName) {
    if (checkbox.checked) {
        selectedLayers.add(layerName);
    } else {
        selectedLayers.delete(layerName);
    }

    layerInputGroup.eachLayer(layer => {
        if (layer.options.layerName === layerName) {
            if (checkbox.checked) {
                layer.setStyle({ color: SELECTED_GEOM_COLOR, weight: 3, fillOpacity: 0.3 }); // Destaque verde
                layer.bringToFront();
            } else {
                layer.setStyle({ color: BASE_GEOM_COLOR, weight: 1, fillOpacity: 0.1 }); // Reset azul
            }
        }
    });

    updateIntersectButton();
}

function updateIntersectButton() {

    const btn = document.getElementById('btn-intersect');
    
    if (!btn) return;

    const podeProcessar = selectedLayers.size >= 2;

    btn.disabled = !podeProcessar;
    
    if (podeProcessar) {
        btn.style.opacity = "1";
        btn.style.cursor = "pointer";
        btn.style.backgroundColor = ""; 
    } else {
        btn.style.opacity = "0.5";
        btn.style.cursor = "not-allowed";
        btn.style.backgroundColor = "gray"; 
    }
}

function configurarSincronizacao() {
    mapInput.on('move', () => {
        mapOutput.setView(mapInput.getCenter(), mapInput.getZoom(), { animate: false });
    });

    mapOutput.on('move', () => {
        mapInput.setView(mapOutput.getCenter(), mapOutput.getZoom(), { animate: false });
    });
}

async function carregarTabelaResultado() {
    try {
        iniciarMonitoramento();

        const badge = document.getElementById('status-badge');
        const response = await fetch('/api/read_output_geojson');

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Erro no endpoint /api/read_output_geojson: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.features.length === 0) {
            atualizarStatusBadge("⚠️ As camadas não possuem área de interseção em comum!", "processing");
            document.getElementById('table-results-container').innerHTML = "";
        } else {
            atualizarStatusBadge("✅ Interseção realizada com sucesso!", "success");
            renderAttributeTable('table-results-container', data);
        }
    } catch (err) {
        console.error("Erro ao carregar tabela de atributos:", err);
        atualizarStatusBadge("❌ Erro ao carregar tabela de atributos", "error");
    } finally {
        pararMonitoramento(); 
        monitorarLogs();
    }
}

function atualizarStatusBadge(mensagem, tipo) {
    const badge = document.getElementById('status-badge');
    if (!badge) return;

    badge.innerText = mensagem;
    badge.classList.remove('success', 'error', 'processing');

    if (tipo === 'success') {
        badge.classList.add('success');
    } else if (tipo === 'error') {
        badge.classList.add('error');
    } else if (tipo === 'processing') {
        badge.classList.add('processing');
    }
}

function iniciarMonitoramento() {
    if (logInterval) clearInterval(logInterval);
    logInterval = setInterval(monitorarLogs, 1000);
}

function pararMonitoramento() {
    clearInterval(logInterval);
}

async function monitorarLogs() {
    try {
        const res = await fetch('/api/logs');

        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.detail || `Erro no endpoint /api/logs: ${res.status}`);
        }

        const data = await res.json();
        const consoleLog = document.getElementById('log-console');

        if (data.logs) {
            const formattedLogs = data.logs.map(log => {
                let logClass = 'log-info';
                if (log.includes('[SUCESSO]')) logClass = 'log-success';
                else if (log.includes('[ERRO]')) logClass = 'log-error';
                return `<div class="${logClass}">• ${log}</div>`;
            });
            consoleLog.innerHTML = formattedLogs.join('');
            consoleLog.scrollTop = consoleLog.scrollHeight;
        }
    } catch (err) {
        console.error("Erro ao ler logs:", err);
        atualizarStatusBadge("❌ Erro ao ler logs!", "error");
        pararMonitoramento(); 
    }
}

function toggleLayerVisibility(btn, layerName) {
    let layerEncontrada = false;

    layerInputGroup.eachLayer(layer => {
        if (layer.options.layerName === layerName) {
            layerEncontrada = true;
            if (mapInput.hasLayer(layer)) {
                mapInput.removeLayer(layer);
                btn.innerText = '❌'; 
                btn.title = "Mostrar camada";
                btn.style.opacity = '0.5';
            } else {
                mapInput.addLayer(layer);
                btn.innerText = '👁️'; 
                btn.title = "Ocultar camada";
                btn.style.opacity = '1';
            }
        }
    });

    if (!layerEncontrada) {
        console.warn(`Camada "${layerName}" não encontrada no mapa.`);
    }
}

document.body.addEventListener('htmx:beforeRequest', function(evt) {
    if (evt.detail.elt.getAttribute('hx-get') === '/api/map_intersect') {
        const badge = document.getElementById('status-badge');
        const btn = evt.detail.elt;

        // Atualiza o Badge
        atualizarStatusBadge("⏳ Processando interseção...", "processing");
        btn.disabled = true;
    }
});

document.body.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.elt.getAttribute('hx-post') === '/api/map_intersect') {
        evt.detail.elt.disabled = false;
        carregarTabelaResultado(); 
    }
});

document.body.addEventListener('htmx:configRequest', (evt) => {
    if (evt.detail.path === '/api/map_intersect') {

        const camadasParaProcessar = Array.from(selectedLayers);
        
        if (camadasParaProcessar.length > 0) {
            evt.detail.parameters['layers'] = camadasParaProcessar.join(',');
        }
    }
});

document.addEventListener('DOMContentLoaded', init);