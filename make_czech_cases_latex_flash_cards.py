# -*- coding: utf-8 -*-

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import pandas as pd
import csv

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
# SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_SPREADSHEET_ID = '13gCnAtKyXzXxTLMCz3erHv71ugwDCdLRIKAydnLkY0A'
# SAMPLE_RANGE_NAME = 'Class Data!A2:E'
SAMPLE_RANGE_NAMES = ['Nouns!A1:K', 'Adjectives!A1:N', 'Possessives!A1:R', 'Demonstratives!A1:E']

verbs = {'nominative': {'verb': 'je tady', 'verb_1': 'je tady', 'verb_2': 'jsou tady', 'verb_3': 'jsou tady'},
         'accusative': {'verb': u'Vidím', 'verb_1': u'Vidím', 'verb_2': '', 'verb_3': ''},
         'locative': {'verb': u'Mluvím o', 'verb_1': u'Mluvím o', 'verb_2': '', 'verb_3': ''},
         'genitive': {'verb': u'Fotky', 'verb_1': u'Fotky', 'verb_2': '', 'verb_3': ''},
         'instrumental': {'verb': u'Jsem před', 'verb_1': u'Jsem před', 'verb_2': '', 'verb_3': ''},
         'dative': {'verb': u'Jsem rád, diky', 'verb_1': u'Jsem rád, diky', 'verb_2': '', 'verb_3': ''},
         'vocative': {'verb': u'Ahoj', 'verb_1': u'Ahoj', 'verb_2': '', 'verb_3': ''}}

verbs_translation = {'nominative': 'It is the',
                     'accusative': 'I see the',
                     'locative': 'I am talking about the',
                     'genitive': 'Photos of the',
                     'instrumental': 'I am in front of the',
                     'dative': 'I am pleased thanks to the',
                     'vocative': 'Hello'}


class Word():
    def __init__(self, translation='', case=''):
        assert ' ' not in translation, 'No spaces allowed'
        self.translation = translation
        self.case = case


class Noun(Word):
    def __init__(self, translation, case, card, gender, noun_class):
        Word.__init__(self, translation, case)
        self.card = card
        self.gender = gender
        self.noun_class = noun_class

    def get_translation(self, card='singular'):
        s = self.translation
        if card == 'plural':
            if s[-1] == 'y':
                t = s[:-1] + 'ies'
            elif s[-3:] == 'man':
                t = s[:-3] + 'men'
            else:
                t = s + 's'
        else:
            t = s
        return t


class CzechNoun(Noun):
    def __init__(self, translation='', case='', card='s', gender='', noun_class='', singular_stem_class='',
                 singular_stem='', singular_declension='', plural_stem_class='', plural_stem='', plural_declension='', **kwargs):
        Noun.__init__(self, translation, case, card, gender, noun_class)

        self.singular_stem_class = singular_stem_class
        self.singular_stem = singular_stem[:-1] if singular_stem_class == 'soft' else singular_stem
        self.singular_stem_soft_ending = '' if singular_stem_class != 'soft' else singular_stem[-1]
        self.singular_declension = singular_declension

        self.plural_stem_class = plural_stem_class if plural_stem_class != '' else singular_stem_class
        if plural_stem != '':
            self.plural_stem = plural_stem[:-1] if self.plural_stem_class == 'soft' else plural_stem
            self.plural_stem_soft_ending = '' if self.plural_stem_class != 'soft' else plural_stem[-1]
        else:
            self.plural_stem = self.singular_stem
            self.plural_stem_soft_ending = self.singular_stem_soft_ending

        self.plural_declension = plural_declension

    # def label():
        # return '%s%s' % (self.singular_stem, self.singular_declension)

    def latex(self, card_format='plural', adjective=None, descriptor=None):

        if adjective is not None:
            assert adjective.case == self.case, 'Verb/Noun case mis-match'

        latex_macro = {'singular': '\czechcard', 'plural': '\czechcardplural'}

        if card_format == 'singular':
            verb = verbs[self.case]['verb']
            adjective = adjective.latex(self.gender, 'singular') if adjective is not None else ''
            descriptor = descriptor.latex(self.case, self.gender, card_format, 'my') if descriptor is not None else ''

            if self.case == 'nominative':
                latex_string = '\czechcard{%(case)s}{' % self.__dict__ + descriptor + adjective + ' %(singular_stem)s\soft{%(singular_stem_soft_ending)s}\%(gender)s{%(singular_declension)s} je tady}' % self.__dict__
            else:
                latex_string = '\czechcard{%(case)s}{' % self.__dict__ + verb + descriptor + adjective + ' %(singular_stem)s\soft{%(singular_stem_soft_ending)s}\%(gender)s{%(singular_declension)s}}' % self.__dict__

        if card_format == 'plural':
            verb = verbs[self.case]['verb_1']
            adjective_plural = adjective.latex(self.gender, card_format) if adjective is not None else ''
            descriptor_plural = descriptor.latex(self.case, self.gender, card_format,
                                                 'my') if descriptor is not None else ''

            if self.case == 'nominative':
                latex_string = '\czechcard{%(case)s}{' % self.__dict__ + descriptor_plural + adjective_plural + ' \pl{%(plural_stem)s\soft{%(plural_stem_soft_ending)s}}\%(gender)s{%(plural_declension)s} jsou tady}' % self.__dict__
            else:
                latex_string = '\czechcard{%(case)s}{' % self.__dict__ + verb + descriptor_plural + adjective_plural + ' \pl{%(plural_stem)s\soft{%(plural_stem_soft_ending)s}}\%(gender)s{%(plural_declension)s}}' % self.__dict__

        return (latex_string)

    def __repr__(self):
        return (self.singular_stem.encode('utf-8'))


class Adjective(Word):
    def __init__(self, translation='', case='', adjective_class='', stem='', MA_singular='', MI_singular='',
                 F_singular='', N_singular='', MA_plural_stem='', MA_plural='', MI_plural='', F_plural='', N_plural='',
                 **kwargs):
        Word.__init__(self, translation, case=case)
        self.adjective_class = adjective_class
        self.stem = stem
        self.MAs = MA_singular
        self.MIs = MI_singular
        self.Fs = F_singular
        self.Ns = N_singular
        self.MA_plural_stem = MA_plural_stem if MA_plural_stem != '' else self.stem
        self.MAp = MA_plural
        self.MIp = MI_plural
        self.Fp = F_plural
        self.Np = N_plural

    def latex(self, gender='MA', card='plural'):
        stem = self.MA_plural_stem if gender == 'MA' and card == 'plural' else self.stem
        declension = getattr(self, gender + card[0])
        if card == 'plural':
            lstring = ' \pl{%s}\%s{%s} ' % (stem, gender, declension)
        else:
            lstring = ' %s\%s{%s} ' % (stem, gender, declension)
        return (lstring)


class Descriptor(dict):
    def __init__(self, name='Possessives'):
        self.name = name

    def parse_descriptor_record(self, r):
        case = r.pop('case')
        gender = r.pop('gender')
        for k in r.keys():
            cardinality = k.split('_')[-1]
            descriptor = '_'.join(k.split('_')[:-1])
            self[(case, gender, cardinality, descriptor)] = r[k]

    def latex(self, case, gender, cardinality, descriptor):
        if case == 'vocative':
            return ('')
        if gender in ['MA', 'MI'] and case not in ['accusative', 'nominative']:
            ternary_gender = 'M'
        else:
            ternary_gender = gender
        return (' \%s{%s} ' % (gender, self[(case, ternary_gender, cardinality, descriptor)]))


def parse_google_sheet(SAMPLE_SPREADHSEET_ID, SAMPLE_RANGE_NAMES):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    # NOUNS
    # -----
    result_nouns = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                      range=SAMPLE_RANGE_NAMES[0]).execute()
    values_nouns = result_nouns.get('values', [])

    # ADJECTIVES
    # ----------
    result_adjectives = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                           range=SAMPLE_RANGE_NAMES[1]).execute()
    values_adjectives = result_adjectives.get('values', [])

    # DEMONSTRATIVES
    # --------------
    result_demonstratives = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                               range=SAMPLE_RANGE_NAMES[3]).execute()
    values_demonstratives = result_demonstratives.get('values', [])

    return (values_nouns, values_adjectives, values_demonstratives)

# def parse_excel_vocab_sheet():
# nouns = pd.read_excel('/Users/asavol/Dropbox/Public/CZECH/LATEX/Czech_vocabulary.xlsx',sheet_name='Nouns')
# adjectives = pd.read_excel('/Users/asavol/Dropbox/Public/CZECH/LATEX/Czech_vocabulary.xlsx',sheet_name='Adjectives')

# nouns[nouns.isna()] = ''
# adjectives[adjectives.isna()] = ''
# nouns.replace('nan','',inplace=True)
# adjectives.replace('nan','',inplace=True)

# return(nouns,adjectives)

def czech_main():
    nouns, adjectives, demonstratives = parse_google_sheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAMES)

    all_cases  = ['nominative', 'accusative', 'locative', 'genitive', 'instrumental', 'dative', 'vocative']

    if True:
        # -----
        # NOUNS
        # -----
        NS = {case: [] for case in all_cases}
        
        declension_components = nouns.pop(0)
        for record in nouns:
            record_dict = dict(zip(declension_components, record))
            record_dict.pop('final_column')

            x = CzechNoun(**record_dict)
            NS[x.case].append(x)

        # ----------
        # ADJECTIVES
        # ----------
        AS = {case: [] for case in all_cases}

        declension_components = adjectives.pop(0)
        for record in adjectives:
            record_dict = dict(zip(declension_components, record))
            record_dict.pop('final_column')

            x = Adjective(**record_dict)
            AS[x.case].append(x)

        i_slide = 0
        rename_slides = []

        if False:
            with open('czech_flashcards_entries.tex', 'w') as fid:
                for case in ['nominative', 'accusative', 'locative', 'genitive', 'instrumental', 'dative', 'vocative']:
                    # for case in ['genitive']:
                    for N in NS[case]:
                        for A in [x for x in AS[case] if x.adjective_class == 'hard']:
                            # fid.write(N.latex(card_format='plural',adjective=A).encode('utf-8'))
                            for cardinality in ['singular', 'plural']:
                                if case == 'nominative':
                                    if cardinality == 'singular':
                                        english_string = 'The %s %s is here' % (A.translation, N.translation)
                                    else:
                                        english_string = 'The %s %s are here' % (
                                            A.translation, N.get_translation(cardinality))
                                else:
                                    english_string = '%s %s %s' % (
                                        verbs_translation[case], A.translation, N.get_translation(cardinality))
                                rename_slides.append(
                                    'mv cases_flashcards-%d.png %s.png ' % (
                                        i_slide, '_'.join(english_string.split(' '))))
                                # fid.write(N.latex(card_format='singular',adjective=A,descriptor=P).encode('utf-8'))
                                # fid.write(N.latex(card_format='singular',adjective=A).encode('utf-8'))
                                fid.write(N.latex(card_format=cardinality, adjective=A).encode('utf-8'))
                                fid.write('\n')
                                i_slide = i_slide + 1

            os.system('pdflatex cases_flashcards.tex')

            print(rename_slides)
            if False:
                # os.system('export MAGICK_HOME="/Applications/ImageMagick-7.0.7"')
                # os.system('export DYLD_LIBRARY_PATH="$MAGICK_HOME/lib/"')
                # os.system('export PATH="$MAGICK_HOME/bin:$PATH"')

                # os.system('/Applications/ImageMagick-7.0.7/bin/convert -density 400 cases_flashcards.pdf cases_flashcards.png')
                for cmd in rename_slides:
                    os.system(cmd)

    return (NS, AS)


if __name__ == '__main__':
    (N, A) = czech_main()
