/* Configuração PÚBLICA do Firebase da caixa de sugestões da Banca (Terra Brasilis).
   Estes valores não são senha: o Google os mostra para qualquer site. Quem protege os dados
   são as regras do Firestore (ver regras no painel do Firebase).
   Enquanto for null, a aba "Sugestões" mostra "abre em breve". */
window.BANCA_FIREBASE = null;
/* Depois de criar o projeto no Firebase, troque a linha acima por algo assim:
window.BANCA_FIREBASE = {
  apiKey: "...",
  authDomain: "....firebaseapp.com",
  projectId: "...",
  appId: "..."
};
*/
