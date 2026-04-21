// 1. Variáveis Globais
let mapInput, mapOutput;
let layerInputGroup, layerOutputGroup;
let layerOutput = null;
let logInterval;

// Inicializa mapas
function init() {
    console.log("Iniciando...");
    iniciarMonitoramento();
    
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

    configurarSincronizacao();

    setTimeout(() => {
        mapInput.invalidateSize();
        mapOutput.invalidateSize();
        carregarCamadasBase();
    }, 400);
}

// renderiza shapes de entrada
async function carregarCamadasBase() {
    const badge = document.getElementById('status-badge');
    try {

        const res = await fetch('/api/inputs_geojson');
        if (!res.ok) throw new Error("Falha na API");
        
        const data = await res.json();
        layerInputGroup.clearLayers();

        let todasAsFeatures = [];

        Object.keys(data).forEach(key => {
            const geojsonLayer = L.geoJSON(data[key], {
                style: { color: '#3498db', weight: 2, fillOpacity: 0.2 }
            });
            layerInputGroup.addLayer(geojsonLayer);
            
            if(data[key].features) {
                todasAsFeatures = todasAsFeatures.concat(data[key].features);
            }
        });

        const bounds = L.featureGroup(layerInputGroup.getLayers()).getBounds();
        if (bounds.isValid()) mapInput.fitBounds(bounds);

        const dataParaTabela = {
            type: "FeatureCollection",
            features: todasAsFeatures
        };

        renderAttributeTable('table-input-container', dataParaTabela, ['ID_GBA', 'Área (m²)', 'Área (ha)', 'value']);

    } catch (err) {
        console.error("Erro ao carregar bases:", err);
        atualizarStatusBadge("❌ Erro: " + err.message, "error");
    } finally {
        pararMonitoramento(); 
        monitorarLogs();
    }
}

// atualiza mapa resultado
document.body.addEventListener('atualizarMapa', async () => {
    console.log("Evento 'atualizarMapa' Iniciando carga do Mapa 2...");
    const badge = document.getElementById('status-badge');

    try {
        atualizarStatusBadge("⏳ Carregando geometrias...", "processing");

        const response = await fetch('/api/read_output_geojson'); 
        if (!response.ok) throw new Error("Erro ao buscar dados do mapa");
        
        const data = await response.json();

        if (layerOutput) {
            mapOutput.removeLayer(layerOutput);
        }

        if (!data || !data.features || data.features.length === 0) {
            console.log("Resultado vazio, limpando mapa e tabela...");
            if (layerOutput) layerOutputGroup.clearLayers();
            document.getElementById('table-results-container').innerHTML = "Sem áreas de interseção encontradas.";
            return;
        }

        layerOutput = L.geoJSON(data, {
            style: {
                color: '#e74c3c', 
                weight: 3,
                fillOpacity: 0.4
            }
        }).addTo(layerOutputGroup);

        mapOutput.fitBounds(layerOutput.getBounds());

        atualizarStatusBadge("✅ Mapa atualizado!", "success");

    } catch (err) {
        console.error("Erro ao renderizar mapa 2:", err);
        atualizarStatusBadge("❌ Erro: " + err.message, "error");
    } finally {
        pararMonitoramento(); 
        monitorarLogs();
    }
});

// renderiza tabela de atributos
function renderAttributeTable(containerId, geojsonData, specificColumns = null) {
    const container = document.getElementById(containerId);
    
    if (!geojsonData || !geojsonData.features || geojsonData.features.length === 0) {
        container.innerHTML = '';
        return;
    }

    const features = geojsonData.features;
    const headers = specificColumns || Object.keys(features[0].properties);

    let html = `
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        ${headers.map(h => `<th>${h}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
    `;

    features.forEach(feature => {
        html += '<tr>';
        headers.forEach(col => {
            let val = feature.properties[col];
            
            // Formatação Numérica (ABNT/BR)
            if (typeof val === 'number') {
                let decimals;

                if (col.includes('Área')) {
                    decimals = 3;
                } else if (col.includes('banda') || col === 'media') {
                    decimals = 2;
                } else {
                decimals = Number.isInteger(val) ? 0 : 2;
            }

            val = val.toLocaleString('pt-BR', { 
                minimumFractionDigits: decimals, 
                maximumFractionDigits: decimals 
            });
        }
            
            const isNumeric = typeof feature.properties[col] === 'number';
            html += `<td class="${isNumeric ? 'numeric' : ''}">${val ?? '-'}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
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
        const badge = document.getElementById('status-badge');
        const response = await fetch('/api/read_output_geojson');
        const data = await response.json();
        
        if (data.features.length === 0) {
            atualizarStatusBadge("⚠️ As geometrias não tem áreas de interseção", "processing");
            document.getElementById('table-results-container').innerHTML = "";
        } else {
            atualizarStatusBadge("✅ Interseção realiza com sucesso!", "success");
            renderAttributeTable('table-results-container', data);
        }
    } catch (err) {
        console.error("Erro ao carregar tabela de atributos:", err);
        atualizarStatusBadge("❌ Erro: " + err.message, "error");
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

// document.body.addEventListener('atualizarMapa', () => {
//     carregarTabelaResultado();
// });

document.body.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.elt.getAttribute('hx-get') === '/api/map_intersect') {
        evt.detail.elt.disabled = false;
        carregarTabelaResultado(); 
    }
});

document.addEventListener('DOMContentLoaded', init);