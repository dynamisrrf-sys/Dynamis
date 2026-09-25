import { api, clearSession, formToJson, getSession } from './api.js';

if (!getSession()?.access_token) window.location.replace('login.html');

const state = { profile: null, opportunities: [], surpluses: [], reservations: [] };
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
  })[character]);
}

function toast(message, type = 'success') {
  const element = $('[data-toast]');
  element.textContent = message;
  element.dataset.type = type;
  element.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { element.hidden = true; }, 3200);
}

function formatDate(value) {
  if (!value) return '—';
  return new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' }).format(new Date(`${value}T12:00:00Z`));
}

function money(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value || 0));
}

function setView(name) {
  $$('.app-view').forEach((view) => view.classList.toggle('is-active', view.dataset.view === name));
  $$('[data-view-target]').forEach((button) => button.classList.toggle('is-active', button.dataset.viewTarget === name));
  $('[data-sidebar]').classList.remove('is-open');
}

$$('[data-view-target]').forEach((button) => button.addEventListener('click', () => setView(button.dataset.viewTarget)));
$('[data-sidebar-toggle]').addEventListener('click', () => $('[data-sidebar]').classList.toggle('is-open'));
$('[data-logout]').addEventListener('click', () => { clearSession(); window.location.replace('login.html'); });

async function loadProfile() {
  state.profile = await api('/perfil/me');
  if (!state.profile.tipo_perfil) throw new Error('Seu usuário ainda não possui um perfil DYNAMIS.');
  const data = state.profile.dados;
  $('[data-profile-name]').textContent = data.nome;
  $('[data-profile-type]').textContent = state.profile.tipo_perfil.replace('_', ' ');
  $$('[data-role]').forEach((element) => { element.hidden = element.dataset.role !== state.profile.tipo_perfil; });
}

async function loadSurpluses() {
  if (state.profile.tipo_perfil !== 'estabelecimento') return;
  state.surpluses = await api('/excedentes/meus');
  $('[data-surpluses]').innerHTML = state.surpluses.length ? state.surpluses.map((item) => `<tr><td><strong>${escapeHtml(item.nome)}</strong><br><small>${escapeHtml(item.categoria)}</small></td><td>${escapeHtml(item.quantidade)} ${escapeHtml(item.unidade_medida)}</td><td>${formatDate(item.validade)}</td><td>${escapeHtml(item.urgencia || 'normal')}</td><td><span class="status-badge">${escapeHtml(item.status)}</span></td></tr>`).join('') : '<tr><td colspan="5">Nenhum excedente cadastrado.</td></tr>';
}

async function loadOpportunities() {
  if (state.profile.tipo_perfil !== 'consumidor') return;
  state.opportunities = await api('/excedentes/disponiveis');
  renderOpportunities();
}

function renderOpportunities() {
  const term = ($('[data-search]')?.value || '').toLowerCase();
  const type = $('[data-type-filter]')?.value || '';
  const items = state.opportunities.filter((item) => (!term || `${item.nome} ${item.categoria}`.toLowerCase().includes(term)) && (!type || item.tipo_destinacao === type));
  $('[data-opportunities]').innerHTML = items.length ? items.map((item) => `<article class="opportunity-card"><header><span class="destination-badge">${escapeHtml(item.tipo_destinacao)}</span><span>${escapeHtml(item.urgencia)}</span></header><h2>${escapeHtml(item.nome)}</h2><p>${escapeHtml(item.estabelecimento)} · ${escapeHtml(item.cidade || item.local)}</p><div class="opportunity-meta"><span>Disponível<strong>${escapeHtml(item.quantidade_disponivel)} ${escapeHtml(item.unidade_medida)}</strong></span><span>Validade<strong>${formatDate(item.validade)}</strong></span><span>Retirada<strong>${escapeHtml(item.local)}</strong></span><span>Data<strong>${formatDate(item.data_inicio)}</strong></span></div><footer><strong>${Number(item.preco_final) > 0 ? money(item.preco_final) : 'Gratuito'}</strong><button data-reserve="${item.id_destinacao}">Reservar</button></footer></article>`).join('') : '<p class="empty-state">Nenhuma oportunidade encontrada.</p>';
  $$('[data-reserve]').forEach((button) => button.addEventListener('click', () => openReserveDialog(Number(button.dataset.reserve))));
}

function openReserveDialog(id) {
  const item = state.opportunities.find((opportunity) => Number(opportunity.id_destinacao) === id);
  if (!item) return;
  const form = $('[data-reserve-form]');
  form.reset();
  form.elements.id_destinacao.value = item.id_destinacao;
  form.elements.quantidade.max = item.quantidade_disponivel;
  form.elements.quantidade.value = Math.min(1, Number(item.quantidade_disponivel));
  $('[data-reserve-name]').textContent = item.nome;
  $('[data-reserve-description]').textContent = `${item.estabelecimento} · retirada em ${item.local}`;
  $('[data-reserve-limit]').textContent = `Disponível: ${item.quantidade_disponivel} ${item.unidade_medida}`;
  $('[data-reserve-dialog]').showModal();
}

$('[data-reserve-form]').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    await api('/reservas', { method: 'POST', body: JSON.stringify({ id_destinacao: Number(form.elements.id_destinacao.value), quantidade: Number(form.elements.quantidade.value) }) });
    toast('Reserva criada. Consulte o código em Minhas reservas.');
    $('[data-reserve-dialog]').close();
    await Promise.all([loadOpportunities(), loadReservations()]);
  } catch (error) { toast(error.message, 'error'); }
  finally { button.disabled = false; }
});

async function loadReservations() {
  if (state.profile.tipo_perfil !== 'consumidor') return;
  state.reservations = await api('/reservas');
  $('[data-reservations]').innerHTML = state.reservations.length ? state.reservations.map((item) => {
    const destination = item.consumidor_destinacao?.destinacao;
    const surplus = destination?.classificacao?.excedente;
    return `<tr><td>${escapeHtml(surplus?.nome || 'Excedente')}</td><td>${formatDate(item.data_retirada || destination?.data_inicio)} ${escapeHtml(item.horario_retirada || destination?.horario_inicio)}</td><td><strong>${escapeHtml(item.codigo_retirada || '—')}</strong></td><td>${money(item.valor_total)}</td><td><span class="status-badge">${escapeHtml(item.status)}</span></td></tr>`;
  }).join('') : '<tr><td colspan="5">Você ainda não possui reservas.</td></tr>';
}

async function loadDestinationTypes() {
  if (state.profile.tipo_perfil !== 'estabelecimento') return;
  const types = await api('/tipos-destinacao');
  $('[data-destination-types]').innerHTML = '<option value="">Selecione</option>' + types.map((item) => `<option value="${item.id_tipo_destinacao}">${escapeHtml(item.nome)}</option>`).join('');
}

function updateSummary() {
  const values = state.profile.tipo_perfil === 'estabelecimento'
    ? [state.surpluses.filter((item) => !['concluido', 'cancelado'].includes(item.status)).length, state.surpluses.filter((item) => item.status === 'disponivel').length, '—']
    : ['—', state.opportunities.length, state.reservations.length];
  $$('[data-summary] strong').forEach((element, index) => { element.textContent = values[index]; });
}

async function loadAll() {
  try {
    await loadProfile();
    await Promise.all([loadSurpluses(), loadOpportunities(), loadReservations(), loadDestinationTypes()]);
    updateSummary();
  } catch (error) {
    toast(error.message, 'error');
    if (/autentica|token|sessão/i.test(error.message)) { clearSession(); setTimeout(() => window.location.replace('login.html'), 1200); }
  }
}

$('[data-refresh]').addEventListener('click', loadAll);
$('[data-search]')?.addEventListener('input', renderOpportunities);
$('[data-type-filter]')?.addEventListener('change', renderOpportunities);
$$('[data-new-surplus]').forEach((button) => button.addEventListener('click', () => $('[data-surplus-dialog]').showModal()));

async function submitForm(form, path, successMessage, afterSubmit) {
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const payload = formToJson(form);
    Object.keys(payload).forEach((key) => {
      if (['id_excedente','id_classificacao','id_tipo_destinacao'].includes(key)) payload[key] = Number(payload[key]);
      if (['quantidade','preco_original','preco_final'].includes(key)) payload[key] = Number(payload[key]);
      if (key === 'aptidao_consumo') payload[key] = payload[key] === 'true';
    });
    await api(path, { method: 'POST', body: JSON.stringify(payload) });
    form.reset(); toast(successMessage); await afterSubmit?.();
  } catch (error) { toast(error.message, 'error'); }
  finally { button.disabled = false; }
}

$('[data-surplus-form]').addEventListener('submit', async (event) => { event.preventDefault(); await submitForm(event.currentTarget, '/excedentes', 'Excedente cadastrado.', async () => { $('[data-surplus-dialog]').close(); await loadSurpluses(); updateSummary(); }); });
$('[data-classification-form]').addEventListener('submit', async (event) => { event.preventDefault(); await submitForm(event.currentTarget, '/classificacoes', 'Classificação registrada.', loadSurpluses); });
$('[data-destination-form]').addEventListener('submit', async (event) => { event.preventDefault(); await submitForm(event.currentTarget, '/destinacoes', 'Destinação publicada.', loadSurpluses); });

loadAll();
