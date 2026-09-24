# DYNAMIS

Plataforma digital de gestão de excedentes alimentares. O MVP registra o fluxo:

`estabelecimento → excedente → classificação → destinação → reserva/retirada`

## Estrutura

- `index.html`, `sobre.html`: site público;
- `login.html`, `cadastro.html`: autenticação;
- `app.html`: área logada para estabelecimentos e consumidores;
- `backend/app`: API FastAPI organizada em rotas, services, schemas e acesso ao Supabase;
- `backend/sql/mvp_security.sql`: catálogo inicial, políticas de reserva e RPCs transacionais;
- `banco.sql` e o DER fornecidos: fonte de verdade do modelo de dados.

## Configuração

1. Crie o ambiente Python:

   ```bash
   cd backend
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

2. Copie `backend/.env.example` para `backend/.env` e preencha:

   ```env
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_PUBLISHABLE_KEY=...
   SUPABASE_SECRET_KEY=...
   ```

   A chave secreta é opcional quando a confirmação de e-mail está desativada. Ela existe apenas no servidor e nunca é enviada ao navegador.

3. Revise e execute `backend/sql/mvp_security.sql` no SQL Editor do Supabase, primeiro em homologação.

4. Inicie a aplicação:

   ```bash
   cd backend
   .venv/bin/python run.py
   ```

5. Abra `http://127.0.0.1:8000`.

Documentação da API: `http://127.0.0.1:8000/docs`.

## Segurança

- O front-end envia o JWT do usuário ao back-end.
- O back-end valida o JWT no Supabase Auth e repassa o token às consultas, preservando o RLS.
- A reserva é feita por RPC transacional com bloqueio da destinação para evitar excesso de reservas concorrentes.
- `.env`, chaves e ambientes virtuais estão ignorados pelo Git.
- A `service_role`/secret key nunca deve ser colocada em JavaScript ou em variáveis públicas.

## Perfis do MVP

- **Estabelecimento:** cadastra excedente, classifica e publica uma destinação.
- **Consumidor:** consulta oportunidades e realiza reservas.
- **Agente:** perfil preparado no schema; a interface operacional específica fica para a próxima etapa do MVP.

## Observação sobre o arquivo de ambiente fornecido

O arquivo recebido contém credenciais de conexão PostgreSQL. A aplicação web também precisa da URL do projeto e de uma chave publicável do Supabase para autenticação e acesso via Data API. Não copie credenciais para arquivos versionados.
