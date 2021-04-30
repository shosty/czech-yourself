
class Word():
    def __init__(self, translation='', case='', language=''):
        assert ' ' not in translation, 'No spaces allowed'
        self.translation = translation
        self.case = case
        self.language = language


class Noun(Word):
    def __init__(self, translation, case, card, gender, noun_class, language):
        Word.__init__(self, translation, case, language)
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
                 singular_stem='', singular_declension='', plural_stem_class='', plural_stem='', plural_declension='',
                 **kwargs):
        Noun.__init__(self, translation, case, card, gender, noun_class, 'czech')

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

    def latex(self, card_format='plural', adjective=None, descriptor=None):

        if adjective is not None:
            assert adjective.case == self.case, 'Verb/Noun case mis-match'

        latex_macro = {'singular': '\card', 'plural': '\cardplural'}

        if card_format == 'singular':
            verb = verbs[self.case]['verb']
            adjective = adjective.latex(self.gender, 'singular') if adjective is not None else ''
            descriptor = descriptor.latex(self.case, self.gender, card_format, 'my') if descriptor is not None else ''

            if self.case == 'nominative':
                latex_string = '\card{%(case)s}{' % self.__dict__ + descriptor + adjective + ' %(singular_stem)s\soft{%(singular_stem_soft_ending)s}\%(gender)s{%(singular_declension)s} je tady}' % self.__dict__
            else:
                latex_string = '\card{%(case)s}{' % self.__dict__ + verb + descriptor + adjective + ' %(singular_stem)s\soft{%(singular_stem_soft_ending)s}\%(gender)s{%(singular_declension)s}}' % self.__dict__

        if card_format == 'plural':
            verb = verbs[self.case]['verb_1']
            adjective_plural = adjective.latex(self.gender, card_format) if adjective is not None else ''
            descriptor_plural = descriptor.latex(self.case, self.gender, card_format,
                                                 'my') if descriptor is not None else ''

            if self.case == 'nominative':
                latex_string = '\card{%(case)s}{' % self.__dict__ + descriptor_plural + adjective_plural + ' \pl{%(plural_stem)s\soft{%(plural_stem_soft_ending)s}}\%(gender)s{%(plural_declension)s} jsou tady}' % self.__dict__
            else:
                latex_string = '\card{%(case)s}{' % self.__dict__ + verb + descriptor_plural + adjective_plural + ' \pl{%(plural_stem)s\soft{%(plural_stem_soft_ending)s}}\%(gender)s{%(plural_declension)s}}' % self.__dict__

        return ('%s{%s}' % (latex_string, self.language))

    def __repr__(self):
        return (self.singular_stem.encode('utf-8'))



class CzechAdjective(Word):
    def __init__(self, singular_translation='', case='', adjective_class='', stem='', MA_singular='', MI_singular='',
                 F_singular='', N_singular='', MA_plural_stem='', MA_plural='', MI_plural='', F_plural='', N_plural='',
                 **kwargs):
        Word.__init__(self, singular_translation, case, 'czech')
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
    
    
class GermanNoun(Noun):
    def __init__(self, translation='', card='', case='', gender='', stem='', declension='', **kwargs):
        Noun.__init__(self, translation, case, card, gender, 'normal', 'german')

        self.stem = stem
        self.declension = declension

    def latex(self, adjective_articality, card_format='singular', adjective=None, descriptor=None, ):
        if adjective is not None:
            assert adjective.case == self.case, 'Verb/Noun case mis-match'

        if card_format == 'singular':
            # verb = verbs[self.case]['verb']
            verb = 'verb'
            adjective = adjective.latex(self.gender, adjective_articality, cardinality=self.card) if adjective is not None else ''
            descriptor = descriptor.latex(self.case, self.gender, card_format, 'my') if descriptor is not None else ''

            latex_string = '\card{%(case)s}{' % self.__dict__ + verb + \
                           descriptor + adjective + ' %(singular_stem)s\%(gender)s{%(singular_declension)s}}' % self.__dict__

        return latex_string


class GermanAdjective(Word):
    def __init__(self, case='', stem='', M_def='', M_indef='', F_def='', F_indef='', N_def='', N_indef='',
                 P_preceded='', P_unpreceded='', singular_translation='', **kwargs):
        Word.__init__(self, singular_translation, case, 'german')

        self.stem = stem
        self.M_def = M_def
        self.M_indef = M_indef
        self.F_def = F_def
        self.F_indef = F_indef
        self.N_def = N_def
        self.N_indef = N_indef
        self.P_preceded = P_preceded
        self.P_unpreceded = P_unpreceded

    def latex(self, gender, articality, cardinality='singular'):
        isSingular = cardinality == 'singular'
        declension = getattr(self, '%s_%s' % (gender, articality)) if isSingular \
            else getattr(self, 'P_%s' % articality)
        if isSingular:
            lstring = ' %s\%s{%s} ' % (self.stem, gender, declension)
        else:
            lstring = ' \pl{%s}\%s{%s} ' % (self.stem, gender, declension)
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
