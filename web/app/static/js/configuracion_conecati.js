// Cambiar opcion
function cambiarOpcion(spanID, textoVisible, toggleID) {
  const span = document.getElementById(spanID);
  const toggle = document.getElementById(toggleID);

  if (span) span.textContent = textoVisible;
  if (toggle) toggle.checked = false;

  if (spanID === 'valorIdioma') {
    const idioma = textoVisible === 'EN' ? 'en' : 'es';
    document.getElementById('inputIdioma').value = idioma;
    document.getElementById('formIdioma').submit();
  }

  // Cambiar tema claro/oscuro
  if (spanID === 'valorTema') {
    const tema = textoVisible === 'Oscuro' ? 'oscuro' : 'claro';
    document.documentElement.classList.toggle('tema-oscuro', tema === 'oscuro');
    localStorage.setItem('tema', tema);

    const inputTema = document.getElementById('inputTema');
    if (inputTema) {
      inputTema.value = tema;
      document.getElementById('formTema').submit();
    }
  }
}

// Cambiar privacidad
function handlePrivacidadClick(elemento) {
  const spanID = elemento.dataset.spanid;
  const textoVisible = elemento.dataset.visible; // Lo que se muestra en pantalla
  const toggleID = elemento.dataset.toggleid;
  const valorReal = elemento.dataset.value; // Lo que se envía al backend

  const span = document.getElementById(spanID);
  const toggle = document.getElementById(toggleID);
  const input = document.getElementById('inputPrivacidadForm');

  if (span) span.textContent = textoVisible;
  if (toggle) toggle.checked = false;

  console.log("Valor enviado:", valorReal);

  if (input) {
    input.value = valorReal;
    document.getElementById('formPrivacidad').submit();
  }
}

// Mostrar/ocultar dropdown del buscador
const input = document.getElementById('inputBusqueda');
const dropdown = document.getElementById('dropdownBuscador');

if (input && dropdown) {
  input.addEventListener('focus', () => {
    dropdown.classList.remove('oculto');
  });

  document.addEventListener('click', function (e) {
    if (!document.querySelector('.buscador')?.contains(e.target)) {
      dropdown.classList.add('oculto');
    }
  });
}

