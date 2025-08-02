document.addEventListener('DOMContentLoaded', () => {
  const { gettext } = window;

  // Boton para aceptar solicitud de amistad
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
            <div class="item-amigo card-amigo">
              <a href="/app/usuario/${amigo.id}/" class="item-amigo-link">
                <img src="${amigo.foto}" alt="${amigo.nombre}" />
                <div class="contenido">
                  <strong>@${amigo.username}</strong> <span class="nombre">${amigo.nombre}</span>
                  <p>${amigo.descripcion || ""}</p>
                </div>
              </a>
              <div class="acciones-amigoz">
                <i class="fas fa-user-slash eliminar" data-id="${amigo.amistad_id}"></i>
              </div>
            </div>
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
              mensajeVacioSolicitudes.textContent = gettext('No tienes solicitudes de amistad.');
              const solicitudesSection = document.querySelector('.solicitudes');
              solicitudesSection.appendChild(mensajeVacioSolicitudes);
            }
          }
        }
      });
    });
  });

  // Boton para rechazar solicitud de amistad
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
                vacio.textContent = gettext('No tienes nuevas solicitudes de amistad.');
                solicitudesSection.appendChild(vacio);
              }
            }
          }
        }
      });
    });
  });

  // Boton para eliminar amistad
  document.querySelectorAll('.eliminar').forEach(btn => {
    btn.addEventListener('click', () => {
      const amistadId = btn.getAttribute('data-id');
      if (!amistadId) {
        console.error("amistad_id no válido:", amistadId);
        return;
      }

      fetch('/app/eliminar-amistad/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ amistad_id: amistadId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.ok) {
          btn.closest('.item-amigo').remove();

          const contenedorAmigos = document.querySelectorAll('.item-amigo');
          if (contenedorAmigos.length === 0) {
            document.getElementById('mensaje-sin-amigos').style.display = 'block';
          }
        } else {
          console.error("Error del servidor:", data.error);
        }
      });
    });
  });

  document.querySelectorAll(".btn-chatear").forEach(btn => {
    btn.addEventListener("click", function () {
      const usuarioId = this.dataset.id;
      enviarSolicitudChat(usuarioId, this);
    });
  });

  function enviarSolicitudChat(para_usuario_id, boton) {

    if (!boton) return;
    boton.disabled = true;
    boton.innerHTML = '<span>{% trans "Enviando..." %}</span>';

    fetch("/app/enviar-solicitud-chat/", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ para_usuario_id: para_usuario_id })
    })
    .then(response => response.json())
    .then(data => {
      if (data.ok || (data.error && data.error.includes('Ya existe solicitud'))) {
        boton.outerHTML = `<button class='btn-chatear' disabled style='cursor:not-allowed;opacity:0.7;'>
          <i class="fas fa-comments"></i> {% trans "Pendiente" %}
        </button>`;
      } else {
        alert(data.error || '{% trans "Error enviando solicitud" %}');
        boton.innerHTML = '<i class="fas fa-comments"></i> {% trans "Chatear" %}';
        boton.disabled = false;
      }
    })
    .catch(err => {
      boton.innerHTML = '<i class="fas fa-comments"></i> {% trans "Error" %}';
      boton.disabled = false;
    });
  }

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
