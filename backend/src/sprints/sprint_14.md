# Sprint 14: Armazenamento em Nuvem Raw/Processed (AWS S3)

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Pré-processamento Documental
- **Objetivo da Sprint:** Upload dos arquivos processados para o bucket, preparando-os para o OCR sem lotar disco local.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- Setup do conector boto3.
- Geração de Pre-Signed URLs.
- Upload do RAW file e Upload do Processed file.
- Atualização do path no PostgreSQL Database.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- boto3

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `S3BucketManager`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `upload_file_to_s3()`\n- `generate_presigned_url()`\n- `delete_blob_s3()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
