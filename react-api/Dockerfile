# Usa a imagem do Node 22 no Alpine Linux
FROM node:22-alpine

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia apenas os arquivos de dependências primeiro para aproveitar cache de build
COPY package*.json ./

# Instala as dependências
RUN npm install --legacy-peer-deps

# Copia todo o código-fonte
COPY . .

# Expõe a porta padrão do React (3000)
EXPOSE 3000 5173

# Inicia a aplicação
CMD ["yarn", "dev", "--host"]