-- DYNAMIS MVP — segurança, catálogo inicial e operações transacionais.
-- Revisar em um ambiente de homologação e executar pelo SQL Editor do Supabase.

begin;

create schema if not exists private;
grant usage on schema private to authenticated;

insert into public.tipo_destinacao (nome, descricao, status)
select item.nome, item.descricao, 'ativo'
from (values
  ('Oferta', 'Comercialização de alimento apto com preço reduzido'),
  ('Doação', 'Destinação social de alimento apto ao consumo humano'),
  ('Destinação ambiental', 'Compostagem, reaproveitamento ou descarte ambiental adequado')
) as item(nome, descricao)
where not exists (
  select 1 from public.tipo_destinacao existente
  where lower(existente.nome) = lower(item.nome)
);

grant select, insert, update on table
  public.estabelecimento,
  public.consumidor,
  public.agente,
  public.excedente,
  public.classificacao,
  public.destinacao,
  public.consumidor_destinacao,
  public.reserva
to authenticated;
grant select on table public.tipo_destinacao to authenticated;
grant usage, select on all sequences in schema public to authenticated;

drop policy if exists reserva_select on public.reserva;
create policy reserva_select_propria
on public.reserva for select
to authenticated
using (
  exists (
    select 1
    from public.consumidor_destinacao cd
    left join public.consumidor c on c.id_consumidor = cd.id_consumidor
    left join public.agente a on a.id_agente = cd.id_agente
    join public.destinacao d on d.id_destinacao = cd.id_destinacao
    join public.classificacao cl on cl.id_classificacao = d.id_classificacao
    join public.excedente ex on ex.id_excedente = cl.id_excedente
    join public.estabelecimento e on e.id_estabelecimento = ex.id_estabelecimento
    where cd.id_consumidor_destinacao = reserva.id_consumidor_destinacao
      and (
        c.auth_user_id = (select auth.uid())
        or a.auth_user_id = (select auth.uid())
        or e.auth_user_id = (select auth.uid())
      )
  )
);

drop policy if exists reserva_update on public.reserva;
create policy reserva_update_participantes
on public.reserva for update
to authenticated
using (
  exists (
    select 1
    from public.consumidor_destinacao cd
    left join public.consumidor c on c.id_consumidor = cd.id_consumidor
    left join public.agente a on a.id_agente = cd.id_agente
    join public.destinacao d on d.id_destinacao = cd.id_destinacao
    join public.classificacao cl on cl.id_classificacao = d.id_classificacao
    join public.excedente ex on ex.id_excedente = cl.id_excedente
    join public.estabelecimento e on e.id_estabelecimento = ex.id_estabelecimento
    where cd.id_consumidor_destinacao = reserva.id_consumidor_destinacao
      and (
        c.auth_user_id = (select auth.uid())
        or a.auth_user_id = (select auth.uid())
        or e.auth_user_id = (select auth.uid())
      )
  )
)
with check (
  exists (
    select 1
    from public.consumidor_destinacao cd
    left join public.consumidor c on c.id_consumidor = cd.id_consumidor
    left join public.agente a on a.id_agente = cd.id_agente
    join public.destinacao d on d.id_destinacao = cd.id_destinacao
    join public.classificacao cl on cl.id_classificacao = d.id_classificacao
    join public.excedente ex on ex.id_excedente = cl.id_excedente
    join public.estabelecimento e on e.id_estabelecimento = ex.id_estabelecimento
    where cd.id_consumidor_destinacao = reserva.id_consumidor_destinacao
      and (
        c.auth_user_id = (select auth.uid())
        or a.auth_user_id = (select auth.uid())
        or e.auth_user_id = (select auth.uid())
      )
  )
);

create or replace function private.listar_excedentes_disponiveis()
returns table (
  id_destinacao bigint,
  id_excedente bigint,
  nome varchar,
  categoria varchar,
  descricao text,
  validade date,
  urgencia varchar,
  quantidade_disponivel numeric,
  unidade_medida varchar,
  condicao varchar,
  data_inicio date,
  data_fim date,
  horario_inicio time,
  horario_fim time,
  local varchar,
  preco_original numeric,
  preco_final numeric,
  percentual_desconto numeric,
  tipo_destinacao varchar,
  estabelecimento varchar,
  cidade varchar,
  bairro varchar
)
language plpgsql
security definer
set search_path = ''
as $$
begin
  if (select auth.uid()) is null then
    raise exception 'Autenticação necessária' using errcode = '42501';
  end if;

  return query
  select
    d.id_destinacao,
    ex.id_excedente,
    ex.nome,
    ex.categoria,
    ex.descricao,
    ex.validade,
    ex.urgencia,
    greatest(d.quantidade - coalesce(sum(
      case when r.status in ('ativa', 'confirmada') then cd.quantidade else 0 end
    ), 0), 0) as quantidade_disponivel,
    d.unidade_medida,
    d.condicao,
    d.data_inicio,
    d.data_fim,
    d.horario_inicio,
    d.horario_fim,
    d.local,
    d.preco_original,
    d.preco_final,
    d.percentual_desconto,
    td.nome as tipo_destinacao,
    e.nome as estabelecimento,
    e.cidade,
    e.bairro
  from public.destinacao d
  join public.tipo_destinacao td on td.id_tipo_destinacao = d.id_tipo_destinacao
  join public.classificacao cl on cl.id_classificacao = d.id_classificacao
  join public.excedente ex on ex.id_excedente = cl.id_excedente
  join public.estabelecimento e on e.id_estabelecimento = ex.id_estabelecimento
  left join public.consumidor_destinacao cd on cd.id_destinacao = d.id_destinacao
  left join public.reserva r on r.id_consumidor_destinacao = cd.id_consumidor_destinacao
  where d.status = 'disponivel'
    and (d.data_fim is null or d.data_fim >= current_date)
  group by d.id_destinacao, ex.id_excedente, td.nome, e.id_estabelecimento
  having greatest(d.quantidade - coalesce(sum(
    case when r.status in ('ativa', 'confirmada') then cd.quantidade else 0 end
  ), 0), 0) > 0
  order by ex.urgencia desc, d.data_inicio asc;
end;
$$;

create or replace function public.listar_excedentes_disponiveis()
returns table (
  id_destinacao bigint, id_excedente bigint, nome varchar, categoria varchar,
  descricao text, validade date, urgencia varchar, quantidade_disponivel numeric,
  unidade_medida varchar, condicao varchar, data_inicio date, data_fim date,
  horario_inicio time, horario_fim time, local varchar, preco_original numeric,
  preco_final numeric, percentual_desconto numeric, tipo_destinacao varchar,
  estabelecimento varchar, cidade varchar, bairro varchar
)
language sql
security invoker
set search_path = ''
as $$ select * from private.listar_excedentes_disponiveis(); $$;

create or replace function private.criar_reserva_atomica(
  p_destinacao_id bigint,
  p_quantidade numeric
)
returns public.reserva
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_consumidor_id bigint;
  v_destinacao public.destinacao%rowtype;
  v_reservado numeric;
  v_vinculo_id bigint;
  v_reserva public.reserva%rowtype;
begin
  if (select auth.uid()) is null then
    raise exception 'Autenticação necessária' using errcode = '42501';
  end if;
  if p_quantidade is null or p_quantidade <= 0 then
    raise exception 'Quantidade inválida' using errcode = '22023';
  end if;

  select c.id_consumidor into v_consumidor_id
  from public.consumidor c
  where c.auth_user_id = (select auth.uid()) and c.status = 'ativo';
  if v_consumidor_id is null then
    raise exception 'Perfil de consumidor ativo não encontrado' using errcode = '42501';
  end if;

  select * into v_destinacao
  from public.destinacao d
  where d.id_destinacao = p_destinacao_id
  for update;
  if not found or v_destinacao.status <> 'disponivel' then
    raise exception 'Destinação indisponível' using errcode = 'P0002';
  end if;

  select coalesce(sum(cd.quantidade), 0) into v_reservado
  from public.consumidor_destinacao cd
  join public.reserva r on r.id_consumidor_destinacao = cd.id_consumidor_destinacao
  where cd.id_destinacao = p_destinacao_id and r.status in ('ativa', 'confirmada');

  if p_quantidade > (v_destinacao.quantidade - v_reservado) then
    raise exception 'Quantidade solicitada não está disponível' using errcode = 'P0001';
  end if;

  insert into public.consumidor_destinacao (
    id_destinacao, id_consumidor, tipo_participacao, quantidade, data_aceite, confirmacao, status
  ) values (
    p_destinacao_id, v_consumidor_id, 'reserva', p_quantidade, now(), false, 'reservado'
  ) returning id_consumidor_destinacao into v_vinculo_id;

  insert into public.reserva (
    id_consumidor_destinacao, quantidade, valor_unitario, valor_total,
    data_reserva, horario_reserva, codigo_retirada, confirmacao_retirada, status
  ) values (
    v_vinculo_id, p_quantidade, coalesce(v_destinacao.preco_final, 0),
    p_quantidade * coalesce(v_destinacao.preco_final, 0), current_date, localtime,
    upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8)), false, 'ativa'
  ) returning * into v_reserva;

  if p_quantidade = (v_destinacao.quantidade - v_reservado) then
    update public.destinacao set status = 'esgotada' where id_destinacao = p_destinacao_id;
  end if;

  return v_reserva;
end;
$$;

create or replace function public.criar_reserva_atomica(
  p_destinacao_id bigint,
  p_quantidade numeric
)
returns public.reserva
language sql
security invoker
set search_path = ''
as $$ select private.criar_reserva_atomica(p_destinacao_id, p_quantidade); $$;

revoke all on function private.listar_excedentes_disponiveis() from public;
revoke all on function private.criar_reserva_atomica(bigint, numeric) from public;
revoke all on function public.listar_excedentes_disponiveis() from public, anon;
revoke all on function public.criar_reserva_atomica(bigint, numeric) from public, anon;
grant execute on function private.listar_excedentes_disponiveis() to authenticated;
grant execute on function private.criar_reserva_atomica(bigint, numeric) to authenticated;
grant execute on function public.listar_excedentes_disponiveis() to authenticated;
grant execute on function public.criar_reserva_atomica(bigint, numeric) to authenticated;

commit;
