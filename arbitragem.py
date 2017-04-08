# -*- coding: utf-8 -*-

''' DESCRIÇÃO DO ALGORITMO :
O algoritmo carrega todos os ciclos possiveis já calculados anteriormente em outra versão atraves de grafos e salvos em um txt chamado 
"Percussos" Pega os valores de compra(Bids) e de venda(Asks) na poloniex para cada par de moeda que pode fazer parte de um ciclo salva
 em um txt. Se o Bitcoin vale 1100 USDT(dolar tether) entao 1 USDT vale 1/1100 BTC e assim é salvo todos os valores dos pares de moeda 
 nas duas direções no arquivo Asks.txt e Bids.txt ... essa parte de "atualizar " esses vaores de compra e venda dos pares eh feito dentro
 do getStatus(). (OBS : existe um erro q não sei ainda como contornar... quando existe um erro na rede ou esta sem internet o algoritmo
 entra em uma exception q fecha o programa) diferente de um erro na internet ou na poloniex q retorna um Request normal ... ERROR 404 ou 200
 REQUISIÇÃO FEITA COM SUCESSO  etc.
 
 Apos a atualização para cada ciclo em Percussos é feito o um calculo que consiste simplesmente em caminhar pelo ciclo comprando e vendendo 
 na ordem dada e depois é visto se ao terminar retornou com mais dinheiro q entrou. No caso das criptomoedas por ser mercado muito recente
 existem moedas q nao tem liquidez e ficam "paradas" e entre os compradores e os vendedores exitem um GAP , por conta disso o ciclo em um 
 sentido nao retorna simplesmente o oposto no outro sentido q seria : se um ciclo em um sentido da 0,8% de prejuizo no outro deveria dar 0,8%
 de lucro, mas não é assim com as criptomoedas.Os valores sao muitas vezes totalmente diferentes, entao os ciclos sao calculados nos dois sentidos.

Apos atualizar os Asks e Bids e caminhar pelos ciclos e verificar se retorna mais dinheiro q entrou é visto tambem quanto é gasto de taxa
com as transações e verificado se ainda assim possui lucro. OBS : alguns ciclos não começam com bitcoin, porem toda moeda pode ser trocada 
com bitcoin , Entao para esses ciclos são adicionados nas taxas a de comprar atraves do bitcoin para entrar no ciclo e a de vender a ultima
moeda apos terminar o ciclo para ficar tudo em bitcoin. Apos retirar as taxas o retorno final so é salvo se for maior ou igual ao valor 
do lucro esperado colocado pelo usuario


OBS : as moedas são "chamadas" muitas vezes apenas pela posição em um vetor ex : BTC é a moeda numero 0 , USDT é 19 ....


   '''



import requests 
import time
from datetime import datetime

def carregaPercussos():                 ############ Carrega os ciclos que estão em um arquivo txt
    p = open("Percussos.txt","r")
    texto = p.readlines()
    p.close()

    for linha in texto :
        texto[texto.index(linha)] = linha.replace("[","").replace("]","").replace("\n","").split(",")
    return texto
    
def taxa(x):                          ##############   Calcula o valor gasto com taxas
    y = (1.0 - 0.0015)**x
    y = 1 - y
    #print(y*100)
    return y*100 
    
def compensa(bruto, tamanho, minimo):      ########### Retorna se compensa determinado ciclo subtraindo do retorno bruto o gasto com taxas 
    retorno = bruto - (100 + taxa(tamanho))
    #print(str(retorno))
    if (retorno >= float(minimo)):
        return True
    else:
        return False

def PecorrePercusso(percussos, Cripto_M ,asks, bids, mercados, contTemp, minimoDeLucro): # Faz a parte de pecorrer o percusso, retirar as taxas e verificar se o retorno é maior q o esperado se for envia para o telegram

    for percusso in percussos:

        v = calculaLucros(percusso, Cripto_M ,asks, bids, mercados)
        quantidadeOperacao = len(percusso) - 1
        if (percusso[0] != 0):
            quantidadeOperacao = quantidadeOperacao + 2
        if (contTemp < 60*3):

            nomeArq2  = "Caminho " + str(percussos.index(percusso)) + ".txt"
            arquivoCaminho = open(nomeArq2,"a")
            arquivoCaminho.write(str(v))
            arquivoCaminho.write("     ")
            arquivoCaminho.write(str(datetime.now()))
            arquivoCaminho.write("\n")
            arquivoCaminho.close()
        elif (contTemp > 60*3):
            contTemp = 0
        if (compensa(v,quantidadeOperacao,float(minimoDeLucro))):
            nomeArq  = "R_Lucr_Liq_C" + str(percussos.index(percusso)) + ".txt"
            arquivo = open(nomeArq,"a")
            tax = taxa(quantidadeOperacao)
            conteudo = "Bruto = " + str(v) + " taxas : " + str(tax) + " Lucro : " + str((v - tax)-100) + "\n" 
            mensagem = " Lucro caminho : " + str((v - tax) - 100) + " " + str(percussos.index(percusso)) + " " + str(percussos.index(percusso))
            enviar_luca = "https://api.telegram.org/bot377228323:AAHcU7LjQ2NaObxzyrKPYo1yBAqE8MLeDbE/sendMessage?text=" + mensagem + "&chat_id=86791355"
            enviar_henrique = "https://api.telegram.org/bot377228323:AAHcU7LjQ2NaObxzyrKPYo1yBAqE8MLeDbE/sendMessage?text=" + mensagem + "&chat_id=95778171"
            print("enviando porcentagem do lucro para telegram")
            telegramBot = requests.get(enviar_luca)            
            telegramBot = requests.get(enviar_henrique)

            if (telegramBot.status_code == 200):
                print("menssagem enviada para o telegram")
            else:
                print("erro ao enviar menssagem ao telegram")
            
            arquivo.write(conteudo)
            arquivo.close()

        percusso.reverse()
        v = calculaLucros(percusso, Cripto_M ,asks, bids, mercados)
        quantidadeOperacao = len(percusso) - 1
        if (percusso[0] != 0) :
            quantidadeOperacao = quantidadeOperacao + 2
        if (compensa(v, quantidadeOperacao, float(minimoDeLucro))):
            nomeArq ="INVERT_R_Lucr_Liq_" + str(percussos.index(percusso)) + ".txt"
            arquivo = open(nomeArq,"a")
            tax = taxa(quantidadeOperacao)
            conteudo = "Invertido Bruto = " + str(v) + " taxas : " + str(tax) + " Lucro : " + str((v - tax) -100) + "\n" 
            mensagem = " Lucro CaminhoInvertido "+ str(percussos.index(percusso)) + " " + str((v - tax) - 100) + " " + str(percussos.index(percusso)) + " valor ja retirado taxa"
            enviar_luca = "https://api.telegram.org/bot377228323:AAHcU7LjQ2NaObxzyrKPYo1yBAqE8MLeDbE/sendMessage?text=" + mensagem + "&chat_id=86791355"
            enviar_henrique = "https://api.telegram.org/bot377228323:AAHcU7LjQ2NaObxzyrKPYo1yBAqE8MLeDbE/sendMessage?text=" + mensagem + "&chat_id=95778171"
            print("enviando porcentagem do lucro para telegram")
            telegramBot = requests.get(enviar_luca)
            telegramBot = requests.get(enviar_henrique)
            if (telegramBot.status_code == 200):
                print("menssagem enviada para o telegram")
            else:
                print("erro ao enviar menssagem ao telegram")
            arquivo.write(conteudo)
            arquivo.close()

    for sec in range(10):
        time.sleep(1)
        tempo = 10 - sec
        contTemp = contTemp + 1
        print(str(tempo) +  " segundos para proxima requisicao")

def guardaLucro(percussos, Cripto_M, asks, bids, mercados):
    valorLucro = open("LUCROS.txt",'w')
    for percusso in percussos:
        v = calculaLucros(percusso, Cripto_M, asks, bids, mercados)
        quantidadeOperacao = len(percusso) - 1
        if (percusso[0] != 0):
             quantidadeOperacao = quantidadeOperacao + 2
        
        if (v > 100):
            texto = "CAMINHO : " + str(percussos.index(percusso)) + "       DE PERCSSO : "+  str(percusso) + "      VALOR :  " + str(v) + '  e tamanho : ' + str(quantidadeOperacao)
            valorLucro.write(texto)
            valorLucro.write("\n\n\n")
            
        percusso.reverse()
        v = calculaLucros(percusso, Cripto_M, asks, bids, mercados)
        if v > 100 :
            texto = "CAMINHO(invertido) : " + str(percussos.index(percusso)) + "       DE PERCUSSO : " + str(percusso) + "      VALOR :  " + str(v) +'  e tamanho : ' + str(quantidadeOperacao)
            valorLucro.write(texto)
            valorLucro.write("\n\n\n")
           
    valorLucro.close()

def calculaLucros(caminho, Cripto_M, asks, bids, mercados):

    pesos = list()
    for a in range((len(caminho)-1)) :
        vertex1 = int(caminho[a])
        vertex2 = int(caminho[a +1])
        
        par = Cripto_M[int(vertex1)],Cripto_M[int(vertex2)]
        teste = buyOrSell(par, mercados)
        if (teste == 'BUY'):
            valores = asks[vertex1][vertex2]
            pesos.append(float(valores))
        elif (teste == 'SELL'):
            valores = bids[vertex1][vertex2]
            pesos.append(valores)

        #print(vertex1," ,",vertex2," ",pesos[len(pesos)-1] )

    lucro = 1.0

    for a in pesos:
        peso = float(a)
        lucro = peso*lucro

    return(lucro*100)

# A função buyOrSell olha se vc vai ter q olhar as ordens de compra ou as de vendas. Ex :
# Se no ciclo tem q vc sai do bitcoin para USDT significa q vc vai "Vender" seu BTC por usdt  . So que nao exite no mercado de bitcoin/dolar
#  o USDT, se vc for na poloniex e ver o mercado de bitcoin nao tem USDT, pq na vdd é no mercado de USDT que esta o bitcoin entao vc vai "comprar"
# USDT com bitcoin no mercado de USDT/BTC em vez de vender BTC no mercado de BTC/USDT pq não existe BTC/USDT .
def buyOrSell(pair, mercados):
    pair = pair # Pra que isso??    R : o pair = pair ? acho q era pra ter um "this" aqui . pra diferenciar. nao lembro mais kkkk
    count0 = 0
    count1 = 0
    if (pair[0] in mercados):
        count0 = count0 + 1
    if (pair[1] in mercados):
        count1 = count1 + 1

    if (count1 and count0):         

         if (pair[0] == 'USDT' and (pair[1] == 'BTC' or pair[1] == 'XMR' or pair[1] == 'ETH')):
            return 'BUY' #OLHAR ORDENS DE VENDAS 
         elif ((pair[0] == 'BTC' or pair[0] == 'XMR' or pair[0] == 'ETH') and (pair[1] == 'USDT')):
            return 'SELL' # OLHAR ORDENS DE COMPRAS
         elif (pair[0] == 'BTC'):
            return 'BUY'
         elif (pair[1] == 'BTC'):
            return 'SELL'

    elif (count0):
        return  'BUY' #olhar ordens de vendas
    elif (count1):
        return 'SELL' #olhar ordens de compras

def getStatus(Cripto_M, asks, bids):
    
    response = requests.get('https://poloniex.com/public?command=returnTicker')    

    if (response.status_code == 200):
    
        x = response.json()
        for dados in x:
            for moeda in Cripto_M:
                par = dados.split("_")
                for moeda2 in Cripto_M:
                    if moeda != moeda2 :
                        if moeda == par[0] :
                            if moeda2 == par[1]:
                                asks[Cripto_M.index(par[0])][Cripto_M.index(par[1])] = 1/float(x[dados]["lowestAsk"])
                                asks[Cripto_M.index(par[1])][Cripto_M.index(par[0])] = float(x[dados]["lowestAsk"])
                                bids[Cripto_M.index(par[0])][Cripto_M.index(par[1])] = 1/float(x[dados]["highestBid"])
                                bids[Cripto_M.index(par[1])][Cripto_M.index(par[0])] = float(x[dados]["highestBid"])

        return "OK"
    else:
        print("Nao foi possivel efetuar a requisicao ou poloniex nao respondeu ....")
        print("resposta foi ..... "+ response.status_code)
        return "NOT OK"

def salvarAsksAndBids(n_moedas, asks, bids):
    arqBid = open("Bids.txt","w")
    arqAsk =open("Asks.txt","w")
    for linha in range(n_moedas):
        for coluna in range(n_moedas):
            if (asks[linha][coluna] != None):
                valorAsk = str(asks[linha][coluna])
            else:
                valorAsk = "None"
            if (bids[linha][coluna] != None) :
                valorBid = str(bids[linha][coluna])
            else:
                valorBid = "None"
            espaco =" "
            texto = "(" + str(linha) + "," + str(coluna) + ")  :" + valorAsk 
            espaco = espaco*(35 - len(texto))
            arqAsk.write(texto + espaco)
            texto = "(" + str(linha) + "," + str(coluna) + ")  :" + valorBid + "   "
            espaco =" "
            espaco = espaco*(35 - len(texto))
            arqBid.write(texto + espaco)
        arqAsk.write("\n")
        arqBid.write("\n")
    arqAsk.close()
    arqBid.close()

def main():

    mercados = ['USDT','BTC','ETH','XMR']
    Cripto_M = ['BTC','ETC','ETH','XMR','LTC','DASH','ZEC','XRP','NXT','REP','STR','LSK','STEEM','MAID','BBR','BTCD','QORA','BCN','BLK','USDT']
    n_moedas = len(Cripto_M)
    asks = list(list())
    bids = list(list())
    contTemp = 0
    percussos = carregaPercussos()
    
    # Inicializa as listas valor1, valor2, asks e bids com None 
    for linha in range(n_moedas):
        valor = list() # Pra que serve essa lista? R : So pra ficar logo uma matriz de asks carregada com alguma coisa, pra fazer coisas do tipo Asks[3][4] == None 
        valor1 = list()
        valor2 = list()
        iniciador = list() # Pra que serve essa lista? R: Isso foi pq eu tava começando a implementar a parte de contar o tempo , mas fiquei sem pc, no momento serve pra nada

        for coluna in range(n_moedas):
            a1 = (None)
            a2 = (None)
            valor1.append(a1)
            valor2.append(a2)
        asks.append(valor1)
        bids.append(valor2)

    minimoDeLucro = input("Qual o mínimo de lucro ?\n")

    mensagem = " iniciando loop"
    enviar_luca = "https://api.telegram.org/bot377228323:AAHcU7LjQ2NaObxzyrKPYo1yBAqE8MLeDbE/sendMessage?text=" + mensagem +"&chat_id=86791355"
    enviar_henrique = "https://api.telegram.org/bot377228323:AAHcU7LjQ2NaObxzyrKPYo1yBAqE8MLeDbE/sendMessage?text=" + mensagem +"&chat_id=95778171"
    telegramBot= requests.get(enviar_luca)
    telegramBot = requests.get(enviar_henrique)

    
    continuar = True
    while (continuar):    

        status = getStatus(Cripto_M, asks, bids)
        if (status == "OK"):
            salvarAsksAndBids(n_moedas, asks, bids)
            PecorrePercusso(percussos, Cripto_M, asks, bids, mercados, contTemp, minimoDeLucro)
            guardaLucro(percussos, Cripto_M, asks, bids, mercados)  

        c = input("deseja continuar ? \n")
        if (c == "s"):
            continuar = True
        else:
            continuar = False

        time.sleep(1)
        
if __name__ == "__main__": # nao sei pra q serve isso kkkkk , aprendi python meio q so pelo q ia precisando. nunca precisei disso , mas ja vi
    main()
