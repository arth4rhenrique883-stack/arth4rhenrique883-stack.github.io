# Plano: conta obrigatória e acesso por ciclo (ckp)

Estado em 24/11/2026: **nada disto está ligado no app publicado.** Login e pagamento nunca foram testados em aparelho; travar o app agora deixaria o Arthur sem acesso. Preços previstos (não aparecem no app): ciclo básico R$ 34,99, ciclo clínico R$ 49,99, pacote completo R$ 59,99 (promocional de lançamento).

## O que já existe
- Login opcional pelo ícone de conta (script `data-nuvem` em cada página): e-mail e senha, "Criar conta" e Google, no projeto Supabase `xequemate-med` (ref `phzcjcduvfrizcgfosxu`).
- Sincronização: tabela `estado` (`user_id`, `dados` jsonb, `atualizado`). Sobe e baixa todas as chaves do localStorage que começam com `medaj` ou `medas-tema`, resolvendo conflito por data de cada chave (vale a mais nova).
- Offline: `sw.js` guarda o app inteiro. Contato: constante `CK_EMAIL` em `ferramentas/design-ckp.py` (vazia = o botão avisa "em breve").

## Fase 0: preparar sem travar (pode ser feita já)
1. Chave `CK_CONTA_OBRIGATORIA=false` no código; só vira `true` depois do teste real.
2. Testar em aparelho real: criar conta, entrar com Google, sair, entrar em outro aparelho, ver o progresso chegar.
3. Política de privacidade (`privacidade.html`) atualizada para dados de conta, e-mail de contato.

## Fase 1: conta obrigatória (sem pagamento)
- Ao abrir o app sem sessão, mostrar tela de entrada/criação de conta antes da escolha de ciclo.
- **Progresso já salvo:** ao criar a conta ou entrar pela primeira vez, o sincronismo atual já envia o localStorage do aparelho para a conta (merge por chave). Só falta aviso na tela ("seu progresso deste aparelho será salvo na conta") e um backup local antes do primeiro envio.
- **Offline:** guardar a sessão e permitir uso offline por um prazo (sugestão: 14 dias sem validar); renovar o token quando houver internet. Sem sessão guardada e sem internet, só a tela de entrada.
- **Aviso honesto:** bloquear a interface no navegador não protege o conteúdo. Os arquivos do GitHub Pages são públicos. Para proteger de verdade, o conteúdo pago precisa sair do Pages e ser entregue por backend autenticado (ex.: Supabase Storage/Edge Function que checa a assinatura). O app de loja (APK/AAB) empacota o conteúdo e pode ser protegido pela própria loja. Decidir isso antes de vender.

## Fase 2: acesso por ciclo (depende de pagamento)
- Tabela `assinatura` no Supabase: `user_id`, `plano` (`basico` | `clinico` | `completo`), `valido_ate`, `origem` (`play`, `web`, `apple`), `token_compra`, com RLS "cada usuário lê só a sua".
- Regra: `basico` libera 1º ao 5º; `clinico` libera 6º ao 8º; `completo` libera os dois. A tela de escolha de ciclo já existe e pode mostrar cadeado nos ciclos não liberados.
- **Play Billing:** compra no app Android → Edge Function valida o token na Google Play Developer API → grava em `assinatura`. Notificações em tempo real (RTDN) para renovação, cancelamento e reembolso. Só funciona no app instalado da Play Store, não na versão web.
- **Web/PWA e iOS:** precisam de outro caminho (gateway com Pix/cartão, ou compra via App Store). Decidir se haverá venda fora da loja.
- Preço promocional do pacote completo: campo `preco_promocional_ate` na configuração, nunca no código do app.

## Ordem sugerida
1. Fase 0 (testes reais, privacidade, e-mail de contato criado e colocado em `CK_EMAIL`).
2. Fase 1 com a chave desligada para teste interno, depois ligada.
3. Escolher onde o conteúdo pago mora (Pages x backend).
4. Fase 2 junto com a publicação na Play Store.
5. Recomendado: advogado antes da venda (já anotado no plano de independência).
