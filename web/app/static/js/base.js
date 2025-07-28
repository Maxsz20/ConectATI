
document.addEventListener('DOMContentLoaded', () => {
  const { gettext } = window;
  const input = document.getElementById('inputBusqueda');
  const dropdown = document.getElementById('dropdownBuscador');

  if (!input || !dropdown) return;

  input.addEventListener('input', () => {
    const query = input.value.trim();
    const contenedor = dropdown.querySelector('.usuarios-buscados');
    dropdown.classList.remove('oculto');

    if (query.length === 0) {
      contenedor.innerHTML = `<p class="sin-resultados">${gettext("Escribe algo para buscar")}</p>`;
      return;
    }

    fetch(`/app/buscar-usuarios/?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        contenedor.innerHTML = '';
        if (!data.usuarios || data.usuarios.length === 0) {
          contenedor.innerHTML = `<p class="sin-resultados">${gettext("Sin resultados")}</p>`;
          return;
        }

        data.usuarios.forEach(usuario => {
          const div = document.createElement('div');
          div.classList.add('usuario-busqueda');
          div.innerHTML = `
            <a href="/app/usuario/${usuario.id}" class="link-usuario-busqueda">
              <img src="${usuario.foto}" alt="${usuario.nombre}">
              <div class="info">
                <strong>@${usuario.username}</strong>
                <small>${usuario.nombre}</small>
              </div>
            </a>
            <div class="acciones-buscador">
              ${
                usuario.estado_amistad === 'aceptada'
                  ? `<i class="fas fa-user-check" title="${gettext("Ya son amigos")}"></i>`
                  : usuario.estado_amistad === 'pendiente'
                    ? `<span class="estado-pendiente"><i class="fas fa-clock"></i> ${gettext("Pendiente")}</span>`
                    : `<button class="btn-agregar" data-id="${usuario.id}">${gettext("Añadir")}</button>`
              }
              ${
                usuario.estado_chat === 'aceptada'
                  ? `<a href="/app/chat"><i class="fas fa-comments icono-chat" title="${gettext("Chatear")}"></i></a>`
                  : usuario.estado_chat === 'pendiente'
                    ? `<span class="estado-pendiente"><i class="fas fa-clock"></i> ${gettext("Chat Pendiente")}</span>`
                    : `<button class="btn-chat-solicitud" data-id="${usuario.id}"><i class="fas fa-comment-dots"></i> ${gettext("Chatear")}</button>`
              }
            </div>`;
          contenedor.appendChild(div);
        });
      });
  });

  input.addEventListener('focus', () => {
    if (input.value.trim().length > 0) {
      dropdown.classList.remove('oculto');
    }
  });

  input.addEventListener('click', () => dropdown.classList.remove('oculto'));

  document.addEventListener('click', e => {
    if (!document.querySelector('.buscador').contains(e.target)) {
      dropdown.classList.add('oculto');
    }

    if (e.target.classList.contains('btn-agregar')) {
      const userId = e.target.getAttribute('data-id');
      fetch(`/app/enviar-solicitud-amistad/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ para_usuario_id: userId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.ok) {
          e.target.outerHTML = `<span class="solicitud-enviada"><i class="fas fa-paper-plane"></i> ${gettext("Enviada")}</span>`;
        } else {
          e.target.textContent = gettext("Ya enviada");
          e.target.disabled = true;
          e.target.classList.add("btn-error");
        }
      });
    }

    if (e.target.closest('.btn-chat-solicitud')) {
      const btn = e.target.closest('.btn-chat-solicitud');
      const userId = btn.getAttribute('data-id');
      fetch(`/app/enviar-solicitud-chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ para_usuario_id: userId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.ok) {
          btn.outerHTML = `<span class="estado-pendiente"><i class="fas fa-clock"></i> Chat Pendiente</span>`;
        } else {
          alert(data.error || 'Error enviando solicitud');
        }
      });
    }

    if (e.target.classList.contains('aceptar')) {
      const id = e.target.dataset.id;
      fetch('/app/aceptar-solicitud-chat/', {
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
          const item = e.target.closest('.solicitud-preview');
          item.remove();

          const panel = document.querySelector('.panel-lateral');
          if (panel) {
            const vacio = panel.querySelector('.mensaje-vacio-chat');
            if (vacio) vacio.remove();

            const nuevoChat = document.createElement('a');
            nuevoChat.href = '/app/chat';
            nuevoChat.innerHTML = `
              <div class="mensaje-preview">
                <img src="${data.chat.foto}" alt="${data.chat.nombre}" />
                <div class="mensaje-info">
                  <div class="usuario">
                    <span class="nombre">${data.chat.nombre}</span>
                    <span>@${data.chat.username} · ahora</span>
                  </div>
                  <p>${gettext("Haz clic aquí para conversar")}</p>
                </div>
                <i class="fas fa-envelope"></i>
              </div>`;
            panel.insertBefore(nuevoChat, panel.querySelector('h3:nth-of-type(2)'));
          }

          mostrarMensajeVacioSiAplica('.panel-lateral', '.solicitud-preview', gettext("No tienes solicitudes de chat pendientes."));
        }
      });
    }

    if (e.target.classList.contains('rechazar')) {
      const id = e.target.dataset.id;
      fetch('/app/rechazar-solicitud-chat/', {
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
          const item = e.target.closest('.solicitud-preview');
          item.remove();

          mostrarMensajeVacioSiAplica('.panel-lateral', '.solicitud-preview', gettext("No tienes solicitudes de chat pendientes."));
        }
      });
    }
  });

  function mostrarMensajeVacioSiAplica(containerSelector, itemSelector, mensajeTexto) {
    const contenedor = document.querySelector(containerSelector);
    const items = contenedor.querySelectorAll(itemSelector);
    if (items.length === 0) {
      const mensaje = document.createElement('div');
      mensaje.style.color = '#888';
      mensaje.style.textAlign = 'center';
      mensaje.style.padding = '1rem 0';
      mensaje.textContent = mensajeTexto;
      contenedor.appendChild(mensaje);
    }
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
