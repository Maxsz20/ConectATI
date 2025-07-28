document.addEventListener('DOMContentLoaded', () => {
  const gettext = django.gettext;
  const eliminarBtn = document.getElementById('btnEliminarFoto'); 
  const profileImage = document.getElementById('profileImage');
  const inputFoto = document.getElementById('inputFotoArchivo');
  let valorFotoOriginal = "{{ usuario_logueado.foto|default:'' }}";

  function mostrarToast(mensaje) {
    const toast = document.getElementById("toast");
    const mensajeEl = document.getElementById("toastMensaje");
    mensajeEl.textContent = mensaje;

    toast.style.display = "block";

    setTimeout(() => {
      toast.style.display = "none";
    }, 3000);
  }

  if (inputFoto && profileImage) {
    inputFoto.addEventListener('change', () => {
      const archivo = inputFoto.files[0];
      if (archivo) {
        const reader = new FileReader();
        reader.onload = function (e) {
          profileImage.src = e.target.result;
        };
        reader.readAsDataURL(archivo);

        const formData = new FormData();
        formData.append('foto_archivo', archivo);

        fetch("{% url 'editprofile' %}", {
          method: "POST",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: formData
        })
        .then(res => res.json())
        .then(data => {
          if (data.ok && data.foto_url) {
            profileImage.src = data.foto_url + "?t=" + new Date().getTime();
            valorFotoOriginal = data.foto_url;
            mostrarToast(gettext("Foto subida exitosamente"));
          } else {
            alert(gettext("Error al subir la foto"));
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert(gettext("Error al comunicarse con el servidor"));
        });
      }
    });
  }

  if (eliminarBtn) {
    eliminarBtn.addEventListener('click', () => {
      if (inputFoto.files.length > 0) {
        inputFoto.value = "";
        if (valorFotoOriginal !== "") {
          profileImage.src = valorFotoOriginal;
        } else {
          profileImage.src = "{% static 'images/default_user.avif' %}";
        }
      } else if (valorFotoOriginal !== "") {
        fetch("{% url 'eliminar_foto_perfil' %}", {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.ok) {
            profileImage.src = "{% static 'images/default_user.avif' %}";
            valorFotoOriginal = "";
          } else {
            alert(gettext("Error al eliminar la foto"));
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert(gettext("Error al comunicarse con el servidor"));
        });
      }
    });
  }
});