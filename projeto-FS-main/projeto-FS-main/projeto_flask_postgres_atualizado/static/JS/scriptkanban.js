const todoInput = document.querySelector(".todo-input");
const todoButton = document.querySelector(".todo-button");
const todoList = document.querySelector(".todo-list");
const filterOption = document.querySelector(".filter-todo");

// EVENTOS
document.addEventListener("DOMContentLoaded", loadTasksFromBackend);
todoButton.addEventListener("click", addTodo);
todoList.addEventListener("click", deleteCheck);
filterOption.addEventListener("change", filterTodo);

// ADICIONAR TAREFA AO KANBAN
function addTodo(event) {
    event.preventDefault();

    const taskText = todoInput.value.trim();
    if (!taskText) return;

    fetch("/kanban", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: taskText })
    })
    .then(response => {
        if (!response.ok) throw new Error("Erro ao salvar tarefa.");
        return response.json();
    })
    .then(data => {
        // Supondo que o backend retorne o objeto da tarefa criada com o id
        createTodoElement(taskText, false, data.id);
        todoInput.value = "";
    })
    .catch(error => {
        console.error("Erro:", error);
        alert("Erro ao adicionar tarefa.");
    });
}

// CRIA ELEMENTO NO DOM
function createTodoElement(taskText, isCompleted = false, taskId = null) {
    const todoDiv = document.createElement("div");
    todoDiv.classList.add("todo");
    if (isCompleted) todoDiv.classList.add("completed");
    if (taskId) todoDiv.dataset.id = taskId;

    const newTodo = document.createElement("li");
    newTodo.innerText = taskText;
    newTodo.classList.add("todo-item");
    todoDiv.appendChild(newTodo);

    const completedButton = document.createElement("button");
    completedButton.innerHTML = '<i class="fas fa-check-circle"></i>';
    completedButton.classList.add("complete-btn");
    todoDiv.appendChild(completedButton);

    const trashButton = document.createElement("button");
    trashButton.innerHTML = '<i class="fas fa-trash"></i>';
    trashButton.classList.add("trash-btn");
    todoDiv.appendChild(trashButton);

    todoList.appendChild(todoDiv);
}

// CLIQUES: COMPLETAR / REMOVER
function deleteCheck(e) {
    const item = e.target;

    if (item.classList.contains("trash-btn")) {
        const todo = item.parentElement;
        const taskId = todo.dataset.id;

        if (!taskId) {
            console.error("Task ID não encontrado para exclusão.");
            return;
        }

        fetch("/kanban/delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: taskId })
        })
        .then(response => {
            if (!response.ok) throw new Error("Erro ao deletar");
            todo.classList.add("slide");
            todo.addEventListener("transitionend", () => todo.remove());
        })
        .catch(error => console.error("Erro ao deletar:", error));
    }

    if (item.classList.contains("complete-btn")) {
        const todo = item.parentElement;
        const taskId = todo.dataset.id;

        if (!taskId) {
            console.error("Task ID não encontrado para atualizar status.");
            return;
        }

        const newStatus = !todo.classList.contains("completed") ? 1 : 0;

        fetch("/kanban/status", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: taskId, status: newStatus })
        })
        .then(response => {
            if (!response.ok) throw new Error("Erro ao atualizar status");
            todo.classList.toggle("completed");
        })
        .catch(error => console.error("Erro ao atualizar status:", error));
    }
}

// FILTRA TAREFAS
function filterTodo(e) {
    const todos = todoList.childNodes;
    todos.forEach(function(todo) {
        if (!(todo instanceof Element)) return; // ignora nós de texto
        switch (e.target.value) {
            case "all":
                todo.style.display = "flex";
                break;
            case "completed":
                todo.style.display = todo.classList.contains("completed") ? "flex" : "none";
                break;
            case "incomplete":
                todo.style.display = !todo.classList.contains("completed") ? "flex" : "none";
                break;
        }
    });
}

// CARREGA AS TAREFAS EXISTENTES
function loadTasksFromBackend() {
    fetch("/carregar_kanban")
        .then(response => {
            if (!response.ok) throw new Error("Erro ao buscar tarefas.");
            return response.json();
        })
        .then(tasks => {
            tasks.forEach(task => {
                createTodoElement(task.task, task.status, task.id);
            });
        })
        .catch(error => {
            console.error("Erro ao carregar tarefas:", error);
        });
}
