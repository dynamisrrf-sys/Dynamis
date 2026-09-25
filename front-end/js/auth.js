import { api, getSession, saveSession, formToJson } from './api.js';

if (getSession()?.access_token) window.location.replace('app.html');

const form = document.querySelector('[data-auth-form]');
const feedback = document.querySelector('[data-auth-feedback]');

function showFeedback(message, type = 'error') {
  if (!feedback) return;
  feedback.textContent = message;
  feedback.dataset.type = type;
  feedback.hidden = false;
}

form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  const original = button.textContent;
  button.disabled = true;
  button.textContent = 'Aguarde…';
  feedback.hidden = true;

  try {
    const payload = formToJson(form);
    const isSignup = form.dataset.authForm === 'cadastro';
    const result = await api(isSignup ? '/auth/cadastro' : '/auth/login', {
      method: 'POST', body: JSON.stringify(payload),
    });
    if (result.access_token) {
      saveSession(result);
      window.location.replace('app.html');
      return;
    }
    showFeedback(result.message || 'Confira seu e-mail para concluir o cadastro.', 'success');
    form.reset();
  } catch (error) {
    showFeedback(error.message);
  } finally {
    button.disabled = false;
    button.textContent = original;
  }
});

const profileType = document.querySelector('#tipo_perfil');
const documentLabel = document.querySelector('[data-document-label]');
const responsibleGroup = document.querySelector('[data-responsible-group]');
const updateProfileFields = () => {
  if (!profileType) return;
  const consumer = profileType.value === 'consumidor';
  documentLabel.textContent = consumer ? 'CPF' : 'CNPJ';
  document.querySelector('#documento').placeholder = consumer ? '000.000.000-00' : '00.000.000/0000-00';
  responsibleGroup.hidden = consumer;
};
profileType?.addEventListener('change', updateProfileFields);
updateProfileFields();
