document.addEventListener("DOMContentLoaded", () => {
    // Abrir modal de respuesta
    const botonesComentar = document.querySelectorAll(".comentario-btn");
    const modal = document.getElementById("modalRespuesta");
  
    botonesComentar.forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const isMobile = window.innerWidth <= 876;
  
        if (isMobile) {
          window.location.href = "/app/reply_mobile/";
        } else {
          abrirModalRespuesta();
        }
      });
    });
  
    document.addEventListener("click", (e) => {
      if (
        modal &&
        modal.style.display === "flex" &&
        !document.querySelector(".contenido-modal").contains(e.target)
      ) {
        cerrarModal();
      }
    });
  
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        cerrarModal();
      }
    });
  
    function abrirModalRespuesta() {
      document.getElementById("modalRespuesta").style.display = "flex";
    }
  
    function cerrarModal() {
      document.getElementById("modalRespuesta").style.display = "none";
    }
  
    // Expansión dinámica del textarea
    const textarea = document.querySelector(".crear-post textarea");
    if (textarea) {
      textarea.addEventListener("input", () => {
        textarea.style.height = "auto";
        textarea.style.height = textarea.scrollHeight + "px";
      });
    }
  
    // Selector de privacidad
    window.seleccionarPrivacidad = function (valor) {
      document.getElementById("valorPrivacidad").textContent = valor;
      document.getElementById("togglePrivacidad").checked = false;
  
      const inputPriv = document.getElementById("inputPrivacidad");
      if (inputPriv) {
        inputPriv.value = valor === "Público" ? "publica" : "privada";
      }
    };
  
    // Interacción con estrellas
    document.querySelectorAll('.estrella').forEach(el => {
      el.addEventListener('click', function () {
        if (this.classList.contains('marcada')) return; // Ya marcada
    
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


    const inputArchivo = document.getElementById('archivoInput');
    const preview = document.getElementById('previewImagen');
    const imgTag = document.getElementById('imagenPreview');

    if (inputArchivo && preview && imgTag) {
      inputArchivo.addEventListener('change', function () {
        const archivo = this.files[0];
        if (archivo) {
          const lector = new FileReader();
          lector.onload = function (e) {
            imgTag.src = e.target.result;
            preview.style.display = 'block';
          }
          lector.readAsDataURL(archivo);
        } else {
          preview.style.display = 'none';
        }
      });
    }
  
    // Extraer token CSRF desde cookies
    function getCSRFToken() {
      const name = "csrftoken";
      const cookies = document.cookie.split(";");
  
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          return decodeURIComponent(cookie.substring(name.length + 1));
        }
      }
      return "";
    }
  });
  