document.addEventListener("DOMContentLoaded", () => {
  const gettext = django.gettext;
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

  // Abrir modal al hacer clic en el ícono de comentar
  document.querySelectorAll(".comentario-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();

      const isMobile = window.innerWidth <= 876;
      if (isMobile) {
        const postId = btn.dataset.id;
        window.location.href = `/app/reply_mobile/${postId}/`;
        return;
      }

      // Cargar datos del post al que se responde
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

  // Cerrar modal al hacer clic fuera del contenido
  document.addEventListener("click", (e) => {
    if (modal && modal.style.display === "flex" &&
        !document.querySelector(".contenido-modal").contains(e.target)) {
      cerrarModal();
    }
  });

  // Cerrar modal con tecla ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
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
      const publicacionId = document.getElementById("idPadreRespuesta").value;

      if (!texto) {
        alert("Debes escribir algo para responder.");
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
      .then(response => response.json())
      .then(data => {
        if (data.ok) {
          mostrarToast(gettext("Comentario publicado"));
          cerrarModal();
          document.getElementById("inputRespuesta").value = "";
          const iconoComentario = document.querySelector(`.comentario-btn[data-id="${publicacionId}"]`);
          if (iconoComentario) {
            const contador = iconoComentario.parentElement.querySelector(".contador-comentarios");
            if (contador) {
              contador.textContent = data.nuevo_total;
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

  // Expansión dinámica del textarea principal (crear post)
  const textarea = document.querySelector(".crear-post textarea");
  if (textarea) {
    textarea.addEventListener("input", () => {
      textarea.style.height = "auto";
      textarea.style.height = textarea.scrollHeight + "px";
    });
  }

  // Selector de privacidad
  window.seleccionarPrivacidad = function (elemento) {
    const valor = elemento.dataset.value;          // publica o privada
    const visible = elemento.dataset.visible;      // PÚBLICO o PRIVATE

    const inputPriv = document.getElementById("inputPrivacidad");
    const label = document.getElementById("valorPrivacidad");
    const toggle = document.getElementById("togglePrivacidad");

    if (inputPriv) inputPriv.value = valor;
    if (toggle) toggle.checked = false;
    if (label) label.textContent = visible;
  };



  // Marcar estrella (like)
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

  // Vista previa de imagen
  const inputArchivo = document.getElementById('archivoInput');
  const preview = document.getElementById('previewImagen');
  const imgTag = document.getElementById('imagenPreview');

  if (inputArchivo && preview && imgTag) {
    inputArchivo.addEventListener('change', function () {
      const archivo = this.files[0];
      if (archivo && archivo.type.startsWith("image/")) {
        const lector = new FileReader();
        lector.onload = function (e) {
          imgTag.src = e.target.result;
          preview.style.display = 'block';
        };
        lector.readAsDataURL(archivo);
      } else {
        preview.style.display = 'none';
        imgTag.src = "#";
      }
    });
  }

  // Validación antes de enviar el formulario de publicación
  const formulario = document.querySelector(".crear-post");
  if (formulario) {
    formulario.addEventListener("submit", function (e) {
      const texto = formulario.querySelector("textarea[name='texto']")?.value.trim();
      const archivo = inputArchivo?.files.length;

      if (!texto && !archivo) {
        e.preventDefault();
        alert(gettext("Debe escribir un texto o subir una imagen para publicar."));
      }
    });
  }

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
