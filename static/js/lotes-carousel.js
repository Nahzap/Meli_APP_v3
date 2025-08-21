document.addEventListener('DOMContentLoaded', () => {
    const carouselContainer = document.getElementById('lotes-carousel-container');
    if (!carouselContainer) {
        console.error('Error: Carousel container #lotes-carousel-container not found.');
        return;
    }

    const userId = carouselContainer.dataset.userId;
    if (!userId || userId === 'None') {
        return;
    }

    loadLotes(userId);
});

async function loadLotes(userId) {
    const carousel = document.getElementById('lotes-carousel');
    if (!carousel) return;

    try {
        const response = await fetch(`/api/lotes/${userId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const lotes = data.success ? data.lotes : (Array.isArray(data) ? data : []);
        renderLotesCarousel(lotes);
    } catch (error) {
        console.error('Error loading lotes:', error);
        carousel.innerHTML = `<p class="text-red-500 col-span-full">Error al cargar lotes.</p>`;
    }
}

function renderLotesCarousel(lotes) {
    const carousel = document.getElementById('lotes-carousel');
    if (!carousel) return;

    carousel.innerHTML = '';

    if (!lotes || lotes.length === 0) {
        carousel.innerHTML = '<p class="text-gray-500 col-span-full">Este usuario no tiene lotes registrados.</p>';
        return;
    }

    lotes.forEach(lote => {
        const loteButton = document.createElement('button');
        loteButton.dataset.loteId = lote.id;
        loteButton.className = 'flex-shrink-0 w-20 h-14 bg-white rounded-lg shadow-md p-1 flex flex-col items-center justify-center text-center hover:shadow-lg hover:bg-yellow-50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-yellow-500';
        loteButton.type = 'button';

        loteButton.innerHTML = `
            <span class="text-lg font-bold text-yellow-500">${lote.orden_miel}</span>
            <span class="text-xs font-semibold text-gray-700 break-words overflow-hidden text-ellipsis">${lote.nombre_miel}</span>
        `;

        loteButton.addEventListener('click', handleLoteButtonClick);
        carousel.appendChild(loteButton);
    });
}

async function handleLoteButtonClick(event) {
    const button = event.currentTarget;
    const loteId = button.dataset.loteId;

    if (!loteId) {
        console.error('No lote ID found on the button.');
        return;
    }

    console.log(`Fetching composition for lot ID: ${loteId}`);

    try {
        const response = await fetch(`/api/lote/composicion/${loteId}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.success) {
            console.log('--- Composición Botánica ---');
            console.log(`Lote ID: ${data.lote_id}`);
            console.log('Composición:', data.composicion);
            console.log('--------------------------');
            
            // Parse composition data and update botanical chart
            const compositionData = parseCompositionData(data.composicion);
            updateBotanicalChartWithComposition(compositionData);
            
        } else {
            console.error(`Error fetching composition: ${data.error}`);
            alert(`Error al obtener la composición: ${data.error}`);
        }
    } catch (error) {
        console.error('Failed to fetch lot composition:', error);
        alert(`Fallo la solicitud para obtener la composición del lote: ${error.message}`);
    }
}

function parseCompositionData(compositionString) {
    // Parse "Trebol Blanco:100" format
    const compositions = {};
    if (!compositionString) return compositions;
    
    const entries = compositionString.split(',');
    entries.forEach(entry => {
        const [species, percentage] = entry.split(':');
        if (species && percentage) {
            compositions[species.trim()] = parseFloat(percentage.trim());
        }
    });
    
    return compositions;
}

function updateBotanicalChartWithComposition(compositionData) {
    // Find botanical chart instance and update it with composition data
    if (window.BotanicalChart && window.botanicalChartInstance) {
        window.botanicalChartInstance.updateWithComposition(compositionData);
    } else {
        console.warn('Botanical chart not found or not initialized');
    }
}
