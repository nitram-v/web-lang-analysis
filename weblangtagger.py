from estnltk.taggers import Retagger
from estnltk.taggers import RegexTagger
import estnltk.taggers.dict_taggers.vocabulary 
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import ClauseSegmenter
import regex as re
from collections import defaultdict
from estnltk.layer.span_operations import conflict


MACROS={'LOWERCASE': 'a-zšžõäöü','UPPERCASE': 'A-ZŠŽÕÄÖÜ','NUMERIC': '0-9','2,':'{2,}','1,':'{1,}','4,':'{4,}','0,1':'{0,1}','1,2':'{1,2}'}

MACROS['LETTERS'] = MACROS['LOWERCASE'] + MACROS['UPPERCASE']
MACROS['ALPHANUM'] = MACROS['LETTERS'] + MACROS['NUMERIC']

sonad = []
with open('data/zž_sõnad.txt') as f:
    sonad = f.readlines()
    
sonad = [line.rstrip('\n') for line in sonad]

def foreign_z_letters_val(m):
    return not m.group(0).lstrip() in sonad

def punct_reps_val(m):
    if any(char in emoji.UNICODE_EMOJI['en'] for char in m.group(0)):
        return False
    if len([flag for flag in re.finditer(u'[\U0001F1E6-\U0001F1FF]+', m.group(0))]) > 0:
        return False
    return True

def domain_val(m):
    re_pattern = re.compile(r'''(\.ee|\.com|\.ru)($|[^{ALPHANUM}])'''.format(**MACROS),re.X)
    matched = re_pattern.finditer(m.group(0))
    matches = [match.group(0) for match in matched]
    if len(matches) > 0:
        return False
    return True

vocabulary = [
              {'_regex_pattern_': re.compile(r'''([^\n\. {ALPHANUM}])\1{1,}'''.format(**MACROS),re.X),
               '_validator_': punct_reps_val,
               'comment':'punctuation mark more than once (except a dot)',
               'pattern_type':'punct_reps',
               'example':'!!!!!!!!!'},
    
              {'_regex_pattern_': re.compile(r'''([\.]{4,}|[^\.][\.][\.][^\.])'''.format(**MACROS),re.X),
               'comment':'punctuation mark two or more than three times (a dot)',
               'pattern_type':'punct_reps',
               'example':'......'},
    
              {'_regex_pattern_': re.compile(r'''(?:^|\s|\n)[^\s\n{NUMERIC}]*([{LETTERS}])\1{2,}[^\s\?,\.\)\!]*'''.format(**MACROS),re.X),
               'comment':'letter more than twice',
               'pattern_type':'letter_reps',
               'example':'jaaaaa'},
    
              {'_regex_pattern_': re.compile(r'''[{LETTERS}]{2,}[^\s{ALPHANUM}ôÔ\-_/'\*][{LETTERS}]{2,}'''.format(**MACROS), re.X),
               '_validator_': domain_val,
               'comment':'no spaces after punctuation marks',
               'pattern_type':'no_spaces',
               'example':'tere!kuidas läheb?hästi',
               '_group_': 0},
    
              {'_regex_pattern_': re.compile(r'''(\s|^)[{UPPERCASE}]{2,}[^{LOWERCASE}\-]+[{UPPERCASE} ,.!\?]+(\s|[,\.!\?]+)[{UPPERCASE}][^ ]*'''.format(**MACROS),re.X),
               'comment':'some parts of texts written in capital letters',
               'pattern_type':'capital_letters',
               'example':'MISASJA? kas päriselt? MINE METSA!'},
    
              {'_regex_pattern_': re.compile(r'''(?:^|\s)((?=[^{UPPERCASE}\s]*[cqwxy])[^ ]*) '''.format(**MACROS),re.X),
               'comment':'if foreign letters are used',
               'pattern_type':'foreign_letters',
               'example':'ma ei viici yksi'},
    
              {'_regex_pattern_': re.compile(r'''[^{NUMERIC}\.]([\!\?\.]{1,2}|[\!\?\.]{4,})\s*[{LOWERCASE}]+\s'''.format(**MACROS),re.X),
               '_validator_': domain_val,
               'comment':'capital letters ignored (except after a dot)',
               'pattern_type':'ignored_capital',
               'example':'tule siia! ma ei viitsi.'},
    
              {'_regex_pattern_': re.compile(r'''[{ALPHANUM}]+\s([^{ALPHANUM}\n \.\…\&§\-\–\‒\—\+\=•]|\.)\s[{ALPHANUM}]+'''.format(**MACROS),re.X),
               'comment':'spaces around punctuation marks',
               'pattern_type':'incorrect_spaces',
               'example':'See on tore ! Mulle meeldib.'},
    
              {'_regex_pattern_': re.compile(r'''(?:^|\s)((?=[^{UPPERCASE}\s]*[z])[^ ]*) '''.format(**MACROS),re.X),
               '_validator_': foreign_z_letters_val,
               'comment':'if foreign z is used',
               'pattern_type':'foreign_z_letters',
               'example':'plz aita mind kodutööga'},
             ]



class WebLangTagger(Tagger):
    """Retagger for detecting web language features in text. Web language features will be marked as attributes of the paragraphs layer."""
    
    conf_param = ['use_unknown_words','use_emoticons','use_letter_reps','use_punct_reps','use_capital_letters',
                  'use_missing_commas','use_ignored_capital','use_no_spaces','use_incorrect_spaces','use_foreign_letters',
                  'regex_tagger', 'use_emojis', 'use_foreign_z_letters', 'clauses_layer']
    
    def __init__(self,
                 output_layer='weblang_tokens',
                 words_layer='words', 
                 clauses_layer=None, 
                 compound_tokens_layer='compound_tokens',
                 use_unknown_words=True,
                 use_emoticons=True,
                 use_letter_reps=True,
                 use_punct_reps=False, 
                 use_capital_letters=True,
                 use_missing_commas=True,
                 use_ignored_capital=True,
                 use_no_spaces=True,
                 use_incorrect_spaces=True,
                 use_foreign_letters=True,
                 use_foreign_z_letters=True,
                 use_emojis=True):
        
        self.clauses_layer = clauses_layer
        
        #output_attributes=('word_count',)
        #output_attributes=()
        
        self.use_unknown_words = use_unknown_words
        self.use_emoticons = use_emoticons
        self.use_letter_reps = use_letter_reps
        self.use_punct_reps = use_punct_reps
        self.use_capital_letters = use_capital_letters
        self.use_missing_commas = use_missing_commas
        self.use_ignored_capital = use_ignored_capital
        self.use_no_spaces = use_no_spaces
        self.use_incorrect_spaces = use_incorrect_spaces
        self.use_foreign_letters = use_foreign_letters
        self.use_foreign_z_letters = use_foreign_z_letters
        self.use_emojis = use_emojis
        
        self.input_layers = [words_layer, compound_tokens_layer] #clauses_layer
        self.output_layer = output_layer #paragraphs_layer
        
        self.output_attributes = ['type']
        
        filtered_vocabulary=[i for i in vocabulary if (
                (i["pattern_type"]=="punct_reps" and use_punct_reps is True) or 
                (i["pattern_type"]=="letter_reps" and use_letter_reps is True) or
                (i["pattern_type"]=="no_spaces" and use_no_spaces is True) or
                (i["pattern_type"]=="capital_letters" and use_capital_letters is True) or
                (i["pattern_type"]=="foreign_letters" and use_foreign_letters is True) or
                (i["pattern_type"]=="ignored_capital" and use_ignored_capital is True) or
                (i["pattern_type"]=="incorrect_spaces" and use_incorrect_spaces is True) or
                (i["pattern_type"]=="foreign_z_letters" and use_foreign_z_letters is True))]
        
        # only attribute flags that are True are added to output_attributes
        #if use_emoticons is True:
        #    output_attributes=output_attributes + ("emoticons",)
        #if use_missing_commas is True:
        #    output_attributes=output_attributes + ("missing_commas",)
        #if use_unknown_words is True:
        #    output_attributes=output_attributes + ("unknown_words",)
        #if use_emojis is True:
        #    output_attributes=output_attributes + ("emojis",)
            
        #if len(filtered_vocabulary) != 0: # attributes from vocabulary for regextagger
        #    for i in filtered_vocabulary:
        #        if not i["pattern_type"] in output_attributes:
        #            output_attributes=output_attributes + (i["pattern_type"],)
        #else:
        #    output_attributes          
        #self.output_attributes=output_attributes
        
        self.regex_tagger = RegexTagger(vocabulary=filtered_vocabulary,
                                        output_layer='web_language',output_attributes=['pattern_type'],
                                        conflict_resolving_strategy='ALL')
        
        # only used when these attribute flags are True
        if use_missing_commas is True:
            self.input_layers.append(clauses_layer)
            self.conf_param.append('clause_segmenter')
            self.clause_segmenter = ClauseSegmenter(ignore_missing_commas=True, output_layer='ignore_missing_commas_clauses')
        else:
            pass
            
        if use_unknown_words is True:
            self.conf_param.append('vabamorf_tagger')
            self.vabamorf_tagger = VabamorfTagger(guess=False,propername=False,disambiguate=False,phonetic=False,output_layer='morph_unknown_words')
        else:
            pass
        
    #def _make_layer_template(self):
    #    return Layer(name=self.output_layer, text_object=None)
            
    def _make_layer(self, text, layers, status): # status=None
        # Create new layer based on the configuration
        layer = Layer(name=self.output_layer, attributes=self.output_attributes, text_object=text, ambiguous=True) #attributes=self.output_attributes
        
        #layer = self._make_layer_template()
        #layer.text_object = text
        
        words=layers['words']
        compound_tokens=layers['compound_tokens']
        
        layer.meta['punct_reps'] = 0
        layer.meta['letter_reps'] = 0
        layer.meta['no_spaces'] = 0
        layer.meta['capital_letters'] = 0
        layer.meta['foreign_letters'] = 0
        layer.meta['foreign_z_letters'] = 0
        layer.meta['ignored_capital'] = 0
        layer.meta['incorrect_spaces'] = 0
        layer.meta['emoticons'] = 0
        layer.meta['missing_commas'] = 0
        layer.meta['unknown_words'] = 0
        layer.meta['emojis'] = 0
        layer.meta['word_count'] = 0
        
        web_language_layer = self.regex_tagger.make_layer(text=text,layers=layers)
        
        # only needed when these attribute flags are True
        if self.use_missing_commas == True:
            clauses=layers['clauses']
            ignore_missing_commas_clauses = self.clause_segmenter.make_layer(text=text,layers=layers)
        if self.use_unknown_words == True:
            morph_unknown_words = self.vabamorf_tagger.make_layer(text=text,status=status)
        
        text_score=0 # a total number of all the attributes in a text
        text_word_count=0 # a total number of words in a whole text
        
        # checks if certain words belong to the same paragraph
        def if_in_paragraph(paragraph_i, new_i): 
            #if (paragraph_i.start == new_i.start or paragraph_i.start < new_i.start) and (paragraph_i.end == new_i.end or paragraph_i.end > new_i.end):
            return True
            
        # checks for clauses that shouldn't be counted as attributes 
        # clauses that end eg with a word "ainult" if the following clause starts eg with "et"
        def counter_comma(counter, word, new_list, clause, start_index):
            if counter!=0:
                if clause.text[0].lower() in [word]:
                    new_list.append(start_index)
                    return new_list
        
        # checks if a word consists of letters/numbers
        def validateString(s):
            flag = False
            for i in s:
                if i.isalpha() or i.isdigit():
                    flag = True
            return flag
        
        # finds emojis from a string
        # https://stackoverflow.com/questions/43146528/how-to-extract-all-the-emojis-from-text
        def find_emojis(text):

            emoji_list = []
            data = re.findall(r'\X', text)
            for word in data:
                if any(char in emoji.UNICODE_EMOJI['en'] for char in word):
                    emoji_list.append(word)
    
            # Emojid on tekstist leitud, aga oleks vaja ka leida emojide asukohad tekstis:
            # regexi abil saab leida igale emojile asukohad tekstis
            emoji_pos = []
            for word in set(emoji_list):
                emoji_pos.extend([emoji for emoji in re.finditer(word, text)])
                
            flags = [flag for flag in re.finditer(u'[\U0001F1E6-\U0001F1FF]+', text)]

            return emoji_pos + flags
        
        # tsükli asemel otse säutsu Text objekt
        text_str = text.text
        word_list=[] # a total number of words in text
        attr_dict=defaultdict(int) # attributes counted separately in a text
            
        for i in self.output_attributes: # by default attribute count is set to 0
            if i != "emoticons" or i != "missing_commas" or i != "unknown_words" or i != "emojis":
                attr_dict[i]=0
                
        for i in web_language_layer:
            if if_in_paragraph(text_str, i) == True:
                check=0
                attr=i.pattern_type
                for cp in compound_tokens:
                    # such compound tokens are not counted
                    # muuta ilusamaks
                    #print(cp.type)
                    if "www_address" in cp.type or "email" in cp.type or "non_ending_abbreviation" in cp.type or "username_mention" in cp.type or "hashtag" in cp.type or "emoticon" in cp.type:
                        for item in cp:
                            #print("conflict", item)
                            if conflict(i,item):
                                check+=1
                if check==0:
                    #attr_dict[attr] += 1
                    layer.meta[attr] += 1
                    # kuidas lisada kihile märgendus?
                    layer.add_annotation( (i.start, i.end), **{'type':attr})
                        
        if self.use_emoticons == True: # attribute "emoticons"
            attr_dict["emoticons"]=0
            for cp in compound_tokens:
                #print(type(cp))
                #print(cp.start)
                if "emoticon" in cp.type:
                    if if_in_paragraph(text_str, cp) == True:
                        #attr_dict["emoticons"] += 1
                        layer.meta["emoticons"] += 1
                        layer.add_annotation( (cp.start, cp.end), **{'type':"emoticons"})
                            
        if self.use_emojis == True: # attribute "emojis"
            attr_dict["emojis"]=0
            emojis = find_emojis(text_str)
            #attr_dict["emojis"] += len(emojis)
            layer.meta["emojis"] += len(emojis)
            [layer.add_annotation( (emoji.start(), emoji.end()), **{'type':"emoji"}) for emoji in emojis]
                    
        ## TODO: lisada kihti
        # finds clauses with a missing comma
        if self.use_missing_commas == True:
            attr_dict["missing_commas"]=0
            not_suitable=[]
            for w in words:
                if if_in_paragraph(text_str, w) == True:
                    counter=0
                    counter2=0
                    for cl in ignore_missing_commas_clauses:
                        if cl.end==w.start-1:
                            if cl.text[-1].lower() in ["ainult","vaevalt","peaasi","mitte","ilma","olgugi","nii","sellepärast","selleks","et","sest","aga","kuid","vaid","siis","ja","ning","ega","ehk","või","palun"]:
                                not_suitable.append(w.start)
                                counter+=1
                            if cl.text[-1].lower() in ["juhul","enne","isegi","siis"]:
                                counter2+=1
                                
                        if cl.start==w.start:
                            counter_comma(counter,"et",not_suitable,cl,w.start)
                            counter_comma(counter2,"kui",not_suitable,cl,w.start)
                            
                    if w.start not in [c.start for c in clauses if c]: # indexes of the beginnings of clauses
                        if w.start in [c.start for c in ignore_missing_commas_clauses if c]: # indexes of the beginnings of clauses (also detects clauses that have a missing comma)
                            for cl in ignore_missing_commas_clauses:
                                if w.start==cl.start: # if the start index of a clause is only in ignore_missing_commas_clauses, it means there is a missing comma
                                    if w.start not in not_suitable: # 
                                        if w.text != "palun":
                                            attr_dict["missing_commas"] += 1
                    

        # the number of words in a paragraph  
        for w in words:
            if if_in_paragraph(text_str, w) == True:
                word_list.append(w)
            
        ## TODO: lisada kihti
        # finds unknown words in a paragraph
        if self.use_unknown_words == True:
            attr_dict["unknown_words"]=0
            for morph in morph_unknown_words:
                if if_in_paragraph(text_str, morph) == True:
                    if morph[0].lemma==None:
                        if validateString(morph[0].text)==True:
                            match2=re.match("^[A-ZÜÕÄÖŠŽ]{1,}",morph[0].text)
                            count=0
                            for t,t2 in zip(compound_tokens.normalized, compound_tokens.type):
                                if morph[0].text!=t and "emoticon" not in t2 and "name_with_initial" not in t2 and not match2:
                                    count+=1 # such compound tokens are not counted as unknown words             
                            if count !=0:
                                attr_dict["unknown_words"] += 1
                            if morph[0].start not in text.compound_tokens["start"] and not match2:
                                attr_dict["unknown_words"] += 1
                                        
        layer.meta["word_count"] =len(word_list)
        
        return layer
