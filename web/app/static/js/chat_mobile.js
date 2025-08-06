document.addEventListener("DOMContentLoaded", () => {
  const gettext = django.gettext;
  const isMobile = () => window.innerWidth <= 876;

  const inputMensaje = document.getElementById("chatinput");
  const btnEnviar = document.querySelector(".fa-paper-plane");
  const mensajesContainer = document.querySelector('.chat-mensajes');
  const chatId = window.location.pathname.split("/").filter(Boolean).pop();
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

  function obtenerMensajes() {
    fetch(`/app/obtener-conversacion/?chat_id=${chatId}`)
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

  // Lógica envío
  let enviando = false;

  function enviarMensaje() {
    if (enviando) return;
    const texto = inputMensaje.value.trim();
    if (!texto) return;

    enviando = true;

    fetch("/app/enviar-mensaje-chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify({
        chat_id: chatId,
        texto: texto
      })
    })
    .then(res => res.json())
    .then(data => {
      enviando = false;
      if (data.ok && data.mensaje) {
        const vacio = mensajesContainer.querySelector('.mensajes-sin-mensajes');
        if (vacio) vacio.remove();

        const fechaActual = data.mensaje.fecha;
        const existeSeparador = [...mensajesContainer.querySelectorAll('.separador-fecha')]
          .some(el => el.textContent === fechaActual);

        if (!existeSeparador) {
          const separador = document.createElement("div");
          separador.classList.add("separador-fecha");
          separador.textContent = fechaActual;
          mensajesContainer.appendChild(separador);
        }

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
      }
    })
    .catch(err => {
      enviando = false;
      console.error("Error al enviar mensaje:", err);
    });
  }

  // Enter para enviar
  btnEnviar?.addEventListener("click", enviarMensaje);
  inputMensaje?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      enviarMensaje();
    }
  });


  // Volver
  const btnVolver = document.querySelector(".btn-volver-chat");
  btnVolver?.addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = "/app/chat/";
  });

  // Auto scroll al cargar
  window.addEventListener("load", scrollToBottom);

  // Mantener scroll si aparece el teclado
  inputMensaje?.addEventListener("focus", () => {
    setTimeout(() => {
      inputMensaje.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 200);
  });

  // Intervalo para verificar nuevos mensajes
  obtenerMensajes(); // Inicial
  intervalMensajes = setInterval(obtenerMensajes, 2000);
});
