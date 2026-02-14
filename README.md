# Módulo Odoo: Controle de Combustível

Este repositório contém um módulo customizado para **Odoo 19 (Community)** desenvolvido como parte de um desafio técnico. O objetivo é gerenciar o abastecimento de frotas internas e controlar o estoque físico de tanques de combustível.

![Odoo Version](https://img.shields.io/badge/Odoo-19.0%20(Master)-purple)
![Status](https://img.shields.io/badge/Status-Functional-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

##  Funcionalidades

### 1. Gestão de Tanques (Estoque)
- Cadastro de múltiplos tanques com capacidade máxima definida.
- **Cálculo Automático de Estoque:** O campo `current_stock` é atualizado em tempo real via *Compute Fields* (`@api.depends`) baseando-se nas entradas e saídas.

### 2. Controle de Abastecimentos
- Registro de **Entradas** (Reabastecimento do Tanque) e **Saídas** (Abastecimento de Veículos).
- Integração nativa com o módulo **Fleet (Frota)** para seleção de veículos.
- Validação de segurança (*Constraints*): Impede a saída de combustível se o saldo do tanque for insuficiente.

### 3. Diferencial: Integração com Compras
- Extensão do módulo nativo **Purchase (Compras)**.
- Adicionado campo "Tanque de Destino" no formulário de Pedido de Compra.
- **Automação:** Ao confirmar um pedido de compra, o sistema gera automaticamente um registro de entrada no `fuel.log`, atualizando o estoque sem retrabalho.

### 4. Segurança e Permissões
- **Motorista:** Acesso restrito para registrar abastecimentos.
- **Analista:** Acesso de leitura aos relatórios.
- **Administrador:** Acesso total e configurações.

---

## Tecnologias e Adaptações (Odoo 19)

O módulo foi desenvolvido sobre a versão *Nightly/Master* do Odoo 19. Foram aplicadas correções para *breaking changes* desta versão:

* **Views:** Utilização da nova tag `<list>` (substituindo a depreciada `<tree>`).
* **Security:** Ajuste na estrutura de `res.groups` (remoção de campos legados) para garantir a instalação limpa.

---

## Como Executar

### Pré-requisitos
- Docker e Docker Compose instalados.

### Passo a Passo

1. **Clone o repositório:**
 git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
   cd seu-repositorio
   
3. Suba o ambiente Docker: docker compose up -d

4. Acesse o Odoo:

- URL: http://localhost:8069
- Login: admin
- Senha: admin (ou a definida no seu docker-compose)

4. Ative o "Modo Desenvolvedor" (Configurações).
- Vá em Apps > Atualizar Lista de Aplicativos.
- Procure por controle_combustivel.
- Clique em Ativar.(Nota: O módulo instalará automaticamente as dependências fleet e purchase).
  
## Roteiro de Teste:

1. Teste de Integração (Compras):
- Vá em Compras > Novo.
- Selecione um Fornecedor e escolha o "Tanque Principal" no campo de destino.
- Adicione um produto (ex: Diesel, 1000L) e confirme.
- Verifique em Gestão de Combustível se o estoque aumentou.

2. Teste de Saída (Abastecimento):

 -Vá em Gestão de Combustível > Abastecimentos.
 -Lance uma saída de 50L para um veículo.
 -Verifique se o estoque do tanque foi reduzido.
