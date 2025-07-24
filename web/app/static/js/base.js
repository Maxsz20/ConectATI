const input = document.getElementById('inputBusqueda');
    const dropdown = document.getElementById('dropdownBuscador');

    if (input && dropdown) {
      input.addEventListener('input', () => {
        const query = input.value.trim();
        const contenedor = dropdown.querySelector('.usuarios-buscados');

        dropdown.classList.remove('oculto');

        if (query.length === 0) {
            contenedor.innerHTML = `
            <p class="sin-resultados">Escribe algo para buscar</p>
            `;
            return;
        }

        fetch(`/app/buscar-usuarios/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
            contenedor.innerHTML = '';

            if (data.usuarios.length === 0) {
                contenedor.innerHTML = '<p class="sin-resultados">Sin resultados</p>';
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
                  ${
                    usuario.estado_amistad === 'aceptada'
                      ? `<i class="fas fa-user-check" title="Ya son amigos"></i>`
                      : usuario.estado_amistad === 'pendiente'
                        ? `<span class="estado-pendiente"><i class="fas fa-clock"></i> Pendiente</span>`
                        : `<button class="btn-agregar" data-id="${usuario.id}">Añadir</button>`
                  }
                `;
                contenedor.appendChild(div);
            });
            });
        });

      input.addEventListener('focus', () => {
        if (input.value.trim().length > 0) {
          dropdown.classList.remove('oculto');
        }
      });

      document.addEventListener('click', function (e) {
        if (!document.querySelector('.buscador').contains(e.target)) {
          dropdown.classList.add('oculto');
        }
      });

      dropdown.addEventListener('click', function (e) {
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
          .then(response => response.json())
          .then(data => {
            console.log("Respuesta del servidor:", data); // 👈 Agrega esto

            if (data.ok) {
              e.target.outerHTML = `
                <span class="solicitud-enviada">
                  <i class="fas fa-paper-plane"></i> Enviada
                </span>`;
            } else {
              e.target.textContent = "Ya enviada";
              e.target.disabled = true;
              e.target.classList.add("btn-error");
            }
          });
        }
      });


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
    }
    input.addEventListener('click', () => {
      dropdown.classList.remove('oculto');
    });