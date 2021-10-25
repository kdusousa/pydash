# -*- coding: utf-8 -*-
"""
Carlos Eduardo de Sousa         Mat: 16/0057701
Edilton Costa Alves             Mat: 17/0002365
Estevam Galṽao Albuquerque      Mat:16/0005663
"""

from player.parser import *
from r2a.ir2a import IR2A
import time
import statistics


class R2ANewAlgoritm1(IR2A):

    #Inicialização de variáveis
    def __init__(self, id):
        IR2A.__init__(self, id)
        #Qualidades disponiveis
        self.parsed_mpd = ''
        #Lista com as qualidades disponíveis
        self.qi = []
        
        # Lista com as vazões calculadas
        self.flow_rate = []
        #Variável tempo
        self.request_time = 0
        #Lista de qualidades já utilizadas
        self.quality = []
        #Variável de acesso ao whiteboard
        self.data = self.whiteboard

    #Chamada ao Connection Handler
    def handle_xml_request(self, msg):
        #recebe o tempo do da requisição
        self.request_time = time.perf_counter()
        self.send_down(msg)

    #Tratamento da requisição
    def handle_xml_response(self, msg):
        # getting qi list
        self.parsed_mpd = parse_mpd(msg.get_payload())
        #store quality
        self.qi = self.parsed_mpd.get_qi()

        #Cálculo da primeira vazão
        Dtime = time.perf_counter() - self.request_time
        Dlength = msg.get_bit_length()
        flow_rate = Dtime/Dlength
        self.flow_rate.append(flow_rate)

        self.send_up(msg)


    #Definição da qualidade a ser solicitada com base no fluxo (flow_rate)
    def handle_segment_size_request(self, msg):
        
        # Momento do pedido
        self.time = time.perf_counter()
        #Armazenamento do tamanho da lista de valores
        values = len(self.flow_rate)
        
        
        #Inicialização da variável média (média harmônica)
        mean = statistics.harmonic_mean(self.flow_rate)
        
        #Até ser atingido o número de 50 amostras na lista, a media sera calculada para
        #menos
        if (values < 50):
            mean = 3*statistics.harmonic_mean(self.flow_rate)/5

        #Atingidas 50 amostras, será feita a media harmônica das ultimas 50
        else:
           list = self.flow_rate[(values-50):]            
           mean = statistics.harmonic_mean(list)


        #Inicialização das variáveis index e quality
        index = 0
        quality = self.qi[0]
        #Loop para definir qi a ser baixado, sendo q o qi tem q ser menor ou igual ao resultado
        #da media
        #quality = valor de qi
        #index = numero da qi(0 a 19)
        for idx, val in enumerate(self.qi):
            if mean >= val:
                quality = val
                index = idx
        
        #size =  numero de elementos na lista
        #buffer = tamanho do buffer no momento
        size = len(self.quality)
        buffer = self.data.get_playback_buffer_size()

        #se houver ja uma qualidade na lista entra nesse if
        #nele sera feito, se o resultado do for passado, ou seja a qualidade escolhida
        #eh menor ou maior que a ultima que foi escolhida antes

        #e analisa o tamanho do buffer, caso ele nao exista ainda, primeiros ifs,
        # a qualidade final sera o resultado do for anterior, se ele tiver pelo menos 5 elementos
        #ja que nao eh sera mudado drasticamente a qualidade, diminuindo ou aumentando
        # em apenas uma unidade, mas caso tenha menos
        #sera mudado imediatamente para o valor do loop for, e se forem iguais nada muda
        if(size>0):
            index_2 = self.quality[(size-1)]
            if (self.qi[index] > self.qi[index_2]):
                if  (len(buffer) == 0):
                    index = index
                elif (buffer[len(buffer)-1][1]>5):
                    index = index
                else:
                    index = index_2 + 1
              
            elif (self.qi[index]<self.qi[index_2]):
                if  (len(buffer) == 0):
                    index = index                
                elif (buffer[len(buffer)-1][1]>5):
                    index = index_2 - 1
                else:
                    index = index
 
            else: 
                index = index_2


        #depois entao eh armazenado aqui a qualidade escolhida no fim e entao eh pedido a ser baixada
        quality = self.qi[index]
        #adiciona a lista essa ultima qualidade escolhida
        self.quality.append(index)

        msg.add_quality_id(quality)
        self.send_down(msg)




    #metodo que recebe a mensagem de qual qualidade a ser baixada, e calcula
    #com o momento em que foi recebida a vazao e adiciona ela a lista
    def handle_segment_size_response(self, msg):

        Dtime = time.perf_counter() - self.time
        Dlength = msg.get_bit_length()
        flow_rate = Dtime/Dlength
        self.flow_rate.append(flow_rate)

        self.send_up(msg)       



    def initialize(self):
        pass

    def finalization(self):
        pass