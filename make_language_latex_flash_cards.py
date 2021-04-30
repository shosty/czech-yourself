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

from Grammar_Components import CzechNoun, CzechAdjective, GermanNoun, GermanAdjective

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


def german_main():
    nouns, adjectives = parse_excel_vocab_sheet(language='German')

    all_cases = ['nominative', 'accusative', 'genitive', 'dative']

    # -----
    # NOUNS
    # -----
    NS = {case: [] for case in all_cases}

    for record in nouns.iterrows():
        x = GermanNoun(**record[1])  # ignore record index
        NS[x.case].append(x)

    # ----------
    # ADJECTIVES
    # ----------
    AS = {case: [] for case in all_cases}

    for record in adjectives.iterrows():
        x = GermanAdjective(**record[1])  # ignore record index
        AS[x.case].append(x)

    i_slide = 0
    rename_slides = []
    
    articality_dict = {'singular': ['def','indef'], 'plural': ['preceded','unpreceded']}

    if True:
        with open('german_flashcards_entries.tex', 'w') as fid:
            for case in ['nominative', 'accusative', 'genitive', 'dative']:
                for N in NS[case]:
                    for A in AS[case]:
                        print(N.card)
                        for articality in articality_dict[N.card]:
                            print(N.latex(card_format='singular',
                                          adjective=A,
                                          adjective_articality=articality).encode('utf-8'))
                            i_slide = i_slide + 1

        os.system('pdflatex cases_flashcards.tex')
        
    return (NS,AS)


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


def parse_excel_vocab_sheet(language='Czech'):
    # nouns = pd.read_excel('/Users/asavol/Dropbox/Public/CZECH/LATEX/Czech_vocabulary.xlsx',sheet_name='Nouns')
    # adjectives = pd.read_excel('/Users/asavol/Dropbox/Public/CZECH/LATEX/Czech_vocabulary.xlsx',sheet_name='Adjectives')

    if language == 'Czech':
        nouns = pd.read_excel('/Users/asavol/Downloads/Czech vocabulary.xlsx', sheet_name='Nouns')
        adjectives = pd.read_excel('/Users/asavol/Downloads/Czech vocabulary.xlsx', sheet_name='Adjectives')
        demonstratives = pd.read_excel('/Users/asavol/Downloads/Czech vocabulary.xlsx', sheet_name='Demonstratives')

        nouns[nouns.isna()] = ''
        adjectives[adjectives.isna()] = ''
        nouns.replace('nan', '', inplace=True)
        adjectives.replace('nan', '', inplace=True)
        vocab = (nouns, adjectives, demonstratives)

    if language == 'German':
        nouns = pd.read_excel('/Users/asavol/Downloads/German vocabulary.xlsx', sheet_name='Nouns')
        adjectives = pd.read_excel('/Users/asavol/Downloads/German vocabulary.xlsx', sheet_name='Adjectives')
        # demonstratives = pd.read_excel('/Users/asavol/Downloads/Czech vocabulary.xlsx', sheet_name='Demonstratives')

        # nouns[nouns.isna()] = ''
        # adjectives[adjectives.isna()] = ''
        # nouns.replace('nan', '', inplace=True)
        # adjectives.replace('nan', '', inplace=True)
        vocab = (nouns, adjectives)

    return vocab


def czech_main():
    # nouns, adjectives, demonstratives = parse_google_sheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAMES)
    nouns, adjectives, demonstratives = parse_excel_vocab_sheet(language='Czech')

    all_cases = ['nominative', 'accusative', 'locative', 'genitive', 'instrumental', 'dative', 'vocative']

    if True:
        # -----
        # NOUNS
        # -----
        NS = {case: [] for case in all_cases}

        for record in nouns.iterrows():
            x = CzechNoun(**record[1])  # ignore record index
            NS[x.case].append(x)

        # ----------
        # ADJECTIVES
        # ----------
        AS = {case: [] for case in all_cases}

        for record in adjectives.iterrows():
            x = CzechAdjective(**record[1])  # ignore record index
            AS[x.case].append(x)

        i_slide = 0
        rename_slides = []

        if True:
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

            os.system('pdflatex cases_flashcards.tex')  # need to dynamically accept different languages

            print(rename_slides)
            if False:
                # os.system('export MAGICK_HOME="/Applications/ImageMagick-7.0.7"')
                # os.system('export DYLD_LIBRARY_PATH="$MAGICK_HOME/lib/"')
                # os.system('export PATH="$MAGICK_HOME/bin:$PATH"')

                # os.system('/Applications/ImageMagick-7.0.7/bin/convert -density 400 cases_flashcards.pdf cases_flashcards.png')
                for cmd in rename_slides:
                    os.system(cmd)

    return NS, AS


if __name__ == '__main__':
    # (N, A) = czech_main()
    (NS, AS) = german_main()
