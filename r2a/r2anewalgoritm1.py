# -*- coding: utf-8 -*-
"""

"""

from player.parser import *
from r2a.ir2a import IR2A


class R2ANewAlgoritm1(IR2A):

    #Inicialização de variáveis
    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []
        
        # Lista com as vazões calculadas
        self.flow_rate = []
        #Variável tempo
        self.request_time = 0
        #Lista de qualidades
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
        Dtime = time.perf_counter() - self.time
        Dlength = msg.get_bit_length()
        flow_rate = Dtime/Dlength
        self.flow.append(flow_rate)

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # time to define the segment quality choose to make the request
        msg.add_quality_id(self.qi[19])
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
