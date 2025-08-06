document.addEventListener("DOMContentLoaded", () => {
  const gettext = django.gettext;
  const isMobile = () => window.innerWidth <= 876;

  const chatList = document.querySelector(".chat-list");
  const mensajesContainer = document.querySelector('.chat-mensajes');
  const botonPublicar = document.querySelector(".boton-publicar-mobile");
  const inputMensaje = document.getElementById("chatinput");
  const chatInput = document.querySelector(".chat-input");

  let chatActivoId = null;
  let modoConversacionActiva = false;
  let intervalMensajes = null;

  function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [key, value] = cookie.trim().split('=');
      if (key === name) return decodeURIComponent(value);
    }
    return null;
  }

  function scrollToBottom() {
    if (mensajesContainer) {
      mensajesContainer.scrollTop = mensajesContainer.scrollHeight;
    }
  }

  function verificarMensajesNuevos() {
    if (!chatActivoId || !modoConversacionActiva) return;

    fetch(`/app/obtener-conversacion/?chat_id=${chatActivoId}`)
      .then(res => res.json())
      .then(data => {
        if (!data.ok || !data.mensajes) return;

        const fragmento = document.createDocumentFragment();
        let nuevosAgregados = false;

        Object.entries(data.mensajes).forEach(([fecha, lista]) => {
          const yaExisteFecha = [...mensajesContainer.querySelectorAll('.separador-fecha')]
            .some(el => el.textContent === fecha);

          if (!yaExisteFecha) {
            const separador = document.createElement("div");
            separador.classList.add("separador-fecha");
            separador.textContent = fecha;
            fragmento.appendChild(separador);
          }

          lista.forEach(msg => {
            const yaExiste = [...mensajesContainer.querySelectorAll('.mensaje')]
              .some(div => {
                const contenido = div.querySelector('.contenido-mensaje')?.textContent.trim();
                const hora = div.querySelector('.hora-mensaje')?.textContent.trim();
                const clase = div.classList.contains(msg.propio ? "enviado" : "recibido");
                return contenido === msg.texto && hora === msg.hora && clase;
              });

            if (yaExiste) return;

            const div = document.createElement("div");
            div.classList.add("mensaje", msg.propio ? "enviado" : "recibido");

            const contenido = document.createElement("div");
            contenido.classList.add("contenido-mensaje");
            contenido.textContent = msg.texto;

            const hora = document.createElement("span");
            hora.classList.add("hora-mensaje");
            hora.textContent = msg.hora;

            div.appendChild(contenido);
            div.appendChild(hora);
            fragmento.appendChild(div);

            nuevosAgregados = true;
          });
        });

        if (nuevosAgregados) {
          mensajesContainer.appendChild(fragmento);
          scrollToBottom();
        }
      });
  }

  function activarClickChats() {
    const chatItems = document.querySelectorAll(".chat-user");

    chatItems.forEach(item => {
      item.addEventListener("click", () => {
        const chatId = item.dataset.chatId;
        chatActivoId = chatId;
        modoConversacionActiva = true;

        if (intervalMensajes) clearInterval(intervalMensajes);
        intervalMensajes = setInterval(verificarMensajesNuevos, 2000);

        if (isMobile()) {
          window.location.href = `/app/chat_mobile/${chatId}/`;
          return;
        }

        const usuarioId = item.dataset.usuarioId;
        const linkPerfil = document.getElementById("link-perfil-chat");
        if (linkPerfil && usuarioId) {
          linkPerfil.setAttribute("href", `/app/usuario/${usuarioId}/`);
        }

        fetch(`/app/obtener-conversacion/?chat_id=${chatId}`)
          .then(res => res.json())
          .then(data => {
            if (!data.ok || !data.mensajes) return;

            const avatar = document.getElementById("chat-avatar-desktop");
            const nombre = document.getElementById("chat-nombre-desktop");
            const username = document.getElementById("chat-usuario-desktop");

            const img = item.querySelector('img');
            if (img && avatar) {
              avatar.src = img.src;
              avatar.alt = img.alt;
            }

            const span = item.querySelector('span');
            if (span) {
              const nombreTxt = span.querySelector('small')?.textContent || span.textContent.trim();
              const usernameTxt = span.textContent.match(/@\w+/)?.[0] || '';
              nombre.textContent = nombreTxt;
              username.textContent = usernameTxt;
            }

            mensajesContainer.innerHTML = "";
            if (Object.keys(data.mensajes).length === 0) {
              mensajesContainer.innerHTML = `<div class="mensajes-sin-mensajes">${gettext("No hay mensajes aún.")}</div>`;
            } else {
              Object.entries(data.mensajes).forEach(([fecha, lista]) => {
                const separador = document.createElement("div");
                separador.classList.add("separador-fecha");
                separador.textContent = fecha;
                mensajesContainer.appendChild(separador);

                lista.forEach(msg => {
                  const div = document.createElement("div");
                  div.classList.add("mensaje", msg.propio ? "enviado" : "recibido");

                  const contenido = document.createElement("div");
                  contenido.classList.add("contenido-mensaje");
                  contenido.textContent = msg.texto;

                  const hora = document.createElement("span");
                  hora.classList.add("hora-mensaje");
                  hora.textContent = msg.hora;

                  div.appendChild(contenido);
                  div.appendChild(hora);
                  mensajesContainer.appendChild(div);
                });
              });
            }

            if (chatInput) chatInput.style.display = "flex";
            scrollToBottom();
          });
      });

      const btnEliminar = item.querySelector(".eliminar-chat");
      if (btnEliminar) {
        btnEliminar.addEventListener("click", e => {
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
                if (restantes.length === 0) {
                  const vacio = document.createElement("div");
                  vacio.className = "mensaje-vacio-chat";
                  vacio.textContent = gettext("No hay mensajes.");
                  chatList.appendChild(vacio);
                }
              }
            });
        });
      }
    });
  }

  activarClickChats();

  const btnEnviar = document.querySelector(".fa-paper-plane");

  btnEnviar?.addEventListener("click", () => {
    const texto = inputMensaje.value.trim();
    if (!texto || !chatActivoId) return;

    fetch("/app/enviar-mensaje-chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify({
        chat_id: chatActivoId,
        texto: texto
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.ok && data.mensaje) {
          const vacio = mensajesContainer.querySelector('.mensajes-sin-mensajes');
          if (vacio) vacio.remove();

          const fechaActual = data.mensaje.fecha;

          // Agrega separador si no existe
          const existeSeparador = [...mensajesContainer.querySelectorAll('.separador-fecha')]
            .some(el => el.textContent === fechaActual);

          if (!existeSeparador) {
            const separador = document.createElement("div");
            separador.classList.add("separador-fecha");
            separador.textContent = fechaActual;
            mensajesContainer.appendChild(separador);
          }

          // Agregar mensaje nuevo
          const div = document.createElement("div");
          div.classList.add("mensaje", "enviado");

          const contenido = document.createElement("div");
          contenido.classList.add("contenido-mensaje");
          contenido.textContent = data.mensaje.texto;

          const hora = document.createElement("span");
          hora.classList.add("hora-mensaje");
          hora.textContent = data.mensaje.hora;

          div.appendChild(contenido);
          div.appendChild(hora);
          mensajesContainer.appendChild(div);

          inputMensaje.value = "";
          scrollToBottom();
          const chatItemActual = document.querySelector(`.chat-user[data-chat-id="${chatActivoId}"]`);
          if (chatItemActual) {
            chatItemActual.classList.add('animado-subida');
            chatList.prepend(chatItemActual);  // ← lo mueve al principio

            setTimeout(() => {
              chatItemActual.classList.remove('animado-subida');
            }, 300);
          }
        }
      })
      .catch(err => {
        console.error("Error al enviar mensaje:", err);
      });
  });

  // Enviar con Enter
  inputMensaje?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      btnEnviar.click();
    }
  });

  // Aceptar solicitud de chat
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
            vacio.textContent = gettext("No tienes solicitudes de chat pendientes.");
            solicitudesSection.appendChild(vacio);
          }

          // Crear nuevo chat visualmente
          const nuevo = document.createElement('div');
          nuevo.classList.add('chat-user', 'animado-subida');
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

          // Quitar animación luego de un tiempo
          setTimeout(() => {
            nuevo.classList.remove('animado-subida');
          }, 300);

          activarClickChats();

          if (!isMobile()) {
            nuevo.click();  // Mostrar conversación en desktop
          }
        }
      });
    });
  });

  // Rechazar solicitud de chat
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
            vacio.textContent = gettext("No tienes solicitudes de chat pendientes.");
            solicitudesSection.appendChild(vacio);
          }
        }
      });
    });
  });

  // Si hay un primer chat en desktop, actívalo automáticamente
  const primerChat = document.querySelector(".chat-user");
  if (primerChat) {
    if (!isMobile()) {
      primerChat.click();
      modoConversacionActiva = true;
      verificarMensajesNuevos();
    } else {
      // En mobile no se activa automáticamente
      if (botonPublicar) botonPublicar.style.display = "none";
    }
  } else {
    // No hay chats cargados
    if (isMobile() && botonPublicar) {
      botonPublicar.style.display = "flex";
    }
  }

  // Mobile inicial
  if (!primerChat && isMobile() && botonPublicar) {
    botonPublicar.style.display = "flex";
  }
});
