#TODO - handle one card making multiple diff tokens - DONE
#TODO - handle tokens with more than one word names - DONE
#TODO - handle 'X' after 'create' - DONE
#TODO - default to the first listed set, but have an optional override - DONE
#TODO - split up tokens_xml into individual tokens like split_cards - DONE
#TODO - Reduce split tokens_xml to only those with matching set code - DONE
#TODO - Write new reverse-related field - DONE
#TODO - Output new tokens xml file - DONE
#TODO - Find out why nameless reverse-related field made for dinosaur

import re

presets = {
    'set': 'XLN'
}


def read_xml(name):
    with open(name, 'r') as f:
        output = f.read()
    return output

def write_xml(xml_file, name):
    with open(name, 'w') as f:
        f.writelines(xml_file)

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
    m = re.findall('(?<=<set>).*?(?=</set>)', xml_file, re.DOTALL)[0]
    n = re.findall('(?<=<name>).*?(?=</name>)', m, re.DOTALL)[0]
    print('SET: ', n)
    return n

def split_tokens(xml_file):
    m = re.findall('(?<=<card>).*?(?=</card>)', xml_file, re.DOTALL)
    return m

def reduce_tokens(token_list, setCode):
    output_list = []
    for token in token_list:
        this_token_set_slab = re.findall('<set.*?</set>', token)[0]
        this_token_set = re.findall('(?<=>)[A-Za-z0-9]*?(?=<)', this_token_set_slab)[0].upper() #upper is extra redundancy
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
                print modified_token
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
    print 'TOKENS SET: '
    for token in tokens_set:
        print token
    inverted_dict = {}
    for unique_token in tokens_set:
        ass_card_names = []
        for card_name, token_names in card_token_dict.iteritems():
            for token_name in token_names:
                if token_name == unique_token:
                    ass_card_names.append(card_name)
        inverted_dict[unique_token] = ass_card_names
    return inverted_dict

def write_new_xml(token_list, file_name):
    file_text = '<?xml version="1.0" encoding="UTF-8"?>\n<cockatrice_carddatabase version="3">\n\t<cards>\n'
    for token in token_list:
        file_text = file_text + token
    file_text = file_text + '\t</cards>\n</cockatrice_carddatabase>'
    with open(file_name, 'w') as f:
        f.write(file_text)

if __name__ == '__main__':
    cards_xml = read_xml('xln.xml')
    tokens_xml = read_xml('tokens.xml')
    if presets['set'] != '':
        setCode = extract_set(cards_xml)
    else: setCode = presets['set']
    card_list = split_cards(cards_xml)
    card_token_dict = parse_cards(card_list)
    inverted_token_card_dict = invert_dict(card_token_dict) #needed so that multiple cards can produce the same token
    token_list = split_tokens(tokens_xml)
    reduced_token_list = reduce_tokens(token_list, setCode)
    mashed_list = mash_tokens(reduced_token_list, inverted_token_card_dict)
    write_new_xml(mashed_list, setCode + '_tokens.xml')
    print card_token_dict

#    m = re.findall('create.*?[A-Z][a-z]*? ', cards_xml, re.DOTALL)
#    print(m)
#    for i in m:
#        print 'NEXT CARD:'
#        print(i)
#    print(len(m))
    pass