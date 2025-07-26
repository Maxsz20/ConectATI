document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.aceptar').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      fetch('/app/aceptar-solicitud/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ solicitud_id: id })
      })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          // Eliminar solicitud
          const solicitud = btn.closest('.item-solicitud');
          solicitud.remove();

          // Insertar nuevo amigo
          const amigo = data.amigo;
          const nuevoHTML = `
            <a href="/app/usuario/${amigo.id}/" class="item-amigo-link">
              <div class="item-amigo card-amigo">
                <img src="${amigo.foto}" alt="${amigo.nombre}" />
                <div class="contenido">
                  <strong>@${amigo.username}</strong> <span class="nombre">${amigo.nombre}</span>
                  <p>${amigo.descripcion || ""}</p>
                </div>
                <i class="fas fa-user-slash eliminar"></i>
              </div>
            </a>
          `;

          const temp = document.createElement('div');
          temp.innerHTML = nuevoHTML.trim();
          const nuevo = temp.firstElementChild;

          // Eliminar mensaje "no tienes amigos"
          const listaAmigos = document.querySelector('.lista-amigos');
          if (listaAmigos) {
            const mensajeVacio = document.getElementById('mensaje-sin-amigos');
            if (mensajeVacio) mensajeVacio.remove();
            listaAmigos.prepend(nuevo);
          }

          // Verificar solicitudes
          const solicitudesRestantes = document.querySelectorAll('.item-solicitud');
          if (solicitudesRestantes.length === 0) {
            let mensajeVacioSolicitudes = document.getElementById('mensaje-sin-solicitudes');
            if (!mensajeVacioSolicitudes) {
              mensajeVacioSolicitudes = document.createElement('div');
              mensajeVacioSolicitudes.id = 'mensaje-sin-solicitudes';
              mensajeVacioSolicitudes.className = 'mensaje-vacio-solicitudes';
              mensajeVacioSolicitudes.style.color = '#888';
              mensajeVacioSolicitudes.style.textAlign = 'center';
              mensajeVacioSolicitudes.style.padding = '1rem 0';
              mensajeVacioSolicitudes.textContent = 'No tienes solicitudes de amistad.';
              const solicitudesSection = document.querySelector('.solicitudes');
              solicitudesSection.appendChild(mensajeVacioSolicitudes);
            }
          }
        }
      });
    });
  });

  document.querySelectorAll('.rechazar').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      fetch('/app/rechazar-solicitud/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ solicitud_id: id })
      })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          btn.closest('.item-solicitud').remove();
          // Si ya no quedan solicitudes, quitar mensaje vacío
          const solicitudesSection = document.querySelector('.solicitudes');
          if (solicitudesSection) {
            const solicitudesRestantes = solicitudesSection.querySelectorAll('.item-solicitud');
            if (solicitudesRestantes.length === 0) {
              let vacio = solicitudesSection.querySelector('p');
              if (!vacio) {
                vacio = document.createElement('p');
                vacio.textContent = 'No tienes nuevas solicitudes de amistad.';
                solicitudesSection.appendChild(vacio);
              }
            }
          }
        }
      });
    });
  });

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
