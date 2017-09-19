#TODO - Find out why nameless reverse-related field made for dinosaur
#TODO - Handle tokens named specific things - Ragavan rather than Monkey
    #TODO - perhaps just search for matching type rather than look for the name?
#TODO - search inputs folder for a non-token xml, stop relying on inputFileName for local inputs
#TODO - automatically draw from customsets folder & local tokens.xml, write to customsets folder

import re
import requests

presets = {
    'inputFileName': 'spoiler', #either a set code like 'XLN' or else 'spoiler'
    'cacheInputs': False, #if true, saves the inputs to 'cache' folder
    'tryLocalInputs': False #if true, tries to use local input files (local input files could be made by cacheInputs)
}


def read_xml(name):
    with open(name, 'r') as f:
        output = f.read()
    return output

def split_cards(xml_file):
    m = re.findall('(?<=<card>).*?(?=</card>)', xml_file, re.DOTALL)
    return m

def parse_cards(card_list):
    output_dict = dict()
    for card_raw in card_list:
        name = re.findall('(?<=<name>).*?(?=</name>)', card_raw)[0]
        text_list = re.findall('(?<=<text>).*?(?=</text>)', card_raw, re.DOTALL)
        if (len(text_list) !=0): #not-vanilla check
            text = text_list[0]
            token_slabs_single = re.findall('[C|c]reate.*?[A-WYZ][a-z]*', text) #produces slabs of words from creates to single token name
            token_slabs_double = re.findall('[C|c]reate.*?[A-WYZ][a-z]* [A-Z][a-z]*', text)
            token_slabs_single
            tokens = []
            for token_slab in token_slabs_double:
                words = token_slab.split()
                token = words[len(words)-2] + ' ' + words[len(words)-1]
                tokens.append(token)
            for token_slab in token_slabs_single: #handles multiple tokens from one card
                #trim to just the name of the token
                words = token_slab.split()
                token = words[len(words)-1]
                for already_found in tokens: #avoids adding Cat when Cat Wizard is already found
                    if token == already_found.split()[0]:
                        break
                else:
                    tokens.append(token)
            if len(tokens) != 0:
                output_dict[name] = tokens
    return output_dict

def extract_set(xml_file):
    sets = []
    m = re.findall('(?<=<set>).*?(?=</set>)', xml_file, re.DOTALL)
    for set_slab in m:
        n = re.findall('(?<=<name>).*?(?=</name>)', set_slab, re.DOTALL)[0]
        sets.append(n)
    print('SETS: ', sets)
    return sets

def split_tokens(xml_file):
    m = re.findall('(?<=<card>).*?(?=</card>)', xml_file, re.DOTALL)
    return m

def reduce_tokens(token_list, setCodes):
    output_list = []
    for token in token_list:
        this_token_set_slab = re.findall('<set.*?</set>', token)[0]
        this_token_set = re.findall('(?<=>)[A-Za-z0-9]*?(?=<)', this_token_set_slab)[0].upper() #upper is extra redundancy
        for setCode in setCodes:
            if this_token_set == setCode:
                output_list.append(token)
    return output_list

def mash_tokens(reduced_token_list, token_card_dict):
    modified_token_list = []
    for unique_token, ass_cards_names in token_card_dict.iteritems():
        for token in reduced_token_list:
            token_name = re.findall('(?<=<name>).*?(?=</name>)', token)[0].lstrip().rstrip()
            if unique_token == token_name:
                #write reverse_related
                modified_token = token.rstrip().lstrip()
                modified_token = '\t\t<card>\n\t\t\t' + modified_token
                for ass_card_name in ass_cards_names:
                    modified_token = modified_token + '\n\t\t\t<reverse-related>' + ass_card_name + '</reverse-related>'
                modified_token = modified_token + '\n\t\t</card>\n'
                modified_token_list.append(modified_token)
                break
        else:
            print 'ERROR: Could not find token named ' + unique_token+ ' for ' + str(ass_cards_names)
    return modified_token_list

def  invert_dict(card_token_dict):
    redundant_token_names_list = []
    for token_names in card_token_dict.itervalues():
        for token_name in token_names:
            redundant_token_names_list.append(token_name)
    tokens_set = set(redundant_token_names_list)
    inverted_dict = {}
    for unique_token in tokens_set:
        ass_card_names = []
        for card_name, token_names in card_token_dict.iteritems():
            for token_name in token_names:
                if token_name == unique_token:
                    ass_card_names.append(card_name)
        inverted_dict[unique_token] = ass_card_names
    return inverted_dict

def write_new_xml(token_list, file_name, sets):
    all_sets_text = '<?xml version="1.0" encoding="UTF-8"?>\n<cockatrice_carddatabase version="3">\n\t<cards>\n'
    for set in sets:
        this_set_text = '<?xml version="1.0" encoding="UTF-8"?>\n<cockatrice_carddatabase version="3">\n\t<cards>\n'
        for token in token_list:
            sets_of_token_slabs = re.findall('(?<=<set).*?(?=/set)', token)
            for set_of_token_slab in sets_of_token_slabs:
                set_of_token = re.findall('(?<=>).*?(?=<)', set_of_token_slab)[0]
                if set_of_token == set:
                    this_set_text = this_set_text + token
                    all_sets_text = all_sets_text + token
        this_set_text = this_set_text + '\t</cards>\n</cockatrice_carddatabase>'
        with open(set + '_tokens.xml', 'w') as f:
            f.write(this_set_text)
    if len(sets) > 1:
        with open(file_name + '_tokens.xml', 'w') as f:
            f.write(all_sets_text)

def open_tokens_xml(cacheInputs, tryLocalInputs):
    tokens_xml = ''
    if tryLocalInputs == True:
        try:
            with open('tokens.xml', 'r') as f:
                tokens_xml = f.read()
            print "Using local 'tokens.xml' as token source"
        except IOError:
            try:
                with open('raw_tokens.xml', 'r') as f:
                    tokens_xml = f.read()
                print "Using local 'raw_tokens.xml' as token source"
            except IOError:
                print "ERROR: Can't find tokens.xml or raw_tokens.xml locally, requesting from github..."
                tokens_xml = requests.get('https://raw.githubusercontent.com/Cockatrice/Magic-Token/master/tokens.xml').text.encode('utf-8')
    else:
        tokens_xml = requests.get('https://raw.githubusercontent.com/Cockatrice/Magic-Token/master/tokens.xml').text.encode('utf-8')
    if cacheInputs == True:
        print 'Saving raw_tokens.xml cache'
        with open('raw_tokens.xml', 'w') as f:
            f.write(tokens_xml)
    return tokens_xml

def open_cards_xml(setCode, cacheInputs, tryLocalInput):
    cards_xml = ''
    if tryLocalInput == True:
        try:
            with open(setCode + '.xml', 'r') as f:
                cards_xml = f.read()
            print 'Using local ' + setCode + '.xml as card source'
        except IOError:
            print "ERROR: Cam't find " + setCode + ".xml locally, requesting from github..."
            cards_xml = requests.get('https://raw.githubusercontent.com/Cockatrice/Magic-Spoiler/files/' + setCode + '.xml').text.encode('utf-8')

    else:
        cards_xml = requests.get('https://raw.githubusercontent.com/Cockatrice/Magic-Spoiler/files/' + setCode + '.xml').text.encode('utf-8')
    if cacheInputs == True:
        print ('Saving ' + setCode + '.xml cache')
        with open(setCode + '.xml', 'w') as f:
            f.write(cards_xml)
    return cards_xml


if __name__ == '__main__':
    tokens_xml = open_tokens_xml(presets['cacheInputs'], presets['tryLocalInputs'])
    cards_xml = open_cards_xml(presets['inputFileName'], presets['cacheInputs'], presets['tryLocalInputs'])
    sets = extract_set(cards_xml)
    card_list = split_cards(cards_xml)
    card_token_dict = parse_cards(card_list)
    inverted_token_card_dict = invert_dict(card_token_dict) #needed so that multiple cards can produce the same token
    token_list = split_tokens(tokens_xml)
    reduced_token_list = reduce_tokens(token_list, sets)
    mashed_list = mash_tokens(reduced_token_list, inverted_token_card_dict)
    write_new_xml(mashed_list, presets['inputFileName'], sets)
    print card_token_dict
    pass
