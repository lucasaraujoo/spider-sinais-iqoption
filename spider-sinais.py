from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
from colorama import init, Fore, Back
from time import time
import sys
import os

init(autoreset=True)

def limpa_tela():
	os.system('cls') 
	print(Fore.RED+
	"""
	 _____       _     _                  _____ _             _     
	/  ___|     (_)   | |                /  ___(_)           (_)    
	\ `--. _ __  _  __| | ___ _ __ ______\ `--. _ _ __   __ _ _ ___ 
	 `--. \ '_ \| |/ _` |/ _ \ '__|______|`--. \ | '_ \ / _` | / __|
	/\__/ / |_) | | (_| |  __/ |         /\__/ / | | | | (_| | \__ -
	\____/| .__/|_|\__,_|\___|_|         \____/|_|_| |_|\__,_|_|___/
	      | |                                                       
	      |_|                                            
	"""
	)
	print(Fore.BLUE+'  -> Catalogador de sinais para IQ Option. Versão 3.1.1 - Lucas Araújo <-'+Fore.RESET+'\n')

limpa_tela()
#IMPLEMENTAR : LOGIN E SENHA NO CONFIG
API = IQ_Option('iqoption email', 'password')
API.connect()


if API.check_connect():
	print(' Conectado com sucesso!')
else:
	print(' Erro ao conectar')
	input('\n\n Aperte enter para sair')
	sys.exit()


def cataloga(par, dias, prct_call, prct_put, timeframe):
	data = []
	datas_testadas = []
	time_ = time()
	sair = False
	while sair == False:
		velas = API.get_candles(par, (timeframe * 60), 1000, time_)
		velas.reverse()
		
		for x in velas:	
			if datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d') not in datas_testadas: 
				datas_testadas.append(datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d'))
				
			if len(datas_testadas) <= dias:
				x.update({'cor': 'verde' if x['open'] < x['close'] else 'vermelha' if x['open'] > x['close'] else 'doji'})
				data.append(x)
			else:
				sair = True
				break
				
		time_ = int(velas[-1]['from'] - 1)

	analise = {}
	for velas in data:
		horario = datetime.fromtimestamp(velas['from']).strftime('%H:%M')
		if horario not in analise : analise.update({horario: {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0, 'dir': ''}})	
		analise[horario][velas['cor']] += 1
		
		try:
			analise[horario]['%'] = round(100 * (analise[horario]['verde'] / (analise[horario]['verde'] + analise[horario]['vermelha'] + analise[horario]['doji'])))
		except:
			pass
	
	for horario in analise:
		if analise[horario]['%'] > 50 : analise[horario]['dir'] = 'CALL'
		if analise[horario]['%'] < 50 : analise[horario]['%'],analise[horario]['dir'] = 100 - analise[horario]['%'],'PUT '
	
	return analise

confluencia = False
qtd_confluencia = 1
print('\nDeseja fazer confluência? s/n: ', end='')
confluencia = input().upper()

if confluencia == 'S':
	print('\nInforme a quantidade de listas da confluência (Max 4): ', end='')
	while qtd_confluencia < 2 or qtd_confluencia > 4:
		qtd_confluencia = int(input())


print('\nQual timeframe deseja analisar?: ', end='')
timeframe = int(input())

dias = []
porcentagem = []
filtro = False

for i in range(qtd_confluencia):
	print('')
	print('\nQuantos dias deseja analisar para lista '+(str(i+1))+'? ' if confluencia == 'S' else  '\nQuantos dias deseja analisar?: ', end='')
	input_dias = 0
	while input_dias < 1 or input_dias > 45:
		input_dias = int(input())
	dias.append(input_dias)
	print('\nPorcentagem minima para lista '+(str(i+1))+'? ' if confluencia == 'S' else  '\nPorcentagem minima?: ', end='')
	input_pct = 0
	while input_pct < 1 or input_pct > 100:
		input_pct = int(input())
	porcentagem.append(input_pct)
	print('')

print('\nQuantos Martingales?: ', end='')
martingale = input()

print('\nCatalogar pares abertos ou todos?: ', end='')
tipo_pares = input()

if confluencia != 'S':
	print('\nDeseja Filtrar e ordenar? (s/n)', end='')
	filtro = input() != 'n'

limpa_tela()

P = API.get_all_open_time()

print('\n')

catalogacao = {}

pares = []

catalogacoes = []

if tipo_pares == 'todos':
	pares = ['EURUSD', 'USDJPY', 'AUDUSD', 'EURJPY', 'EURAUD', 'EURCAD', 'EURGBP', 'AUDJPY', 'USDCAD', 'AUDCAD', 'GBPUSD', 'CADJPY', 'USDCHF', 'EURNZD', 'NZDUSD', 'GBPNZD', 'GBPAUD', 'GBPCAD', 'AUDNZD', 'CHFJPY', 'AUDCHF', 'GBPCHF', 'CADCHF', 'GBPJPY', 'USDNOK']
else:
	for par in P['binary']:
		if P['binary'][par]['open'] == True:
			pares.append(par)

	for par in P['digital']:
		if P['digital'][par]['open'] == True and (par not in pares):
			pares.append(par)

print(str(len(pares))+' ATIVOS ENCONTRADOS\n')

for x in range(qtd_confluencia):

	prct_call = abs(porcentagem[i])
	prct_put = abs(100 - porcentagem[i])
	catalogacao = {}
	print('\nINICIANDO CATALOGAÇÃO ('+(str(x+1))+')\n' if confluencia == 'S' else '')

	for par in pares:
		
		timer = int(time())
		print(Fore.GREEN + '*' + Fore.RESET + ' CATALOGANDO - ' + par + '.. ', end='')
		
		catalogacao.update({par: cataloga(par, dias[x], prct_call, prct_put, timeframe)})	
		
		for par in catalogacao:
			for horario in sorted(catalogacao[par]):
				if martingale.strip() != '':					
				
					mg_time = horario
					soma = {'verde': catalogacao[par][horario]['verde'], 'vermelha': catalogacao[par][horario]['vermelha'], 'doji': catalogacao[par][horario]['doji']}
					
					for i in range(int(martingale)):

						catalogacao[par][horario].update({'mg'+str(i+1): {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0} })

						mg_time = str(datetime.strptime((datetime.now()).strftime('%Y-%m-%d ') + str(mg_time), '%Y-%m-%d %H:%M') + timedelta(minutes=timeframe))[11:-3]
						
						if mg_time in catalogacao[par]:
							#catalogacao[par][horario]['mg'+str(i+1)]['verde'] += catalogacao[par][mg_time]['verde'] + soma['verde']
							#catalogacao[par][horario]['mg'+str(i+1)]['vermelha'] += catalogacao[par][mg_time]['vermelha'] + soma['vermelha']
							#catalogacao[par][horario]['mg'+str(i+1)]['doji'] += catalogacao[par][mg_time]['doji'] + soma['doji']

							#!!!EM TESTE
							catalogacao[par][horario]['mg'+str(i+1)]['verde'] += catalogacao[par][mg_time]['verde'] 
							catalogacao[par][horario]['mg'+str(i+1)]['vermelha'] += catalogacao[par][mg_time]['vermelha'] 
							catalogacao[par][horario]['mg'+str(i+1)]['doji'] += catalogacao[par][mg_time]['doji'] 
							
							catalogacao[par][horario]['mg'+str(i+1)]['%'] = round(100 * (catalogacao[par][horario]['mg'+str(i+1)]['verde' if catalogacao[par][horario]['dir'] == 'CALL' else 'vermelha'] / (catalogacao[par][horario]['mg'+str(i+1)]['verde'] + catalogacao[par][horario]['mg'+str(i+1)]['vermelha'] + catalogacao[par][horario]['mg'+str(i+1)]['doji']) ) )
							
							#soma['verde'] += catalogacao[par][mg_time]['verde']
							#soma['vermelha'] += catalogacao[par][mg_time]['vermelha']
							#soma['doji'] += catalogacao[par][mg_time]['doji']
						else:						
							catalogacao[par][horario]['mg'+str(i+1)]['%'] = 'N/A'
			
		print('finalizado em ' + str(int(time()) - timer) + ' segundos')

	print('\n\n')

	for par in catalogacao:
		for horario in sorted(catalogacao[par]):
			ok = False		
			porc_gale = round(porcentagem[x] * 0.77)
			if catalogacao[par][horario]['%'] >= porcentagem[x]:
				#ok = True

				#!!!EM TESTE
				if int(martingale) > 0:
					for i in range(int(martingale)):
						try:
							porc_cat = int(catalogacao[par][horario]['mg'+str(i+1)]['%'])
							#IMPLEMENTAR: PORCENTAGEM GALE NO CONFIG
							ok =  porc_cat >= porc_gale
							if ok == False:
								break
							
						except:
							continue
				else:
					ok = True	
			#IMPLEMENTAR: PORCENTAGEM GALE NO CONFIG
			elif catalogacao[par][horario]['%'] >= porc_gale:
				for i in range(int(martingale)):
					try:
						porc_cat = int(catalogacao[par][horario]['mg'+str(i+1)]['%'])
						if porc_cat >= porcentagem[x]:
							ok = True
							#break

						if ok: 
							porc_gale -= (i+1) 
						else: 
							porc_gale += (i+1)

						if porc_cat < porc_gale:
							ok = False
							break
					except:
						continue
					
					
			
			if ok == True:
			
				msg = Fore.YELLOW + par + Fore.RESET + ' - ' + horario + ' - ' + (Fore.RED if catalogacao[par][horario]['dir'] == 'PUT ' else Fore.GREEN) + catalogacao[par][horario]['dir'] + Fore.RESET + ' - ' + str(catalogacao[par][horario]['%']) + '% - ' + Back.GREEN + Fore.BLACK + str(catalogacao[par][horario]['verde']) + Back.RED + Fore.BLACK + str(catalogacao[par][horario]['vermelha']) + Back.RESET + Fore.RESET + str(catalogacao[par][horario]['doji'])
				
				if martingale.strip() != '':
					for i in range(int(martingale)):
						if str(catalogacao[par][horario]['mg'+str(i+1)]['%']) != 'N/A':
							msg += ' | MG ' + str(i+1) + ' - ' + str(catalogacao[par][horario]['mg'+str(i+1)]['%']) + '% - ' + Back.GREEN + Fore.BLACK + str(catalogacao[par][horario]['mg'+str(i+1)]['verde']) + Back.RED + Fore.BLACK + str(catalogacao[par][horario]['mg'+str(i+1)]['vermelha']) + Back.RESET + Fore.RESET + str(catalogacao[par][horario]['mg'+str(i+1)]['doji'])
						else:
							msg += ' | MG ' + str(i+1) + ' - N/A - N/A' 
							
				print(msg)	
				sinal = 'M'+str(timeframe)+';'+ par + ';'+ horario + ':00;'  + catalogacao[par][horario]['dir'].strip() 
				open('sinais_' + str((datetime.now()).strftime('%Y-%m-%d')) + '_' + str(timeframe) + 'M-'+str(dias[x])+'-'+str(porcentagem[x])+'-'+str(martingale)+'.txt', 'a').write(sinal+'\n')
				catalogacoes.append(sinal)

lista_filtrada = []
if filtro:
	catalogacoes.sort(key=lambda item: datetime.strptime(item.split(";")[2], "%H:%M:%S"))
	for i, sinal in enumerate(catalogacoes):
		ativo1 = sinal.split(";")[1][0:3]
		ativo2 = sinal.split(";")[1][3:6]
		timeatual = datetime.strptime(sinal.split(";")[2], "%H:%M:%S")
		lista_filtrada.append(sinal)
		if i > 0:
			if (timeatual - timeanterior).total_seconds() <= (3 * timeframe * 60):
				if ativo1 in paranterior or ativo2 in paranterior:
					lista_filtrada.remove(sinal)
					try:
						lista_filtrada.remove(sinalanterior)
					except:
						pass
		sinalanterior = sinal
		paranterior = sinal.split(";")[1]
		timeanterior = datetime.strptime(sinal.split(";")[2], "%H:%M:%S")
		

	for sinal in lista_filtrada:
		open('sinais_' + str((datetime.now()).strftime('%Y-%m-%d')) + '_' + str(timeframe) + 'M-'+str(dias[0])+'-'+str(porcentagem[0])+'-'+str(martingale)+'-Filtrada.txt', 'a').write(sinal+'\n')



#inicia a verificação da confleência
if confluencia == 'S': 
	print('\nBUSCANDO CONFLUÊNCIAS...')
	lista_confluencia = []
	lista_divergencia = []
	for sinal in catalogacoes :
		if catalogacoes.count(sinal) == qtd_confluencia:	
			lista_confluencia.append(sinal)
			
		elif catalogacoes.count(sinal) == 1:
			lista_divergencia.append(sinal)
		
		catalogacoes.remove(sinal)

	configuracao = ''
	for i in range(qtd_confluencia):
		configuracao = configuracao +'-('+ str(timeframe) + 'M-'+str(dias[i])+'-'+str(porcentagem[i])+'-'+str(martingale)+')'

	if len(lista_confluencia) > 0:
		for linha in lista_confluencia:
			open('confluencia_' + str((datetime.now()).strftime('%Y-%m-%d')) +'_config' +configuracao +'.txt', 'a').write(linha+'\n')

	if len(lista_divergencia) > 0:
		for linha in lista_divergencia:
			open('divergencia_' + str((datetime.now()).strftime('%Y-%m-%d')) +'_config' +configuracao +'.txt', 'a').write(linha+'\n')


	print('\n'+str(len(lista_confluencia))+' Confluências encontradas!')
	print('\n'+str(len(lista_divergencia))+' Divergencias encontradas!')



