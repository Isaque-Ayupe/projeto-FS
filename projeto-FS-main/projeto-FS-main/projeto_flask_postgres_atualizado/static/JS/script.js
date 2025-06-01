
document.getElementById('open_btn').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('open-sidebar');
});

 const monthYear = document.getElementById('month-year');
    const calendarBody = document.getElementById('calendar-body');
    const modal = document.getElementById('event-modal');
    const eventContent = document.getElementById('event-content');

    const months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

    let currentDate = new Date();

    const eventos = {}; // Armazenamento temporário local

    function generateCalendar(date) {
      const year = date.getFullYear();
      const month = date.getMonth();
      const firstDay = new Date(year, month, 1).getDay();
      const daysInMonth = new Date(year, month + 1, 0).getDate();

      monthYear.textContent = `${months[month]} ${year}`;
      calendarBody.innerHTML = '';

      let dateCount = 1;
      for (let i = 0; i < 6; i++) {
        let row = document.createElement('tr');

        for (let j = 0; j < 7; j++) {
          let cell = document.createElement('td');
          cell.setAttribute("style", "padding: 20px 0; border: 1px solid #ddd; cursor: pointer; font-size: 1.1em;");

          if (i === 0 && j < firstDay) {
            cell.textContent = '';
          } else if (dateCount > daysInMonth) {
            break;
          } else {
            const fullDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(dateCount).padStart(2, '0')}`;
            cell.setAttribute("data-date", fullDate);
            cell.textContent = dateCount;

            const today = new Date();
            if (
              dateCount === today.getDate() &&
              month === today.getMonth() &&
              year === today.getFullYear()
            ) {
              cell.style.textDecoration = "underline";
              cell.style.color = "#8c52ff";
              cell.style.fontWeight = "bold";
            }

            cell.addEventListener("click", function () {
              const allCells = document.querySelectorAll('td');
              allCells.forEach(c => c.classList.remove('selected-day'));
              cell.classList.add('selected-day');
              showEvents(fullDate);
            });

            dateCount++;
          }
          row.appendChild(cell);
        }

        calendarBody.appendChild(row);
      }
    }

    function showEvents(dateStr) {
      const eventosDoDia = eventos[dateStr] || [];

      eventContent.innerHTML = eventosDoDia.length > 0
        ? eventosDoDia.map(ev => `<p><strong>${ev.nome}</strong> às ${ev.hora}</p>`).join('')
        : "<p>Não há eventos para este dia.</p>";

      eventContent.innerHTML += `
        <hr style="margin: 10px 0;">
        <h4 style="margin-bottom: 6px;">Adicionar Evento:</h4>
        <input id="event-name" type="text" placeholder="Nome do evento" style="width: 100%; padding: 5px; margin-bottom: 6px;"/>
        <input id="event-time" type="time" style="width: 100%; padding: 5px; margin-bottom: 10px;"/>
        <button onclick="saveEvent('${dateStr}')" style="background: #8c52ff; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer;">Salvar Evento</button>
      `;

      modal.style.display = "flex";
    }

    function saveEvent(dateStr) {
      const name = document.getElementById('event-name').value.trim();
      const time = document.getElementById('event-time').value;

      if (!name || !time) {
        alert("Por favor, preencha o nome e a hora do evento.");
        return;
      }

      fetch("/adicionar-evento", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: dateStr, nome: name, hora: time })
      })
      .then(res => res.json())
      .then(res => {
        if (res.mensagem) {
          alert("Evento salvo com sucesso!");
          if (!eventos[dateStr]) eventos[dateStr] = [];
          eventos[dateStr].push({ nome: name, hora: time });
          showEvents(dateStr);
        } else {
          alert("Erro ao salvar: " + res.erro);
        }
      })
      .catch(err => alert("Erro de conexão com o servidor."));
    }

    function closeModal() {
      modal.style.display = "none";
    }

    function changeMonth(offset) {
      currentDate.setMonth(currentDate.getMonth() + offset);
      generateCalendar(currentDate);
    }

    generateCalendar(currentDate);
