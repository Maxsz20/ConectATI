document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modalRespuesta");
  const avatarPublicacion = document.getElementById("avatarPublicacion");
  const nombreAutor = document.getElementById("nombreAutor");
  const textoOriginal = document.getElementById("textoOriginal");
  const usuarioMencionado = document.getElementById("usuarioMencionado");
  const idPadreRespuesta = document.getElementById("idPadreRespuesta");
  const imagenPublicacion = document.getElementById("imagen-publicacion");

  function mostrarToast(mensaje) {
    const toast = document.getElementById("toast");
    const mensajeEl = document.getElementById("toastMensaje");
    mensajeEl.textContent = mensaje;

    toast.style.display = "block";

    setTimeout(() => {
      toast.style.display = "none";
    }, 3000);
  }

  document.querySelectorAll(".comentario-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isMobile = window.innerWidth <= 876;
      if (isMobile) {
        const postId = btn.dataset.id;
        window.location.href = `/app/reply_mobile/${postId}/`;
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

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      cerrarModal();
    }
  });

  function abrirModalRespuesta() {
    modal.style.display = "flex";
  }

  function cerrarModal() {
    modal.style.display = "none";
  }

  const btnEnviarComentario = document.getElementById("btnEnviarComentario");
  if (btnEnviarComentario) {
    btnEnviarComentario.addEventListener("click", () => {
      const texto = document.getElementById("inputRespuesta").value.trim();
      const publicacionId = document.getElementById("idPadreRespuesta").value;
      if (!texto) {
        mostrarToast("Debes escribir algo para responder.");
        return;
      }

      const formData = new FormData();
      formData.append("texto", texto);
      formData.append("publicacion_id", publicacionId);

      fetch("/app/comentar/", {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": getCSRFToken() }
      })
      .then(response => response.json())
      .then(data => {
        if (data.ok) {
          mostrarToast("Comentario publicado");
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

            // Insertarlo justo después del título <h3>Comentarios</h3>
            const h3 = contenedorComentarios.querySelector("h3");
            if (h3) {
              h3.insertAdjacentElement("afterend", nuevoComentario);
            } else {
              contenedorComentarios.appendChild(nuevoComentario);
            }

            // Eliminar mensaje de "Sin comentarios"
            const mensajeVacio = contenedorComentarios.querySelector("p");
            if (mensajeVacio && mensajeVacio.textContent.includes("Sin comentarios")) {
              mensajeVacio.remove();
            }
          }
        } else {
          alert("Error: " + (data.error || "No se pudo comentar"));
        }
      })
      .catch(() => {
        alert("Error de red al intentar comentar");
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

      if (!texto) {
        mostrarToast("Debes escribir algo para responder.");
        return;
      }

      const formData = new FormData();
      formData.append("texto", texto);
      formData.append("publicacion_id", publicacionId);

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
            if (mensajeVacio && mensajeVacio.textContent.includes("Sin comentarios")) {
              mensajeVacio.remove();
            }
          }
        } else {
          alert("Error: " + (data.error || "No se pudo comentar"));
        }
      })
      .catch(() => {
        alert("Error de red al intentar comentar");
      });
    });
  }




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
