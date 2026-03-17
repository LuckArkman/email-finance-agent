# Sprint 10: Processamento: Parsing e Separação de Anexos

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Ingestão e Conectividade
- **Objetivo da Sprint:** Extrair as faturas contidas dentro de mensagens (PDFs, JPEGs) descartando assinaturas inúteis.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Varredura de partes MIME da mensagem.
- [x] Download e identificação de file signature (Magic bytes).
- [x] Remoção de blobs irrelevantes (imagens de rodapé, linkedin icons).
- [x] Escrita dos arquivos brutos no S3 ou Temp storage.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- python-magic, base64

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `AttachmentParser`\n- `FileSanitizer`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `extract_attachments()`\n- `identify_mime_type()`\n- `filter_tracking_pixels()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
