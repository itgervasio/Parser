#!/usr/bin/env python
from simpleparse.parser import Parser

from simpleparse.common import numbers, strings, comments, chartypes
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import DispatchProcessor, dispatch

class MonitoringDataProcessor(DispatchProcessor):

    def SLAMonitoring(self, (tag, start, stop, subtags), buffer):
        metrics = []

        for x in subtags:
            if x[0] == 'ID':
                #Get the id of the SLA
                sla_iD =  buffer[x[1]:x[2]]
            elif x[0] == 'Metric':
                metrics.append(dispatch(self, x, buffer))

        monitoring = { 'iD' : sla_iD, 'metrics' : metrics } 

        #print 'ID: ', sla_iD
        #print 'Metrics: '
        #for metric in metrics:
            #print '\t\tMetric: ', metric

        return monitoring


    def Metric(self, (tag, start, stop, subtags), buffer):
        metric =  dict()
        for x in subtags:
            if x[0] == 'Constraint':
                metric['Metric_Name'] = buffer[x[1]:x[2]]
            elif x[0] == 'Type':
                metric['Value'], metric['type'] = dispatch(self, x, buffer) 
        return metric

    def Type(self, (tag, start, stop, subtags), buffer):
        for x in subtags:
            return dispatch(self, x, buffer) 

    def Boolean(self, (tag, start, stop, subtags), buffer):
        boolean = buffer[start:stop]
        if  boolean.lower() == 'true':
            boolean = True
        elif  boolean == 'false':
            boolean = False
        else:
            print 'Error: Boolean must be true or false'
        return boolean, 'BM'

    def List_Elements(self, (tag, start, stop, subtags), buffer):
        return  buffer[start+1:stop-1].split(','), 'LM'


    def ts(self, (tag, start, stop, subtags), buffer):
        pass

    def Numbers(self, (tag, start, stop, subtags), buffer):
        return buffer[start:stop], 'NM'

class MonitoringParser(Parser):

    def buildProcessor(self):
        return MonitoringDataProcessor()

class Monitoring_Parser(object):

    def parse(self, data):
            with open ("Parser/Grammar_Monitoring", "r   ") as myfile:
                grammar = myfile.read()
            parser = MonitoringParser(grammar, 'start')
            result = parser.parse(data)
            if result[2] != len(data) and  result [2] != len(data)-1:
                print 'Error Parsing Monitoring Data: ', data[0:result[2]]
                print 'The last acceped part is the above, verify if the Monitoring specification is according to the grammar after that'
            return result[1]


if __name__ == '__main__':
    sla_parser = Monitoring_Parser()

    #with open ("SLA_EX", "r   ") as myfile:
    with open ("Monitoring/Data_EX", "r") as myfile:
            SLA = myfile.read()
    sla_parser.parse(SLA)
