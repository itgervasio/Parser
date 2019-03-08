#!/usr/bin/env python
from simpleparse.parser import Parser
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import DispatchProcessor, dispatch
import operator

class SLAProcessor(DispatchProcessor):

    def SLA(self, (tag, start, stop, subtags), buffer):
        groups = []
        general_terms = []
        guarantees = []

        for x in subtags:
            if x[0] == 'ID':
                #Get the id of the SLA
                iD =  buffer[x[1]:x[2]]
            elif x[0] == 'Group':
                #Add group to the groups list: NAME, List of Metrics, Goup_Metrics
                groups.append(dispatch(self, x, buffer))
            elif x[0] == 'Term':
                #Add terms to the SLA: type, source_party, consumer. If BM: BM_name, BOolean IF LM: LM_name, Elements, List_of_Alternative_Elements (list of list os elements).
                #IF NM: nm_name, Interval(lower, upper bound), OpenClosed(lower, upper), unit
                general_terms.append(dispatch(self, x, buffer))
            elif x[0] == 'Guarantee':
                guarantees.append( dispatch(self, x, buffer ))

        SLA = {'iD' : iD, 'groups' : groups, 'terms' : general_terms, 'guarantees' : guarantees} 
        #print 'PARSER2: ',guarantees


        #print 'ID: ', iD
        #print 'Groups: '
        #for group in groups:
            #print '\tGroup Name'
            #print '\t\t', group['Group_Name']
            #print '\tGroup Metrics:'
            #for metric in group['Terms']:
                #print '\t\tMetric: ', metric
        #print 'General Terms: '
        #for term in general_terms:
            #print '\tTerms', term 
        return SLA

    def Group(self, (tag, start, stop, subtags), buffer):
        terms = []
        for x in subtags:
            if x[0] == 'GroupName':
                #Get the name of the group
                #TODO Remove old group name after verifing where it is used
                group = { 'Group_Name' : buffer[x[1]:x[2]] }
                specific = { 'Metric_Name'  : buffer[x[1]:x[2]], 'Original_Name' : buffer[x[1]:x[2]]  }
                group['specific'] = specific
            elif x[0] == 'Term':
                terms.append( dispatch(self, x, buffer) )
        group['Terms'] = terms

        return group

                

    def Term(self, (tag, start, stop, subtags), buffer):
        for x in subtags:
            if x[0] == 'Standard_Term':
                return dispatch(self, x, buffer)
            if x[0] == 'Group_Metric':
                return dispatch(self, x, buffer)
            

    def Standard_Term(self, (tag, start, stop, subtags), buffer):
        term = dict()
        for x in subtags:
            if x[0] == 'Party':
                term [ 'Source_Party' ] =  buffer[x[1]:x[2]] 
            if x[0] == 'Parties':
                term ['Destination_Parties'] = buffer[x[1]:x[2]].strip().split(',')
            if x[0] == 'Metric':
                term ['type'], term ['specific'] = dispatch(self, x, buffer)
        return term

    def Group_Metric(self, (tag, start, stop, subtags), buffer):
        interval = []
        for x in subtags:
            if x[0] == 'Expr':
                interval.append(dispatch(self, x, buffer))
            if x[0] == 'GroupName':
                group = { 'Metric_Name' : buffer[x[1]:x[2]] }
                group['type'] = 'Group'
                group['specific'] = { 'Metric_Name' : group['Metric_Name'], 'Original_Name' : group['Metric_Name'] }
        group['lower_bound'] = interval[0]
        group['upper_bound'] = interval[1]
        return group

    def Metric(self, (tag, start, stop, subtags), buffer):
        for x in subtags:
            metric_type, specific = dispatch(self, x, buffer)
        return metric_type, specific


    def Numeric_Metric(self, (tag, start, stop, subtags), buffer):
        for x in subtags:
            if x[0] == 'NM':
                NM = buffer[x[1]:x[2]]
            elif x[0] == 'Interval':
                bounds, type_interval = dispatch(self, x, buffer)
            elif x[0] == 'Unit':
                unit = buffer[x[1]:x[2]]

        if type_interval[0] == ']':
            lower_interval = operator.lt
        else:
            lower_interval = operator.le

        if type_interval[1] == ']':
            upper_interval = operator.ge
        else:
            upper_interval = operator.gt
            
        type_interval = { 'lower' : lower_interval, 'upper' : upper_interval }
        specific = { 'Metric_Name' : NM, 'Original_Name' : NM, 'bounds' : bounds,  'type_interval' : type_interval, 'unit' : unit}
        return 'NM', specific
        
    def Boolean_Metric(self, (tag, start, stop, subtags), buffer):
        for x in subtags:
            if x[0] == 'BM':
                BM = buffer[x[1]:x[2]]
            if x[0] == 'Boolean':
                Boolean = dispatch(self, x, buffer)
        specific = { 'Metric_Name' : BM, 'Original_Name' : BM, 'Boolean' : Boolean }
        return  'BM', specific

    def List_Metric(self, (tag, start, stop, subtags), buffer):
        list_elements = []
        for x in subtags:
            if x[0] == 'LM':
                LM = buffer[x[1]:x[2]]
            if x[0] == 'List_Elements':
                list_elements.append(dispatch(self, x, buffer) )
        specific = { 'Metric_Name' : LM, 'Original_Name' : LM,  'List_Elements' : list_elements }
        return 'LM', specific

    def Boolean(self, (tag, start, stop, subtags), buffer):
        boolean = buffer[start:stop]
        if  boolean.lower() == 'true':
            boolean = True
        elif  boolean == 'false':
            boolean = False
        else:
            print 'Error: Boolean must be true or false'
        return boolean

    def List_Elements(self, (tag, start, stop, subtags), buffer):
        return  buffer[start+1:stop-1].split(',')

    def Interval(self, (tag, start, stop, subtags), buffer):
        interval = []
        interval_type = []
        for x in subtags:
            if x[0] == 'Expr':
                interval.append(dispatch(self, x, buffer))
            if x[0] == 'IntervalType':
                interval_type.append(buffer[x[1]:x[2]])
        return interval, interval_type

    def ts(self, (tag, start, stop, subtags), buffer):
        pass

    def Expr(self, (tag, start, stop, subtags), buffer):
        if buffer[start:stop] == '-':
            return None
        else:
            return buffer[start:stop]

    def Guarantee(self, (tag, start, stop, subtags), buffer):
        guarantee = dict()
        for x in subtags:
            if x[0] == 'GuaranteeMetricPrefix':
                result_divided, complete = dispatch(self, x, buffer)
                guarantee.update( result_divided)
            elif x[0] == 'GuaranteeMetric':
                guarantee ['Metric'] = buffer[x[1]:x[2]]
            elif x[0] == 'Event':
                guarantee ['Event'] = buffer[x[1]:x[2]]
            elif x[0] == 'ConditionAction':
                guarantee ['if_conditions_actions'], guarantee ['else_actions'] = dispatch(self, x, buffer)
        guarantee ['Complete_Metric'] = complete.replace(' ','').replace('=>',':').strip() + guarantee['Metric']
        if 'Destination_Parties' not in guarantee.keys():
            guarantee ['Destination_Parties'] = None
        if 'Source_Party' not in guarantee.keys():
            guarantee ['Source_Party'] = None
        if 'Groups' not in guarantee.keys():
            guarantee ['Group'] = None

        return  guarantee

    def GroupSpecification(self, (tag, start, stop, subtags), buffer):
        group = []
        for g in buffer[start:stop].split(':'):
            group.append(g)
        return group

    def ConditionAction(self, (tag, start, stop, subtags), buffer):
        if_conditions = []
        for x in subtags:
            if x[0] == 'If':
                if_conditions.append ( dispatch(self, x, buffer) )
            elif x[0] == 'Else':
                else_condition =  dispatch(self, x, buffer)
        return if_conditions, else_condition

    def If(self, (tag, start, stop, subtags), buffer):
        condition = dict()
        actions = []
        for x in subtags:
            if x[0] == 'BooleanExpr':
               condition [ 'variables' ], condition [ 'operator' ] = dispatch(self, x, buffer)
            elif x[0] == 'Action':
                #TODO FIX ACTIONS
                actions.extend(act for act in (action.strip() for action in buffer[x[1]:x[2]].split('\n')) if act is not '' )
        return (condition, actions)

    def Else(self, (tag, start, stop, subtags), buffer):
        actions = []
        for x in subtags:
            if x[0] == 'Action':
                actions.append(buffer[x[1]:x[2]])
        return actions

    def BooleanExpr(self, (tag, start, stop, subtags), buffer):
        booleanOperator = { '==' : operator.eq, '!=' : operator.ne, '>=' : operator.ge, '>' : operator.gt, '<=' : operator.le, '<' : operator.lt }
        variables = []
        for x in subtags:
            if x[0] == 'ExprGuaranteeMetric':
                variables.append ( dispatch(self, x, buffer) )
            elif x[0] == 'Expr':
                #TODO fix EXPR can be a variable
                variables.append ( {'Value' : buffer[x[1]:x[2]], 'Type' : 'Expr'} )
            elif x[0] == 'BooleanOperator':
                boolean_operator = booleanOperator [ buffer[x[1]:x[2]].strip() ]
        return variables, boolean_operator

    def ExprGuaranteeMetric(self, (tag, start, stop, subtags), buffer):
        metric =  dict()
        for x in subtags:
            if x[0] == 'GuaranteeMetric':
                metric[ 'Value' ] = buffer[x[1]:x[2]]
                metric ['Type'] = 'Metric'
            if x[0] == 'GuaranteeMetricPrefix':
                metric['Prefix'],test = dispatch(self, x, buffer) 
        metric ['Complete_Metric'] = buffer[start:stop].replace(' ','').replace('=>',':').strip()

        return metric

    def GuaranteeMetricPrefix(self, (tag, start, stop, subtags), buffer):
        guarantee = dict()
        for x in subtags:
            if x[0] == 'GroupSpecification':
                guarantee ['Group'] = dispatch(self, x, buffer)
            elif x[0] == 'Party':
                guarantee ['Source_Party'] = buffer[x[1]:x[2]]
            elif x[0] == 'Parties':
                guarantee ['Destination_Parties'] = buffer[x[1]:x[2]].strip().split(',')
        if 'Destination_Parties' not in guarantee.keys():
            guarantee ['Destination_Parties'] = None
        if 'Source_Party' not in guarantee.keys():
            guarantee ['Source_Party'] = None
        if 'Groups' not in guarantee.keys():
            guarantee ['Group'] = None
        return guarantee, buffer[start:stop]

            


class MyParser(Parser):

    def buildProcessor(self):
        return SLAProcessor()

class SLAC(object):

    def parse(self, data):
            with open ("Parser/Grammar", "r   ") as myfile:
                grammar = myfile.read()
            parser = MyParser(grammar, 'start')
            result = parser.parse(data)
            print len(data)
            if result[2] != len(data) and  result [2] != len(data)-1:
                print 'Error Parsing sla ', data[0:result[2]]
                print 'The SLA RECEIVED is: ', data
                print 'The last acceped part is the above, verify if the SLA specification is according to the grammar after that'
            return result[1]


if __name__ == '__main__':
    sla_parser = SLAC()

    #with open ("SLA_EX", "r   ") as myfile:
    with open ("parser/SLA_EX2", "r") as myfile:
            SLA = myfile.read()
    sla_parser.parse(SLA)
