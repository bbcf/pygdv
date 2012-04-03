# -*- coding: utf-8 -*-
'''
This will define function that will be used to build an external web form.
It will be combined with an external javascript file to produce the form desired.
'''

elements_types = ('radio_choice', 'boolean', 'drop_container', 'number')
drop_container_types = ('ntracks', 'filter')
''' WARNING : you cannot add another drop_container type without modifying the controller who handle
the tracks '''
form_ids_template = 'gfm_el'

################################################################################
class FormExpose(object):
    '''
    Class that output the JSON and mean to be understood by the external javascript to produce a web form.
    '''

    def __init__(self, title, childs):
        '''
        @param title : the title of the form
        @type title : a string
        @param childs : the childs buttons
        @type childs : a list of FormButtons
        '''
        self.title = title
        self.childs = childs
        self.id = 0 #an icremental number to get uniques id

    @property
    def next_id(self):
        '''
        Get an unique id for elements in the form.
        @return an unique string based on 'form_ids_template'
        '''
        self.id += 1
        return form_ids_template+'_%s' % self.id

    def output(self):
        '''
        Will output the JSON.
        @return: the JSON needed by the javascript
        '''
        final_data = {'title':self.title, 'form_ids_template':form_ids_template}
        for child in self.childs :
            child_data = {self.next_id:child.output(self)}
            final_data[self.next_id] = child.output(self)
        return final_data

################################################################################
class FormButton(object):
    """
    A form button.
    A form button can be just an element that lead to other elements, or
    it can lead to the display of a form.
    """

    def __init__(self, name, do_form, childs, parameters=None):
        """
        @param name : the name to be displayed
        @type name : a string
        @param childs : the childs buttons or childs form elements
        @type childs : a list of FormButtons or FormElement
        @param do_form : leading to display the form?
        @type do_form : a boolean
        @param parameters : parameters needed by gFeatMiner to identify the request
        @type parameters : a dict
        """
        self.name = name
        self.do_form = do_form
        self.childs = childs
        self.parameters = parameters

    def __str__(self):
        return '< FormButton : name: %s, doform: %s, childs: %s, parameters: %s >' % (self.name, self.do_form, self.childs, self.parameters)

    def output(self,root):
        '''
        Output the JSON.
        @param root a link to the root
        @type the FormExpose parent
        '''
        final_data = {'name':self.name}
        if self.do_form : #final item, should have parameters
            final_data['doform']='true'
            if self.parameters :
                final_data['parameters']=self.parameters
            else :
                print 'Warning : there is no parameters defined for "%s"' % self.name
            # add all FormElements
            # store defined drop_container because it can only have one of each type maximum
            drop_containers = []
            for child in self.childs :
                if child.type == 'drop_container' and len(drop_containers)>0:
                    if (drop_containers[0].id == child.id):
                        raise Exception('Warning : this drop container id (%s) is already defined (%s)' % (child.id, child.name))
                else :
                    drop_containers.append(child)
                tmp_data = {}
                # don't keep the None values
                for k, v in child.__dict__.items() :
                    if v == True :
                        tmp_data[k] = 'true'
                    elif v :
                        tmp_data[k] = v
                final_data[root.next_id]=tmp_data
        else : # just intermediate, continue recursively
            for child in self.childs :
                final_data[root.next_id]=child.output(root)
        return final_data

################################################################################
class FormElement(object):
    """
    A form element.
    It can represent a checkbox, textarea, etc ... on the web form.
    The different possible types are given by the tuple 'elements_types'
    """

    def __init__(self, name, type, id, radio_values=None, help_text=None):
        '''
        @param name : the name to be displayed
        @type name : a string
        @param type : the element type
        @type type : one of 'elements_types'
        @param id : the identifier of the parameter in the final form. It must be unique through all items in the form.
        @param id : a string.
        @param radio_values : values for the radio choice
        @type radio_values : a list of string
        @param help_text : a text that help user to understand what is this field for
        @type help_text : a string
        '''
        if type not in elements_types : raise Exception('Type "%s" not authorized. Must be one of %s.' % (type, elements_types))
        self.name = name
        if type == 'drop_container' and id not in drop_container_types :
            raise Exception('Id "%s" not authorized for drop_container. Must be one of %s.' % (id, drop_container_types))
        self.id = id
        self.radio_values = radio_values
        self.help_text = help_text
        self.type = type

    def __str__(self):
        return '< FormElement : name: %s, type: %s, id: %s, radio_values: %s, help_text: %s >' % (self.name, self.type, self.id, self.radio_values, self.help_text)

################################################################################
def gFeatMiner_output():
    '''
    Produce the output needed to expose gFeatMiner methods in GDV.
    '''
    # Some definitions of elements #
    output_type     = FormElement("Output type",    'radio_choice', 'output_type', radio_values=['qualitative','quantitative'])
    input_type      = FormElement("Input type",     'radio_choice', 'input_type', radio_values=['qualitative','quantitative'])
    threshold_value = FormElement("Threshold value",'number', 'threshold', help_text='Choose a cut off value.')
    ntracks         = FormElement("List of tracks", 'drop_container', 'ntracks')
    filter          = FormElement("Filter",         'drop_container', 'filter')
    compare_parents = FormElement("Compare with parents", 'boolean', 'compare_parents')
    per_chromosomes = FormElement("Per chromosomes", 'boolean', 'per_chromosomes')
    log_scale       = FormElement("Log scale",       'boolean', 'log_scale')
    before_start    = FormElement("Before start",    'number', 'before_start', help_text='.')
    before_end      = FormElement("Before end",      'number', 'before_end',   help_text='.')
    after_start     = FormElement("After start",     'number', 'after_start',  help_text='.')
    after_end       = FormElement("After end",       'number', 'after_end',    help_text='.')

    # Descriptive statistics #
    base_coverage      = FormButton("Base Coverage",       True, [compare_parents, per_chromosomes, ntracks, filter],
                         parameters={'operation_type':'desc_stat','characteristic':'base_coverage'})
    number_of_features = FormButton("Number of features",  True, [compare_parents, per_chromosomes, ntracks, filter],
                         parameters={'operation_type':'desc_stat','characteristic':'number_of_features'})
    length             = FormButton("Length distribution", True, [compare_parents, per_chromosomes, ntracks, filter],
                         parameters={'operation_type':'desc_stat','characteristic':'length'})
    score              = FormButton("Score distribution",  True, [compare_parents, per_chromosomes, ntracks, filter],
                         parameters={'operation_type':'desc_stat','characteristic':'score'})

    # Descriptive statistics #
    correlation        = FormButton("Cross-correlation",  True, [ntracks],
                         parameters={'operation_type':'plot','plot':'correlation'})
    scatter            = FormButton("Two signal scatter",  True, [ntracks, log_scale],
                         parameters={'operation_type':'plot','plot':'scatter'})

    # Genomic manipulations: boolean #
    bool_and               = FormButton("AND", True, [ntracks],
                             parameters={'operation_type':'genomic_manip','manipulation':'bool_and'})
    bool_or                = FormButton("OR",  True, [ntracks],
                             parameters={'operation_type':'genomic_manip','manipulation':'bool_or'})
    bool_not               = FormButton("NOT", True, [ntracks],
                             parameters={'operation_type':'genomic_manip','manipulation':'bool_not'})
    bool_xor               = FormButton("XOR", True, [ntracks],
                             parameters={'operation_type':'genomic_manip','manipulation':'bool_xor'})
    booleans = FormButton("Booleans", False, [bool_and, bool_or, bool_not, bool_xor])

    # Genomic manipulations: other #
    mean_score_by_features = FormButton("Mean score (by feature)", True, [ntracks],
                             parameters={'operation_type':'genomic_manip','manipulation':'mean_score_by_feature'})
    filter_track           = FormButton("Filter",      True, [ntracks],
                             parameters={'operation_type':'genomic_manip','manipulation':'filter'})
    merge                  = FormButton("Merge",       True, [ntracks, output_type],
                             parameters={'operation_type':'genomic_manip','manipulation':'merge'})
    threshold              = FormButton("Threshold",   True, [ntracks, threshold_value, output_type],
                             parameters={'operation_type':'genomic_manip','manipulation':'threshold'})
    neighborhood           = FormButton("Neighborhood",True, [ntracks, output_type, before_start, before_end, after_start, after_end],
                             parameters={'operation_type':'genomic_manip','manipulation':'neighborhood'})

    # First level drop-down menu in the side bar #
    stats  = FormButton("Statistics",    False, [base_coverage, number_of_features, length, score])
    plots  = FormButton("Plots",         False, [correlation, scatter])
    manips = FormButton("Manipulations", False, [booleans, mean_score_by_features, filter_track, merge, threshold, neighborhood])

    # Title #
    menu = FormExpose('gFeatMiner', [stats, plots, manips])
    return menu.output()

if __name__ == '__main__':
    print gFeatMiner_output()

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
