document.addEventListener('DOMContentLoaded', function() {
    const createDots = (containerSelector, numDots, className) => {
        const container = document.querySelector(containerSelector);
        for (let i = 0; i < numDots; i++) {
            let dot = document.createElement('div');
            dot.className = className;
            container.appendChild(dot);
        }
    };

    // Corrige la cantidad de bolitas para que coincida con tu descripción
    createDots('.spinner-outer', 6, 'spinner-dot spinner-dot-outer'); // 7 bolitas azules
    createDots('.spinner-inner', 2, 'spinner-dot spinner-dot-inner'); // 3 bolitas doradas

    const positionDots = (containerSelector, radius) => {
        const container = document.querySelector(containerSelector);
        const dots = container.querySelectorAll('.spinner-dot');
        dots.forEach((dot, index) => {
            const angle = (360 / dots.length) * index;
            const angleRad = (angle * Math.PI) / 180;
            // Ajusta la fórmula para considerar el tamaño del contenedor y centrar las bolitas
            const dotRadius = radius - dot.offsetWidth / 2; // Ajusta según el tamaño de las bolitas
            dot.style.transform = `translate(${Math.cos(angleRad) * dotRadius}px, ${Math.sin(angleRad) * dotRadius}px)`;
        });
    };

    // Aumenta los radios para hacer los círculos más grandes
    positionDots('.spinner-outer', 120); // Aumenta el radio para las bolitas azules
    positionDots('.spinner-inner', 60); // Aumenta el radio para las bolitas doradas

    // Controlar el evento de envío del formulario
    document.getElementById('upload-form').addEventListener('submit', function(e) {
        // e.preventDefault(); // Descomenta esta línea si estás manejando la carga con AJAX
        document.getElementById('loading-spinner').style.display = 'flex'; // Mostrar el spinner
        // Aquí se debería manejar la carga del archivo y la respuesta del servidor
        setTimeout(function() {
            document.getElementById('loading-spinner').style.display = 'none'; // Ocultar el spinner después de la "carga"
        }, 3000); // Simulación de la carga
    });
});
