document.addEventListener("DOMContentLoaded", () => {
  const gettext = django.gettext;
  const modal = document.getElementById("modalRespuesta");
  const avatarPublicacion = document.getElementById("avatarPublicacion");
  const nombreAutor = document.getElementById("nombreAutor");
  const textoOriginal = document.getElementById("textoOriginal");
  const usuarioMencionado = document.getElementById("usuarioMencionado");
  const idPadreRespuesta = document.getElementById("idPadreRespuesta");
  const imagenPublicacion = document.getElementById("imagen-publicacion");

  // Función para mostrar un toast
  function mostrarToast(mensaje) {
    const toast = document.getElementById("toast");
    const mensajeEl = document.getElementById("toastMensaje");
    mensajeEl.textContent = mensaje;

    toast.style.display = "block";

    setTimeout(() => {
      toast.style.display = "none";
    }, 3000);
  }

  // Función para abrir el modal de respuesta
  document.querySelectorAll(".comentario-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isMobile = window.innerWidth <= 876;
      if (isMobile) {

        const tipo = btn.dataset.tipo;
        const comentarioId = btn.dataset.id;
        const publicacionId = btn.dataset.publicacionId;

        if (tipo === "comentario" && comentarioId) {
          window.location.href = `/app/reply_mobile_comment/${comentarioId}/`;
        } else if (tipo === "publicacion" && publicacionId) {
          window.location.href = `/app/reply_mobile/${publicacionId}/`;
        }
        return;
      }

      const nombre = btn.dataset.nombre;
      const username = btn.dataset.username;
      const texto = btn.dataset.texto;
      const foto = btn.dataset.foto;
      const postId = btn.dataset.id;
      const imagenUrl = btn.dataset.imagen;

      if (nombreAutor) nombreAutor.textContent = nombre;
      if (usuarioMencionado) usuarioMencionado.textContent = username;
      if (textoOriginal) textoOriginal.textContent = texto;
      if (avatarPublicacion) avatarPublicacion.src = foto;
      if (idPadreRespuesta) idPadreRespuesta.value = postId;
      const tipoPadreInput = document.getElementById("tipoPadre");
      if (tipoPadreInput) tipoPadreInput.value = btn.dataset.tipo || "publicacion";
      
      if (imagenUrl && imagenPublicacion) {
        imagenPublicacion.src = imagenUrl;
        imagenPublicacion.style.display = "block";
      } else if (imagenPublicacion) {
        imagenPublicacion.style.display = "none";
      }

      abrirModalRespuesta();
    });
  });

  document.addEventListener("click", (e) => {
    if (modal && modal.style.display === "flex" &&
        !document.querySelector(".contenido-modal").contains(e.target)) {
      cerrarModal();
    }
  });

  // Cerrar modal al hacer clic en el botón Cancelar
  const btnCancelarModal = document.getElementById("btnCancelarModal");
  if (btnCancelarModal) {
    btnCancelarModal.addEventListener("click", (e) => {
      e.preventDefault();
      cerrarModal();
    });
  }

  // Cerrar modal al presionar la tecla Esc
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      cerrarModal();
    }
  });

  // Funciones para abrir y cerrar el modal
  function abrirModalRespuesta() {
    modal.style.display = "flex";
  }
  
  function cerrarModal() {
    modal.style.display = "none";
  }

  // Enviar comentario desde el modal
  const btnEnviarComentario = document.getElementById("btnEnviarComentario");
  if (btnEnviarComentario) {
    btnEnviarComentario.addEventListener("click", () => {
      const texto = document.getElementById("inputRespuesta").value.trim();
      const publicacionId = document.getElementById("idPublicacionOriginal").value;
      const comentarioId = document.getElementById("idPadreRespuesta").value;

      if (!texto) {
        mostrarToast(gettext("Debes escribir algo para responder."));
        return;
      }

      const formData = new FormData();
      formData.append("texto", texto);
      formData.append("publicacion_id", publicacionId);
      if (comentarioId) {
        formData.append("comentario_id", comentarioId);
      }

      fetch("/app/comentar/", {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": getCSRFToken() }
      })
      .then(response => response.json())
      .then(data => {
        if (data.ok) {
          mostrarToast(gettext("Comentario publicado"));
          cerrarModal();
          document.getElementById("inputRespuesta").value = "";

          // Insertar el nuevo comentario dinámicamente
          const contenedorComentarios = document.querySelector(".comentarios");

          if (contenedorComentarios && data.comentario) {
            const nuevoComentario = document.createElement("div");
            nuevoComentario.classList.add("comentario");
            nuevoComentario.innerHTML = `
              <img src="${data.comentario.foto}" alt="${data.comentario.nombre}" />
              <div class="contenido">
                <div class="usuario">
                  <strong>${data.comentario.nombre}</strong>
                  <span>@${data.comentario.username} · ahora</span>
                </div>
                <p>${data.comentario.texto}</p>
                <div class="acciones">
                  <span><i class="far fa-star"></i> 0</span>
                  <span><i class="far fa-comment comentario-btn" data-usuario="@${data.comentario.username}"></i> 0</span>
                </div>
                <div class="meta">${data.comentario.fecha}</div>
              </div>
            `;

            const tipoPadre = document.getElementById("tipoPadre")?.value || "publicacion";
            if (comentarioId) {
              // Solo mostramos visualmente si:
              // - tipoPadre = comentario y estamos en hilo_comentario
              // - tipoPadre = publicacion (no hacemos nada en ese caso)

              const esHilo = document.getElementById("hilo_comentario_activo") !== null;
              const esPrincipalComentario = esHilo && tipoPadre === "comentario";

              if (esPrincipalComentario) {
                const contenedor = document.querySelector(".comentarios");
                if (contenedor) {
                  const h3 = contenedor.querySelector("h3");
                  if (h3) {
                    h3.insertAdjacentElement("afterend", nuevoComentario);
                  } else {
                    contenedor.appendChild(nuevoComentario);
                  }

                  // Eliminar mensaje de vacío
                  const mensajeVacio = contenedor.querySelector("p");
                  if (mensajeVacio && mensajeVacio.textContent.includes(gettext("No hay respuestas aún."))) {
                    mensajeVacio.remove();  
                  }
                }
              }
              // Si no es respuesta al comentario principal del hilo no se inserta visualmente
            } else {
              // Comentario a la publicación entonces si se muestra
              const contenedor = document.querySelector(".comentarios");
              if (contenedor) {
                const h3 = contenedor.querySelector("h3");
                if (h3) {
                  h3.insertAdjacentElement("afterend", nuevoComentario);
                } else {
                  contenedor.appendChild(nuevoComentario);
                }

                const mensajeVacio = contenedor.querySelector("p");
                if (mensajeVacio && mensajeVacio.textContent.includes(gettext("Sin comentarios"))) {
                  mensajeVacio.remove();  
                }
              }
            }

            // Eliminar mensaje de "Sin comentarios"
            const mensajeVacio = contenedorComentarios.querySelector("p");
            if (mensajeVacio && mensajeVacio.textContent.includes(gettext("Sin comentarios"))) {
              mensajeVacio.remove();  
            }
          }
        } else {
          alert(gettext("Error: " + (data.error || "No se pudo comentar")));
        }
      })
      .catch(() => {
        alert(gettext("Error de red al intentar comentar"));
      });
    });
  }

  // Comentario rápido desde input principal
  const inputRapido = document.getElementById("respuestaRapida");
  const btnRapido = document.getElementById("btnResponderRapido");

  if (btnRapido && inputRapido) {
    btnRapido.addEventListener("click", () => {
      const texto = inputRapido.value.trim();
      const publicacionId = btnRapido.dataset.publicacionId;
      const comentarioId = btnRapido.dataset.comentarioId;

      if (!texto) {
        mostrarToast("Debes escribir algo para responder.");
        return;
      }

      const formData = new FormData();
      formData.append("texto", texto);
      formData.append("publicacion_id", publicacionId);
      if (comentarioId) {
        formData.append("comentario_id", comentarioId);
      }

      fetch("/app/comentar/", {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": getCSRFToken()
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.ok) {
          mostrarToast("Comentario publicado");
          cerrarModal();
          document.getElementById("inputRespuesta").value = "";

          // Insertar el nuevo comentario dinámicamente
          const contenedorComentarios = document.querySelector(".comentarios");
          const inputRapido = document.querySelector(".form-respuesta input[type='text']");

          if (contenedorComentarios && data.comentario) {
            const nuevoComentario = document.createElement("div");
            const respuestasVacias = contenedorComentarios.querySelector(".respuestas-vacias");
            if (respuestasVacias) {
              respuestasVacias.remove();
            }
            nuevoComentario.classList.add("comentario", "respuesta");
            nuevoComentario.innerHTML = `
              <img src="${data.comentario.foto}" alt="${data.comentario.nombre}" />
              <div class="contenido">
                <div class="usuario">
                  <strong>${data.comentario.nombre}</strong>
                  <span>@${data.comentario.username} · ahora</span>
                </div>
                <a href="/app/comentario/${data.comentario.id}/" class="comentario comentario-clickable">
                  <p>${data.comentario.texto}</p>
                </a>
                <div class="acciones">
                  <span><i class="far fa-star"></i> 0</span>
                  <span><i class="far fa-comment comentario-btn" data-usuario="@${data.comentario.username}"></i> 0</span>
                </div>
                <a href="/app/comentario/${data.comentario.id}/" class="comentario comentario-clickable"> 
                  <div class="meta">${data.comentario.fecha}</div>
                </a>
              </div>
            `;

            if (inputRapido) {
              inputRapido.value = "";
            }

            // Insertarlo justo después del título <h3>Comentarios</h3>
            const h3 = contenedorComentarios.querySelector("h3");
            if (h3) {
              h3.insertAdjacentElement("afterend", nuevoComentario);
            } else {
              contenedorComentarios.appendChild(nuevoComentario);
            }

            // Eliminar mensaje de "Sin comentarios"
            const mensajeVacio = contenedorComentarios.querySelector("p");
            if (mensajeVacio && mensajeVacio.textContent.includes(gettext("Sin comentarios"))) {
              mensajeVacio.remove();
            }
          }
        } else {
          alert(gettext("Error: " + (data.error || "No se pudo comentar")));
        }
      })
      .catch(() => {
        alert(gettext("Error de red al intentar comentar"));
      });
    });
  }
  // Dar Estrellas
  document.querySelectorAll('.estrella').forEach(el => {
    el.addEventListener('click', function () {
      if (this.classList.contains('marcada')) return;

      const id = this.dataset.id;
      fetch(`/app/publicacion/${id}/estrella/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
        },
      })
      .then(response => response.json())
      .then(data => {
        if (data.ok) {
          this.querySelector('.contador').textContent = data.nuevas_estrellas;
          this.classList.add('marcada');
          this.querySelector('i').style.color = 'gold';
        }
      });
    });
  });

  // Función para obtener el CSRF token desde cookies
  function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return "";
  }
});
