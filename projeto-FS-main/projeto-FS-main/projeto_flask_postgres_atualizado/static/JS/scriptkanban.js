// Pega os elementos do HTML que vamos usar
const todoInput = document.querySelector(".todo-input");
const todoButton = document.querySelector(".todo-button");
const todoList = document.querySelector(".todo-list");
const filterOption = document.querySelector(".filter-todo");

// EVENTOS: quando a página carrega, e cliques nos botões
document.addEventListener("DOMContentLoaded", loadTasksFromBackend); // carrega tarefas do backend ao abrir
todoButton.addEventListener("click", addTodo); // adiciona nova tarefa
todoList.addEventListener("click", deleteCheck); // lidar com completar ou deletar tarefa
filterOption.addEventListener("change", filterTodo); // filtra tarefas por status

// Função para adicionar nova tarefa ao kanban
function addTodo(event) {
    event.preventDefault(); // evita que a página recarregue

    const taskText = todoInput.value.trim(); // pega o texto e tira espaços extras
    if (!taskText) return; // se o texto estiver vazio, sai da função

    // Envia a tarefa pro backend salvar no banco
    fetch("/kanban", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: taskText })
    })
    .then(response => {
        if (!response.ok) throw new Error("Erro ao salvar tarefa.");
        return response.json(); // espera o backend responder com os dados da tarefa criada
    })
    .then(data => {
        // Cria o elemento da tarefa no DOM, já com o id vindo do backend
        createTodoElement(taskText, false, data.id);
        todoInput.value = ""; // limpa o campo de texto
    })
    .catch(error => {
        console.error("Erro:", error);
        alert("Erro ao adicionar tarefa.");
    });
}

// Função que cria visualmente a tarefa na lista
function createTodoElement(taskText, isCompleted = false, taskId = null) {
    const todoDiv = document.createElement("div");
    todoDiv.classList.add("todo");
    if (isCompleted) todoDiv.classList.add("completed"); // marca como concluída se for o caso
    if (taskId) todoDiv.dataset.id = taskId; // guarda o id da tarefa para futuras ações

    const newTodo = document.createElement("li");
    newTodo.innerText = taskText;
    newTodo.classList.add("todo-item");
    todoDiv.appendChild(newTodo);

    // Botão para marcar como completo
    const completedButton = document.createElement("button");
    completedButton.innerHTML = '<i class="fas fa-check-circle"></i>';
    completedButton.classList.add("complete-btn");
    todoDiv.appendChild(completedButton);

    // Botão para deletar tarefa
    const trashButton = document.createElement("button");
    trashButton.innerHTML = '<i class="fas fa-trash"></i>';
    trashButton.classList.add("trash-btn");
    todoDiv.appendChild(trashButton);

    // Adiciona a tarefa na lista do DOM
    todoList.appendChild(todoDiv);
}

// Função que lida com clique para completar ou deletar tarefa
function deleteCheck(e) {
    const item = e.target;

    // Se clicou no botão de deletar
    if (item.classList.contains("trash-btn")) {
        const todo = item.parentElement;
        const taskId = todo.dataset.id;

        if (!taskId) {
            console.error("Task ID não encontrado para exclusão.");
            return;
        }

        // Pede pro backend deletar a tarefa
        fetch("/kanban_delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: taskId })
        })
        .then(response => {
            if (!response.ok) throw new Error("Erro ao deletar");
            // Faz animação de "deslizar" e depois remove do DOM
            todo.classList.add("slide");
            todo.addEventListener("transitionend", () => todo.remove());
        })
        .catch(error => console.error("Erro ao deletar:", error));
    }

    // Se clicou no botão de completar
    if (item.classList.contains("complete-btn")) {
        const todo = item.parentElement;
        const taskId = todo.dataset.id;

        if (!taskId) {
            console.error("Task ID não encontrado para atualizar status.");
            return;
        }

        // Define o novo status (1 para concluído, 0 para pendente)
        const newStatus = !todo.classList.contains("completed") ? 1 : 0;

        // Atualiza o status da tarefa no backend
        fetch("/kanban_status", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: taskId, status: newStatus })
        })
        .then(response => {
            if (!response.ok) throw new Error("Erro ao atualizar status");
            // Atualiza visualmente o status na tela
            todo.classList.toggle("completed");
        })
        .catch(error => console.error("Erro ao atualizar status:", error));
    }
}

// Função para filtrar as tarefas (todas, completas ou incompletas)
function filterTodo(e) {
    const todos = todoList.childNodes;
    todos.forEach(function(todo) {
        if (!(todo instanceof Element)) return; // ignora nós de texto
        switch (e.target.value) {
            case "all":
                todo.style.display = "flex"; // mostra todas
                break;
            case "completed":
                // mostra só as completadas
                todo.style.display = todo.classList.contains("completed") ? "flex" : "none";
                break;
            case "incomplete":
                // mostra só as que não estão completas
                todo.style.display = !todo.classList.contains("completed") ? "flex" : "none";
                break;
        }
    });
}

// Função que carrega as tarefas já salvas no backend quando a página abre
function loadTasksFromBackend() {
    fetch("/carregar_kanban")
        .then(response => {
            if (!response.ok) throw new Error("Erro ao buscar tarefas.");
            return response.json();
        })
        .then(tasks => {
            // Para cada tarefa vinda do backend, cria um elemento na lista
            tasks.forEach(task => {
                createTodoElement(task.task, task.status, task.id);
            });
        })
        .catch(error => {
            console.error("Erro ao carregar tarefas:", error);
        });
}
