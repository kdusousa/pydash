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
        self.segment_idx = 0
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
        Delta = Dlength/Dtime
        self.flow_rate.append(Delta)
        self.send_up(msg)


    #Definição da qualidade a ser solicitada com base no fluxo (flow_rate)
    def handle_segment_size_request(self, msg):
        
        self.request_time = time.perf_counter()
        avg = statistics.harmonic_mean(self.flow_rate)

        selected_qi = self.qi[0]
        for i in self.qi:
            if avg > i:
                selected_qi = i

        msg.add_quality_id(selected_qi)
        self.send_down(msg)

        

    #metodo que recebe a mensagem de qual qualidade a ser baixada, e calcula
    #com o momento em que foi recebida a vazao e adiciona ela a lista
    def handle_segment_size_response(self, msg):

        Dtime = time.perf_counter() - self.request_time
        Dlength = msg.get_bit_length()
        Delta = Dlength/Dtime
        self.flow_rate.append(Delta)

        self.send_up(msg)       



    def initialize(self):
        pass

    def finalization(self):
        pass