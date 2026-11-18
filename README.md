# Migrador Firebird 2.1 para 3.0

Aplicação gráfica em Python para migrar uma base de dados Firebird 2.1 para Firebird 3.0. O programa cria um backup temporário com o `gbak` do Firebird 2.1 e restaura esse backup num **novo ficheiro** com o `gbak` do Firebird 3.0. O ficheiro de origem não é alterado.

> **Importante:** a aplicação não substitui a base original. Depois da migração, teste a nova base e confirme os dados antes de a utilizar em produção.

## Pré-requisitos

- Windows 10 ou 11.

- Python 3 instalado, incluindo o `tkinter` (normalmente incluído no instalador oficial do Python para Windows).

- Git, caso pretenda obter o projeto através do GitHub.

- Acesso aos executáveis `gbak.exe` das instalações do Firebird 2.1 e 3.0.

- Uma conta de utilizador e as respetivas senhas válidas para cada versão do Firebird.

O programa usa apenas bibliotecas da biblioteca padrão do Python; não é necessário instalar dependências com `pip`.

## Obter o projeto

Abra o PowerShell numa pasta onde tenha permissões de escrita — por exemplo, Documentos — e execute:

```
cd $HOME\Documents
git clone https://github.com/FabioHenrique023/firebird_migration.git
cd firebird_migration
```

Evite clonar o repositório em `C:\Program Files`, pois essa pasta é protegida pelo Windows.

## Executar

No PowerShell, dentro da pasta do projeto, execute o ficheiro Python principal. Se o ficheiro se chamar `migrador.py`:

```
python .\migrador.py
```

Se o comando `python` não for reconhecido, experimente:

```
py .\migrador.py
```

Se o ficheiro principal tiver outro nome, substitua `migrador.py` pelo nome correto. Também pode abrir o ficheiro `.py` com o Python, se essa associação estiver configurada no Windows.

## Utilização da aplicação

1. Em **Banco de origem**, selecione o ficheiro existente `.fdb` ou `.gdb`.

1. Em **gbak do Firebird 2.1**, selecione o `gbak.exe` da instalação Firebird 2.1.

1. Em **gbak do Firebird 3.0**, selecione o `gbak.exe` da instalação Firebird 3.0.

1. Em **Novo banco de destino**, escolha o caminho e o nome para a base migrada. Por padrão, o programa sugere um nome com o sufixo `_FB3`.

1. Informe o utilizador e a senha do Firebird 2.1 e, separadamente, os do Firebird 3.0. As senhas podem ser diferentes.

1. Clique em **Iniciar migração** e acompanhe as mensagens na área de registo.

1. Quando surgir a confirmação de conclusão, teste a nova base com a aplicação que a utiliza antes de a colocar em produção.

O ficheiro de destino não pode ser igual ao ficheiro de origem e, para evitar substituições acidentais, o programa não inicia se o destino já existir. Escolha outro nome ou mova/remova previamente o ficheiro existente, depois de confirmar que já não é necessário.

## O que o programa faz

- Executa o backup da origem com o `gbak` 2.1.

- Guarda o backup temporariamente e remove-o no fim do processo.

- Restaura o backup com o `gbak` 3.0 para criar a nova base.

- Mostra as mensagens dos comandos e informa se a migração terminou ou falhou.

- Não altera nem apaga automaticamente a base original.

## Recomendações e resolução de problemas

- Faça uma cópia de segurança independente antes de migrar uma base importante.

- Feche as aplicações que possam estar a utilizar a base e confirme que tem permissões de leitura na origem e de escrita na pasta de destino.

- Se a migração falhar, consulte as mensagens na área **Andamento / mensagens**. Uma falha durante o restauro pode deixar um ficheiro de destino parcial; não o utilize como base válida. Verifique o ficheiro antes de o remover e escolha um destino novo para tentar novamente.

- Confirme que selecionou os executáveis `gbak.exe` correspondentes às versões indicadas e que as credenciais são válidas em cada versão.

- Para diagnósticos adicionais, execute o programa a partir do PowerShell, assim poderá consultar também eventuais mensagens de erro apresentadas no terminal.

## Segurança

As senhas são pedidas pela interface e passadas aos processos `gbak` por uma variável de ambiente, em vez de serem incluídas diretamente na linha de comando. Não partilhe capturas de ecrã que mostrem senhas, caminhos ou dados confidenciais.