# Desafio de Programação - Renderização de DICOM com Cornerstone.js e Python API

Bem-vindo(a) ao repositório do **Desafio de Programação**!  
Aqui você encontrará um projeto que combina uma aplicação **React** (utilizando [Cornerstone.js](https://www.cornerstonejs.org/)) com uma **API Python** (que faz uso de uma versão modificada da biblioteca `dicompyler-core`) para renderizar imagens DICOM, exibir isodoses e contornos (curvas), em múltiplas visões (axial, coronal e sagital).

---

## Índice

1. [Objetivo](#objetivo)  
2. [Visão Geral do Projeto](#visão-geral-do-projeto)  
3. [Estrutura de Pastas](#estrutura-de-pastas)  
4. [Pré-requisitos](#pré-requisitos)  
5. [Configuração e Execução](#configuração-e-execução)  
   - [1. Clonar o Repositório](#1-clonar-o-repositório)  
   - [2. Configurar e Executar via Docker Compose](#2-configurar-e-executar-via-docker-compose)  
   - [3. Acessar a Aplicação](#3-acessar-a-aplicação)  
6. [Detalhes dos Serviços](#detalhes-dos-serviços)  
   - [Serviço **python-api**](#serviço-python-api)  
   - [Serviço **react-api**](#serviço-react-api)  
7. [Endpoints Python](#endpoints-python)  
8. [Renderização DICOM no React com Cornerstone.js](#renderização-dicom-no-react-com-cornerstonejs)  
9. [Possíveis Customizações e Extensões](#possíveis-customizações-e-extensões)  
10. [Referências e Links Úteis](#referências-e-links-úteis)  
11. [Avaliação](#avaliação)  

---

## Objetivo

O objetivo deste desafio é criar uma aplicação capaz de:

1. **Renderizar imagens DICOM** em diferentes planos (Axial, Coronal e Sagital) com a biblioteca [Cornerstone.js](https://www.cornerstonejs.org/).
2. **Plotar** curvas de isodose e contornos (curvas) retornadas pela **API Python**, que utiliza uma versão adaptada da biblioteca `dicompyler-core`.
3. **Realizar chamadas REST** para a API Python, nos endpoints:
   - `http://localhost:9999/contour`
   - `http://localhost:9999/isodose`
4. **Executar** a aplicação via **Docker** com dois contêineres distintos:
   - Um para a **API Python** (`python-api`)
   - Outro para a **aplicação React** (`react-api`)

---

## Visão Geral do Projeto

Este projeto é composto de:
- **API Python (`python-api`)**: responsável por carregar dados DICOM (ou em formato NIfTI `nii.gz`), gerar informações de contornos (contour) e isodoses (isodose) por meio de chamadas REST.
- **Aplicação React (`react-api`)**: responsável pela interface de usuário e pela renderização das imagens DICOM, contornos e isodoses, utilizando a biblioteca [Cornerstone.js](https://www.cornerstonejs.org/).

Ambos os serviços são orquestrados usando **Docker Compose** para simplificar o processo de configuração, build e execução.

---

## Estrutura de Pastas

A estrutura de pastas principal do projeto é a seguinte:

```
.
├── docker-compose.yml          # Arquivo de configuração do Docker Compose
├── python-api
│   ├── app.py                  # Arquivo principal da API Python (CherryPy ou similar)
│   ├── cache/                  # Pasta que pode ser utilizada para cache
│   ├── data/                   # Pasta onde ficam armazenados os dados (DICOM, NIfTI etc.)
│   ├── Dockerfile              # Dockerfile para construir a imagem da API Python
│   ├── lib/                    # Bibliotecas específicas usadas pela API, se necessário
│   ├── Model/                  # Modelos de dados, classes, etc.
│   └── requirements.txt        # Dependências Python
├── react-api
│   ├── assets/                 # Arquivos estáticos (imagens, fontes, etc.)
│   ├── bun.lockb
│   ├── Dockerfile              # Dockerfile para construir a imagem da aplicação React
│   ├── index.html              # HTML principal (ponto de entrada do React)
│   ├── node_modules/           # Dependências do Node.js (geradas após instalação)
│   ├── package.json            # Configurações e dependências do projeto React
│   ├── package-lock.json
│   ├── public/                 # Pasta com recursos públicos
│   ├── README.md               # Instruções específicas do front-end (opcional)
│   ├── src/                    # Código-fonte da aplicação React
│   ├── tsconfig.json           # Configurações do TypeScript (caso use TypeScript)
│   ├── tsconfig.node.json
│   ├── vite.config.ts          # Configuração do Vite para o build/dev
│   └── yarn.lock
└── README.md                   # Este arquivo (documentação principal do projeto)
```

---

## Pré-requisitos

1. [Docker](https://docs.docker.com/get-docker/) instalado em sua máquina.  
2. [Docker Compose](https://docs.docker.com/compose/install/) — em algumas versões do Docker Desktop, o Compose já vem incluído.  

---

## Configuração e Execução

### 1. Clonar o Repositório

Use o comando abaixo para clonar o repositório em sua máquina local:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```

> Ajuste a URL para o repositório real, caso esteja usando GitHub ou outro serviço de controle de versão.

### 2. Configurar e Executar via Docker Compose

No diretório raiz do projeto (onde está o arquivo `docker-compose.yml`), execute:

```bash
# Cria as imagens dos contêineres python-api e react-api
docker-compose build

# Sobe o contêiner da API Python em segundo plano (-d)
docker-compose up -d python-api

# Sobe o contêiner da aplicação React em modo interativo (logs visíveis)
docker-compose up react-api
```

> Caso deseje subir ambos os contêineres em modo daemon, use `docker-compose up -d`.  
> Se quiser ver os logs de ambos, basta executar `docker-compose logs -f`.

### 3. Acessar a Aplicação

Após o passo acima, o terminal exibirá algo como:

```
react-api_1   |   ➜  Local:   http://localhost:5173/
react-api_1   |   ➜  Network: http://172.28.0.3:5173/
```

- Para **acessar a aplicação**, abra o navegador em:  
  `http://xxxx:5173/`  onde xxx é Network fornecido no log

- A porta padrão do Vite (usada pelo React) é **5173**.  
- A **API Python** estará disponível em `http://localhost:9999/`.

---

## Detalhes dos Serviços

### Serviço **python-api**

- **Dockerfile**: localizado em `./python-api/Dockerfile`.  
- **Funções**:  
  - Subir um servidor (ex.: [CherryPy](https://cherrypy.dev/)) ou outro framework web Python.
  - Disponibilizar endpoints REST para contornos e isodoses.
  - Carregar e processar arquivos DICOM/NIfTI da pasta `python-api/data/` ou `python-api/cache/`.
  - Retornar dados em formato JSON ou binário para a aplicação React.

**Exemplo de `docker-compose.yml`** (trecho):

```yaml
python-api:
  build: ./python-api
  volumes:
    - ./python-api:/var/
  ports:
    - "9999:9999"
  command: "python3 app.py"
  restart: always
```

### Serviço **react-api**

- **Dockerfile**: localizado em `./react-api/Dockerfile`.  
- **Funções**:  
  - Subir a aplicação React com o [Vite](https://vitejs.dev/) ou outro bundler.
  - Renderizar as imagens DICOM (Axial, Coronal e Sagital) usando [Cornerstone.js](https://www.cornerstonejs.org/).
  - Fazer requisições para a API Python e exibir curvas de isodose/contorno.

**Exemplo de `docker-compose.yml`** (trecho):

```yaml
react-api:
  build: ./react-api
  ports:
    - "3000:3000"
    - "5173:5173"
  volumes:
    - ./react-api:/app
    - ./python-api:/var/
    - /app/node_modules
  environment:
    CHOKIDAR_USEPOLLING: "true"
  command: ["yarn", "dev", "--host"]
  stdin_open: true
  restart: always
```

> **Observação**:  
> - O **volumes** `- ./python-api:/var/` faz com que a pasta da API Python seja visível também no contêiner do React, caso seja necessário acessar arquivos DICOM diretamente.  
> - A variável `CHOKIDAR_USEPOLLING: "true"` serve para habilitar o *hot reload* em sistemas Windows/Mac.

---

## Endpoints Python

A API Python oferece (pelo menos) dois endpoints REST:

1. `GET http://localhost:9999/contour`  
   - Retorna dados de contorno (curvas) gerados pelo `dicompyler-core` (ou outro script) em formato JSON ou binário.  
   - **Exemplo de uso**: 
     ```js
     fetch('http://localhost:9999/contour')
       .then(response => response.json())
       .then(data => {
         console.log('Contornos recebidos:', data);
       });
     ```

2. `GET http://localhost:9999/isodose`  
   - Retorna dados de isodose, também gerados por processamento Python.
   - **Exemplo de uso**:
     ```js
     fetch('http://localhost:9999/isodose')
       .then(response => response.json())
       .then(data => {
         console.log('Isodose recebida:', data);
       });
     ```

> **Importante**: De acordo com o escopo do desafio, será necessário ajustar o **`app.py`** (ou outro arquivo Python principal) para que retorne o formato de dados necessário ao Cornerstone.js.  
> Caso precise de desempenho ou de trabalhar diretamente com dados binários, revise o retorno para que atenda às suas necessidades de plotagem.

---

## Renderização DICOM no React com Cornerstone.js

No **React**, você encontrará (ou poderá criar) um componente de exemplo que carrega e renderiza séries DICOM usando [Cornerstone.js](https://www.cornerstonejs.org/).  

- **Configuração inicial**:  
  - Instale as dependências necessárias (`cornerstone-core`, `cornerstone-tools`, `cornerstone-wado-image-loader`, etc.).
  - Inicialize o Cornerstone em algum `useEffect` ou ciclo de vida do React.
  - Aponte o Cornerstone para a pasta de imagens DICOM que está montada em `/var/` no contêiner.

- **Multiplanar (Axial, Coronal e Sagital)**:
  - É possível utilizar bibliotecas específicas de reformat 3D, ou carregar três séries diferentes nos respectivos viewports.

- **Isodoses e Contornos**:  
  - Utilize os dados retornados pelos endpoints Python e desenhe sobre as imagens, seja via Canvas overlay, seja via ferramentas do Cornerstone Tools.

> A [documentação oficial do Cornerstone.js](https://www.cornerstonejs.org/docs/examples/) e [exemplos ao vivo (live-examples)](https://www.cornerstonejs.org/live-examples/) são ótimos pontos de partida.

---

## Possíveis Customizações e Extensões

1. **Processamento Python**:  
   - Pode-se personalizar o script que processa as imagens DICOM (`app.py`) para gerar contornos mais complexos ou cálculos de dose.  
   - Pode-se trabalhar com [SimpleITK](https://simpleitk.org/) para converter DICOM em NIfTI (`nii.gz`).

2. **Upload de arquivos**:  
   - Criar um endpoint que permita o upload de arquivos DICOM para a pasta `python-api/data/`, para então processá-los dinamicamente.

3. **Visualizações adicionais**:  
   - Incluir janelas de intensidade, medições, rotação ou outras ferramentas de manipulação de imagem oferecidas pelo Cornerstone Tools.

4. **Segurança**:  
   - Proteger os endpoints com autenticação/HTTPS caso seja necessário.

---

## Referências e Links Úteis

- [Cornerstone.js](https://www.cornerstonejs.org/)  
- [Exemplos do Cornerstone.js - petct](https://www.cornerstonejs.org/live-examples/petct)  
- [Exemplos do Cornerstone.js - labelmaprendering](https://www.cornerstonejs.org/live-examples/labelmaprendering)  
- [dicompyler-core (GitHub)](https://github.com/dicompyler/dicompyler-core)  
- [CherryPy](https://cherrypy.dev/)  
- [Vite - Guia Oficial](https://vite.dev/guide/)  
- [SimpleITK](https://simpleitk.org/)  

---

## Avaliação

Você será avaliado(a) pela implementação correta dos requisitos:

1. **Uso de Docker** para executar dois contêineres (API Python + React).  
2. **Renderização DICOM** usando [Cornerstone.js](https://www.cornerstonejs.org/).  
3. **Plotagem de Isodose e Curvas** (contornos) retornadas pela API Python.  
4. **Chamadas REST** para os endpoints `http://localhost:9999/contour` e `http://localhost:9999/isodose`.  
5. **Organização e Estrutura** do código fonte.  

Qualquer dúvida, verifique este `README` ou consulte a documentação adicional nos links acima.  
Bons estudos e boa codificação!
