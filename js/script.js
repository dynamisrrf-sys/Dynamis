// ==========================================================
// DYNAMIS — script.js
// JavaScript utilizado apenas onde necessário (envio dos
// formulários de Login e Cadastro). Substitua os alerts pela
// integração real com o backend quando estiver disponível.
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {
  const cadastroForm = document.getElementById('cadastro-form');
  if (cadastroForm) {
    cadastroForm.addEventListener('submit', (e) => {
      e.preventDefault();
      alert('Cadastro enviado! Conecte este formulário ao seu backend.');
    });
  }

  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      alert('Login enviado! Conecte este formulário ao seu backend.');
    });
  }
});
