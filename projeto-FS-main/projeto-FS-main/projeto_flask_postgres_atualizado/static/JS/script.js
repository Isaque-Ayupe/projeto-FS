// Quando clicar no botão com id 'open_btn', alterna (abre/fecha) a sidebar
document.getElementById('open_btn').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('open-sidebar'); 
    // Se a sidebar estiver fechada, abre; se estiver aberta, fecha
});
