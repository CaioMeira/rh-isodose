### Primeiro passo se resumiu a aprender o Docker.
- instalação da wsl
- instalação do Ubuntu (wsl)
- mudança na bios para permitir a virtualização
- instalação do Docker
- como usar alguns dos comandos.:
    - docker ps
    - docker --list --verbose
    - docker up
    - docker down
    - docker stop
    - docker build
    - entre outros.

### Segundo passo foi se preparar com o git
- instalar o git[]
- clonar repositório


### Terceiro passo foi em relação ao Docker-compose
- inicialização em conjunto
- acessar o repositório utilizando cd no powershell e em seguida utilizar o comando docker-compose para executá-los na ordem pré-definida por requisitos.
    - docker-compose build
    - docker-compose up
    - docker-compose stop
    - entre outros.
    
    -d para modo daemon (detach), para liberar o terminal.
    -p para definir uma porta (ex: -p 3030:3030), onde uma é a porta da sua máquina, e a outra de onde o container está sendo executado.
    -P para uma porta automática.

![Containers em pleno funcionamento](image-1.png)

### Quarto passo: um pouco sobre APIs com a lib requests.
-> para APIs REST;

- GET : obter dados;
- POST : enviar dados;
- PUT : atualizar dados (objeto completo);
- PATCH : atualizar dados (objeto parcial);
- DELETE : deletar um dado;
- OPTIONS : permitir acesso de domínios diferentes.


    response = requests.get(url, data, json)


- ** Status Code:
    - 200 : Sucesso
    - 201 : Cadastro feito com Sucesso
    - 204 : Sucesso mas sem conteúdo de retorno
    - 401 : Não autorizado
    - 404 : Não encontrado
    - 500 : Erro no servidor

    - Uso do Imsomnia para ver e testar os endpoints.

### Acessar a API e Receber um Retorno.

Consegui acessar as APIs, primeiramente com a função request.get() para receber uma primeira confirmação, e depois o próximo passo foi determinar como o dado seria passado para conseguir as respostas que queríamos.

inicialmente, a inteção foi passar um caminho por meio de um json.

 payload = {

     "path": "/var/data/dcm/prostate/CT.20190343_221.dcm"

 }

Baseando-me no exemplo disposto em http://localhost:9999/index

A seguinte linha:

    payloadJson = json.dumps(payload)

Foi utilizada para garantir a formatação correta. 

    response = requests.post(url, data={"data": payloadJson})

E assim foi efetuado primeiramente o envio dos "dados" referente ao caminho do arquivo: CT.20190343_221.dcm

### Tipos dos Arquivos Dicom

Estudando um pouco sobre os arquivos Dicom dispostos, podemos separá-los em 5 categorias.

CT -> Arquivos de Tomografia (cada arquivo representa uma fatia para gerar um modelo 3d futuramente)

RD -> RT Dose : Arquivo com dados de dose de radiação planejada

RI -> RT Image: Imagens de verificação ???

RP -> RT Plan: Plano de tratamento completo

RS -> RT Structure Set: Estruturas delineadas.

### Isodose

A parte de Isodose da nossa API esperava um arquivo Json com diversos caminhos.

A função em si usa um json.load(data), e armazena em d.

    for key, value in d['files'].items():

Utiliza um for que pega todos os n items de d com a tag 'files' dentro do arquivo json

esses n itens são caminhos para os arquivos que a função a seguinte função vai utilizar como argumento para lê-los:

    dicom = dicomparser.DicomParser(value)

e para isso tivemos que reformar o payload que definimos para enviar uma série de arquivos anexados em 'files' dentro do json.

    payload = {
        "files": {
            "CT_1": "/var/data/dcm/prostate/CT.20190343_1.dcm",
            "CT_2": "/var/data/dcm/prostate/CT.20190343_2.dcm",

            ...

            "CT_219": "/var/data/dcm/prostate/CT.20190343_219.dcm",
            "CT_220": "/var/data/dcm/prostate/CT.20190343_220.dcm",
            "CT_221": "/var/data/dcm/prostate/CT.20190343_221.dcm",
            "CT_514": "/var/data/dcm/prostate/CT.20190343_514.dcm",
            "RD": "/var/data/dcm/prostate/RD.20190343_.dcm",
            "RI1": "/var/data/dcm/prostate/RI.20190343_7_227.dcm",
            "RI2": "/var/data/dcm/prostate/RI.20190343_7_228.dcm",
  
            ...

            "RI6": "/var/data/dcm/prostate/RI.20190343_7_232.dcm",
            "RI7": "/var/data/dcm/prostate/RI.20190343_7_233.dcm",
            "RP": "/var/data/dcm/prostate/RP.20190343_FASE UNICA.dcm",
            "RS": "/var/data/dcm/prostate/RS.20190343_.dcm"
        }
    }

    Após verificações foi observado que  uma seção separada para os arquivos d['isodoses'] seria necessária também. sendo essa exibida fora do grupo de 'Files'.

    Tive problemas no retorno do Json para a minha aplicação, efetuei a leitura dos arquivos separadamente utilizando a função:

        ds = pydicom.dcmread(caminho_arquivo, force=True)

    onde foi conseguido efetuar a leitura dos arquivos, porém não tinha os argumentos relacionados a função:

        dicom = dicomparser.DicomParser(ds)

    Para efetuar os tratamentos dos dados e gerar os devidos resultados.

    Um código cheio de prints para "debug" dos containers sem trazer pro local foram utilizados para ver o passo a passo dos processos, parando praticamente sempre na função dicomparser.DicomParser()

### Contour

Primeiramente comecei atuando apenas na função Contour para tentar dismistificar e aprender sobre o método de programação (longe de ser uma programação de MicroComputadores como eu estava mais habituado)

A função Contour espera um tipo de payload diferente, com os caminhos diretamente dispostos no json.

A função em questão lê path por path com a função dicomparser.DicomParser() e separa os arquivos CT, RS e RD.

Em sequencia utiliza as seguintes linhas para fazer os cálculos necessários:

    calc = Estrutura(rtstructs[0], None, None)
    ret = calc.structures()

E retorna o ret em formato json para a aplicação que fez a requisição.

### Observações e Conclusões.

Praticamente tudo que eu vi neste projeto eram novidades, todo meu conhecimento de Python se baseava em cálculos em máquinas locais, computação científica e afins, e programação também mais relacionada a MicroControladores, FPGAs entre outros.

Nunca havia trabalhado com arquivos json e Dicom.

Primeiro contado com JavaScript e TypeScript.

Docker, React, Vite, Cherrypy, tudo sendo visto pela primeira vez.

Acredito que o avanço foi grande, mas não o suficiente. Porém fiquei bem interessado em saber como as coisas deveriam funcionar, e gostaria de ter uma oportunidade em progredir mais.

Foram horas e horas de video-aulas esse final de semana, que foram desde instalação das dependências, como habilitação da capacidade de virtualização na BIOS, como instalação do próprio wsl pra operar com Ubuntu dentro da minha máquina, Docker, Docker-compose, APIs, React entre outros.

A parte do front-end não consegui explorar muito visto que fiquei preso numa parte mais do back-end que era necessária para continuar, mas vi um mini-curso de react online para entender pelo menos como as coisas funcionavam dentro do typeScript da API React-api do nosso projeto.

Tive que mudar os dockerfiles e docker-compose para fazer uma indexação diferente dos arquivos data, sendo que foi algo que eu evitei ao máximo no inicio pois acreditava que minhas mudanças teriam que ficar restritas a minha aplicação externa e também um pouco na API para retornar o formato de Json que eu queria para jogar pro React.

Visto que uma API geralmente depende de uma portabilidade para ser acessada por diversas aplicações exteranas e não só a minha.

Mas depois mudei e tentei mexer no que fosse possível para pelo menos obter resultados um pouco melhores.

Foi um final de semana / feriado e tanto em função do desafio, mas como o prazo chegou ao fim, farei o commit do jeito que está, com vários prints, e parcelas comentadas, e seções provisórias.

Agradeço pela oportunidade. E se possível gostaria de participar do projeto de vocês nem que de forma de trainee inicialmente, pois acredito que estava a um momento eureka de resolver o meu problema e fiquei bem interessado.

