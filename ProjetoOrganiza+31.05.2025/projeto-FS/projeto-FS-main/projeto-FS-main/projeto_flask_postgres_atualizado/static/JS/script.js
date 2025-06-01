
async function carregarTarefas(dataSelecionada) {
  const container = document.getElementById('hourly-tasks');
  container.innerHTML = '';

  const res = await fetch(`/tarefas?data=${dataSelecionada}`);
  const tarefas = await res.json();

  for (let hora = 0; hora < 24; hora++) {
    const horaFormatada = hora.toString().padStart(2, '0') + ":00";
    const tarefaTexto = tarefas[horaFormatada] || "";

    const bloco = document.createElement('div');
    bloco.className = 'hora-bloco';

    bloco.innerHTML = `
      <label><strong>${horaFormatada}</strong></label>
      <input type="text" id="tarefa_${horaFormatada}" value="${tarefaTexto}" />
      <button onclick="salvarTarefa('${dataSelecionada}', '${horaFormatada}')">Salvar</button>
    `;

    container.appendChild(bloco);
  }
}

async function salvarTarefa(data, hora) {
  const input = document.getElementById(`tarefa_${hora}`);
  const task = input.value;

  await fetch('/tarefas', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ date: data, hour: hora, task })
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const datePicker = document.getElementById('datePicker');
  const hoje = new Date().toISOString().split('T')[0];
  datePicker.value = hoje;

  carregarTarefas(hoje);

  datePicker.addEventListener('change', () => {
    carregarTarefas(datePicker.value);
  });
});
