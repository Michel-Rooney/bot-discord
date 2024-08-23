# Bots para o Discord

Este é um projeto que armazenarei bots para o discord de uso atual ou futuro.

### 📋 Documentação
[Discord - DOCS](https://discord.com/developers/docs/intro)

### 📌 On Air
Discord - Deploy - *Em análise*

## 🚀 Começando

Essas instruções permitirão que você obtenha uma cópia do projeto em operação na sua máquina local para fins de desenvolvimento e teste.

### 📋 Pré-requisitos

Você precisa do [Python](https://www.python.org/downloads/) instaldo na sua máquina

```
# Verificar se está instaldo
# Linux
python3 --version

# Windows
python --version
```

**Note:** Os comandos abaixo serão na maioria relacionados ao linux

### 🔧 Instalação

1. Clone o repositório do projeto:

```git
git clone https://github.com/Michel-Rooney/bot-discord.git
```

2. Entre na pasta:

```
cd bot-discord
```

3. Crie um ambiente virtual:

```
python3 -m venv venv
```

4. Ative o ambiente virtual:

```
# Linux
source venv/bin/activate

# Windows
venv/Scripts/activate

# Quando ativo, irar aparecer (venv) no inicio
(venv) user@maquina ~/bot-discord$
```

**Note:** Para desativar rode o comando
```
deactivate
```

5. Com o ambiente ativo, instale as dependencias:

```
pip install -r requirements.txt
```

6. Copie o arquivo .env-example para .env:

```
cp .env-example .env

# No arquivo .env substitua os CHANGE-ME
```

7. Inicie o projeto:

```
python (nome-do-arquivo).py
```

## 🛠️ Construído com

* [Python](https://www.python.org/) - Linguagem
* [Discord](https://discord.com/developers/docs/intro) - Api do Discord
* [Strava](https://developers.strava.com/) - Api do Strava

## ✒️ Autores

* [Michel Rooney](https://github.com/Michel-Rooney/) - *Dev*

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE.md](https://github.com/Michel-Rooney/bot-discord/blob/main/LICENSE) para detalhes.
