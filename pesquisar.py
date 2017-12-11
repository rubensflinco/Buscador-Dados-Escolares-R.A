#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, json, requests, argparse, datetime
import http.cookiejar

##Verificar se o comando não é null
if len(sys.argv) < 4:
    print("python pesquisar.py <R.A> <Digito> <UF> <Data Nascimento> ")
    sys.exit(1)
##Codigo para formatar texto para UTF-8, se livrar do erro UnicodeDecodeError


##Capturar informacoes <R.A> <Digito> <UF> <Data Nascimento>
ra = sys.argv[1]
digito = sys.argv[2]
data_nascimento = sys.argv[4]
password = 'PWGroupHue'
UF = sys.argv[3]
user = ra+digito+UF.lower()
if os.path.exists(user+'.html'):
   os.unlink(user+'.html')
##Formatar data para o tipo Y-M-D
formatar_data = datetime.datetime.strptime(data_nascimento, '%d/%m/%Y')
data_nascimento = datetime.date.strftime(formatar_data, "%Y-%m-%d")
##Alterar o Login do Aluno para realizar o Login de
s2 = requests.Session()
senha_data = {"Numero":ra, "Digito":digito, "UF":UF, "DataNascimento":data_nascimento+"T02:00:00.000Z"}
setar_senha = s2.post('https://sed.educacao.sp.gov.br/RecuperacaoSenha/AlterarLoginAluno', data=senha_data)
resposta = setar_senha.text;
senha_gerada = json.loads(resposta)
codigo_retorno_senha = senha_gerada['retorno']['CodigoRetorno']
##Msg para o codigo de retorno tipo 1 [ Aluno nao encontrado ]
##Sistema so aceita codigo de retorno tipo 0 [ Aluno encontrado ]
if codigo_retorno_senha is 1:
   print("Este dados de alunos não sao validos..")
   print("python pesquisar.py <R.A> <Digito> <UF> <Data Nascimento> ")
   sys.exit(1)
##Retornar o texto json, capturando as informações de Mensagem e retirando as informações inuteis para termos a nova senha
pegar_senha_gerada = senha_gerada['retorno']['Mensagem']
pegar_senha_gerada = pegar_senha_gerada.replace("Seu login é: "+user+"  -  Sua senha é: ", "")
print('Gerar nova senha [ OK ]')
##Realizando um novo login, para capturar o Token para redifinir uma nova senha
s3 = requests.Session()
s3_data = {"usuario":user, "senha":pegar_senha_gerada}
s3_token = s3.post('https://sed.educacao.sp.gov.br/Logon/LogOn/', data=s3_data)
s3_resposta = s3_token.text;
s3_resposta = json.loads(s3_resposta)
token = s3_resposta['Token']
print('Pegar Token [ OK ]')
##Redifinir Senha, verificando se esta marcado como Ativo
## pegar_senha_gerada = Senha Atual.. Data do Nascimento
# password = A nova senha que queremos, que no caso seria PWGroupHue
if s3_resposta['DefinirSenha'] is True:
   redifinir_data = {"token":token, "senhaAtual":pegar_senha_gerada, "senhaNova":password}
   redifinir_senha = s2.post('https://sed.educacao.sp.gov.br/Logon/AlterarSenha/', data=redifinir_data)
   print('Redifinir Senha [ OK ]')
##Realizando o Login para Capturar os Cookies
##Conectando na pagina  https://sed.educacao.sp.gov.br/Aluno/ConsultaAluno com os Cookies de Login Salvo
s = requests.Session()
s.cookies = http.cookiejar.LWPCookieJar(user)
print('Salvando cookie [ OK ]')
s.cookies.save()
data = {"usuario":user, "senha":password}
r = s.post('https://sed.educacao.sp.gov.br/Logon/LogOn/', data=data)
print('Carregando Cookie [ OK ]')
s.cookies.load(ignore_discard=True)
r = s.get('https://sed.educacao.sp.gov.br/Aluno/ConsultaAluno')
##Criar Arquivo de informações do Aluno
print('Gerando arquivo de dados [ OK ]')
text = r.text;
i = text.find('<div class="row">')
i2 = text[i:].find('</main>')
text1 = "<div id='texto'>"
text = text1+text[i+len('<div class="row">'):i+i2]
text =  "<head><title>Dados " + user +" </title><meta charset='UTF-8'></head>"+text.replace('Meus Dados','')
text = text.replace('disabled="disabled"', '')
arq = open(user+".html", "w")
arq.write(text)
arq.close()
s.cookies.save(ignore_discard=True)
print('Arquivo de dados salvo [ OK ]')
print('Dados salvo no arquivo '+ user+'.html')
os.unlink(user)

##Code By PwGroup@4dr1anCF  [ 2/11/2017 - 23:00 ] ~~ Codigo Publico =)