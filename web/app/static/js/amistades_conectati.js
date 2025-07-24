document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.aceptar').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      fetch('/app/aceptar-solicitud/', {
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
          // Eliminar solicitud
          const solicitud = btn.closest('.item-solicitud');
          solicitud.remove();

          // Insertar nuevo amigo
          const amigo = data.amigo;
          const nuevo = document.createElement('div');
          nuevo.classList.add('item-amigo');
          nuevo.innerHTML = `
            <img src="${amigo.foto}" alt="${amigo.nombre}" />
            <div class="contenido">
              <strong>@${amigo.username}</strong> <span class="nombre">${amigo.nombre}</span>
              <p>${amigo.descripcion}</p>
            </div>
            <i class="fas fa-user-slash eliminar"></i>
          `;

          const listaAmigos = document.querySelector('.lista-amigos');
          if (listaAmigos) {
            listaAmigos.prepend(nuevo); // lo coloca arriba
          }
        }
      });
    });
  });

  document.querySelectorAll('.rechazar').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      fetch('/app/rechazar-solicitud/', {
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
        }
      });
    });
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
});
