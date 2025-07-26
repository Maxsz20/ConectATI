document.addEventListener("DOMContentLoaded", () => {
  const isMobile = () => window.innerWidth <= 876;

  const chatList = document.querySelector(".chat-list");
  const conversacion = document.querySelector(".conversacion");
  const encabezadoLista = document.querySelector(".encabezado-lista");
  const tituloMobile = document.querySelector(".titulo-mobile");
  const headerMobile = document.querySelector(".header-mobile");
  const chatInput = document.querySelector(".chat-input");
  const menuMobile = document.querySelector(".menu-mobile");
  const encabezadoChatMobile = document.querySelector(".encabezado-chat-mobile");
  const avatarMobile = document.getElementById("chat-avatar");
  const nombreMobile = document.getElementById("chat-nombre");
  const usuarioMobile = document.getElementById("chat-usuario");
  const botonPublicar = document.querySelector(".boton-publicar-mobile");
  const columnaCentral = document.querySelector(".columna-central");
  const avatarDesktop = document.getElementById("chat-avatar-desktop");
  const nombreDesktop = document.getElementById("chat-nombre-desktop");
  const usuarioDesktop = document.getElementById("chat-usuario-desktop");
  const mensajesContainer = document.querySelector('.chat-mensajes');

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

  function scrollToBottom() {
    if (mensajesContainer) {
      mensajesContainer.scrollTop = mensajesContainer.scrollHeight;
    }
  }

  function activarClickChats() {
    const chatItems = document.querySelectorAll(".chat-user");

    chatItems.forEach(item => {
      item.addEventListener("click", () => {
        const usuarioId = item.dataset.usuarioId;
        const linkPerfil = document.getElementById("link-perfil-chat");
        if (linkPerfil && usuarioId) {
          linkPerfil.setAttribute("href", `/app/usuario/${usuarioId}/`);
        }

        // Buscar el chat id asociado (puede estar en data-chat-id si lo agregas en Django)
        let chatId = item.dataset.chatId;
        if (!chatId && item.getAttribute('data-chat-id')) chatId = item.getAttribute('data-chat-id');

        // Si tienes el chat id, usa obtener-conversacion, si no, usa obtener-mensajes-chat
        let url = chatId ? `/app/obtener-conversacion/?chat_id=${chatId}` : `/app/obtener-mensajes-chat/?usuario_id=${usuarioId}`;

        fetch(url)
          .then(res => res.json())
          .then(data => {
            // --- Actualizar encabezado Desktop ---

            if (item.querySelector('img')) {
              avatarDesktop.src = item.querySelector('img').src;
              avatarDesktop.alt = item.querySelector('img').alt;
            }
            if (item.querySelector('span')) {
              const nombre = item.querySelector('span small')?.textContent || item.querySelector('span').textContent.split('\n')[0].trim();
              nombreDesktop.textContent = nombre;
            }
            if (usuarioDesktop && item.querySelector('span')) {
              const username = item.querySelector('span').textContent.match(/@\w+/)?.[0] || '';
              usuarioDesktop.textContent = username;
            }

            // --- Actualizar encabezado Mobile ---
            if (avatarMobile && item.querySelector('img')) {
              avatarMobile.src = item.querySelector('img').src;
              avatarMobile.alt = item.querySelector('img').alt;
            }
            if (nombreMobile && item.querySelector('span small')) {
              nombreMobile.textContent = item.querySelector('span small').textContent;
            }
            if (usuarioMobile && item.querySelector('span')) {
              usuarioMobile.textContent = item.querySelector('span').textContent.match(/@\w+/)?.[0] || '';
            }

            // --- Actualizar mensajes ---
            mensajesContainer.innerHTML = "";
            let mensajes = data.mensajes || [];
            if (mensajes.length === 0) {
              mensajesContainer.innerHTML = `<div style=\"color:#888; text-align:center; padding:1rem;\">No hay mensajes aún.</div>`;
            } else {
              mensajes.forEach(msg => {
                const div = document.createElement("div");
                div.classList.add("mensaje", msg.propio || msg.es_emisor ? "enviado" : "recibido");
                div.textContent = msg.texto;
                mensajesContainer.appendChild(div);
              });
            }

            const linkPerfil = document.getElementById("link-perfil-chat");
            if (linkPerfil && usuarioId) {
              linkPerfil.href = `/app/usuario/${usuarioId}/`;
            }

            // --- Mostrar input ---
            if (chatInput) chatInput.style.display = "flex";

            scrollToBottom();

            // --- Mobile UI ---
            if (isMobile()) {
              chatList.style.display = "none";
              conversacion.style.display = "flex";
              encabezadoLista.style.display = "none";
              encabezadoChatMobile.style.display = "flex";
              headerMobile.style.display = "none";
              tituloMobile.style.display = "none";
              menuMobile.style.display = "none";
              chatInput.style.display = "flex";
              botonPublicar.style.display = "none";
              columnaCentral.style.display = "none";
            }
          });
      });

      const botonEliminar = item.querySelector(".eliminar-chat");
      if (botonEliminar) {
        botonEliminar.addEventListener("click", (e) => {
          e.stopPropagation(); 

          const chatId = item.dataset.chatId;

          fetch('/app/eliminar-chat/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ chat_id: chatId })
          })
          .then(res => res.json())
          .then(data => {
            if (data.ok) {
              item.remove();

              const restantes = document.querySelectorAll('.chat-user');
              const chatVacio = document.querySelector('.chat-mensajes');
              const chatInput = document.querySelector('.chat-input');

              // Si no queda ningún chat, mostrar mensaje de "No hay mensajes"
              if (restantes.length === 0) {
                const vacio = document.createElement('div');
                vacio.className = 'mensaje-vacio-chat';
                vacio.style.color = '#888';
                vacio.style.textAlign = 'center';
                vacio.style.padding = '1rem 0';
                vacio.textContent = 'No hay mensajes.';
                document.querySelector('.chat-list').appendChild(vacio);

                // Reiniciar vista derecha
                document.getElementById('chat-nombre-desktop').textContent = 'Sin chat seleccionado';
                document.getElementById('chat-usuario-desktop').textContent = '';
                document.getElementById('chat-avatar-desktop').src = '/static/images/default_user.avif';
                document.getElementById('chat-avatar-desktop').alt = 'Sin chat seleccionado';

                // También para mobile
                document.getElementById('chat-nombre').textContent = 'Sin chat seleccionado';
                document.getElementById('chat-usuario').textContent = '';
                document.getElementById('chat-avatar').src = '/static/images/default_user.avif';
                document.getElementById('chat-avatar').alt = 'Sin chat seleccionado';

                // Limpiar mensajes
                if (chatVacio) {
                  chatVacio.innerHTML = `<div style="color:#888; text-align:center; padding:1rem;">Selecciona un chat para comenzar a conversar.</div>`;
                }

                // Ocultar input
                if (chatInput) {
                  chatInput.style.display = 'none';
                }

              } else {
                // Si quedan otros chats, activa el primero
                if (!isMobile()) {
                  restantes[0].click();
                }
              }
            }
          });
        });
      }
    });
  }

  activarClickChats();

  const btnVolver = encabezadoChatMobile.querySelector(".btn-volver-chat");
  btnVolver.addEventListener("click", () => {
    chatList.style.display = "block";
    conversacion.style.display = "none";
    encabezadoChatMobile.style.display = "none";
    encabezadoLista.style.display = "flex";
    headerMobile.style.display = "flex";
    tituloMobile.style.display = "block";
    chatInput.style.display = "none";
    menuMobile.style.display = "flex";
    botonPublicar.style.display = "flex";
    columnaCentral.style.display = "block";
  });

  document.querySelectorAll('.solicitudes-chat .aceptar').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
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
          btn.closest('.item-solicitud').remove();

          const solicitudesSection = document.querySelector('.solicitudes-chat');
          if (solicitudesSection.querySelectorAll('.item-solicitud').length === 0) {
            const vacio = document.createElement('div');
            vacio.style.color = '#888';
            vacio.style.textAlign = 'center';
            vacio.style.padding = '1rem 0';
            vacio.textContent = 'No tienes solicitudes de chat pendientes.';
            solicitudesSection.appendChild(vacio);
          }

          // --- NUEVO: Crear el chat con ambos atributos ---
          const nuevo = document.createElement('div');
          nuevo.classList.add('chat-user');
          // Usa el id del usuario con quien se chatea, si está disponible
          nuevo.setAttribute('data-usuario-id', data.chat.usuario_id || data.chat.id);
          nuevo.setAttribute('data-chat-id', data.chat.id);
          nuevo.innerHTML = `
            <div class="chat-user-info">
              <img src="${data.chat.foto}" alt="${data.chat.nombre}" />
              <span>
                @${data.chat.username}<br />
                <small>${data.chat.nombre}</small>
              </span>
            </div>
            <div class="acciones-chat">
              <i class="fas fa-trash eliminar-chat" title="Eliminar chat"></i>
            </div>
          `;
          const mensajeVacio = chatList.querySelector('.mensaje-vacio-chat');
          if (mensajeVacio) mensajeVacio.remove();
          chatList.prepend(nuevo);
          activarClickChats();
          if (!isMobile()) {
            nuevo.click(); // Evita mostrar conversación automáticamente en mobile
          }
          if (chatList.querySelectorAll('.chat-user').length === 1) {
            avatarDesktop.src = data.chat.foto;
            avatarDesktop.alt = data.chat.nombre;
            nombreDesktop.textContent = data.chat.nombre;
            usuarioMobile.textContent = '@' + data.chat.username;
            avatarMobile.src = data.chat.foto;
            avatarMobile.alt = data.chat.nombre;
            nombreMobile.textContent = data.chat.nombre;
            if (chatInput) chatInput.style.display = 'flex';
            if (mensajesContainer) {
              mensajesContainer.innerHTML = `<div style="color:#888; text-align:center; padding:1rem;">No hay mensajes aún.</div>`;
            }
          }
        }
      });
    });
  });

  document.querySelectorAll('.solicitudes-chat .rechazar').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
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
          btn.closest('.item-solicitud').remove();
          const solicitudesSection = document.querySelector('.solicitudes-chat');
          if (solicitudesSection.querySelectorAll('.item-solicitud').length === 0) {
            const vacio = document.createElement('div');
            vacio.style.color = '#888';
            vacio.style.textAlign = 'center';
            vacio.style.padding = '1rem 0';
            vacio.textContent = 'No tienes solicitudes de chat pendientes.';
            solicitudesSection.appendChild(vacio);
          }
        }
      });
    });
  });

  window.addEventListener('load', scrollToBottom);
  
  // Add resize event listener to handle responsive changes
  window.addEventListener('resize', handleResponsiveLayout);
  
  const primerChat = document.querySelector(".chat-user");
  if (primerChat) {
    if (!isMobile()) {
      primerChat.click(); // solo en desktop
    } else {
      // En mobile, asegurar que solo la lista esté visible
      chatList.style.display = "block";
      conversacion.style.display = "none";
      encabezadoChatMobile.style.display = "none";
      encabezadoLista.style.display = "flex";
      headerMobile.style.display = "flex";
      tituloMobile.style.display = "block";
      chatInput.style.display = "none";
      menuMobile.style.display = "flex";
      if (botonPublicar) botonPublicar.style.display = "flex";
      columnaCentral.style.display = "block";
    }
  } else {
    // Si no hay chats, también asegurar que en mobile se muestre la lista vacía
    if (isMobile()) {
      chatList.style.display = "block";
      conversacion.style.display = "none";
      encabezadoChatMobile.style.display = "none";
      encabezadoLista.style.display = "flex";
      headerMobile.style.display = "flex";
      tituloMobile.style.display = "block";
      chatInput.style.display = "none";
      menuMobile.style.display = "flex";
      if (botonPublicar) botonPublicar.style.display = "flex";
      columnaCentral.style.display = "block";
    }
  }
  
  // Initialize responsive layout
  handleResponsiveLayout();
});
