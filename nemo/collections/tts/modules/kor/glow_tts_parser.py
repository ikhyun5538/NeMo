from typing import List, Optional
from .g2p import convertSentence2Pronounce
from .kr_phoneme_symbols import Ko_ARPAbet

#_phoneme_symbol_to_id = {s: i for i, s in enumerate(phoneme_symbols)}

class CMUDict:
    def __init__(self, file_or_path, valid_symbols, keep_ambiguous=True):
        """
        Thin wrapper around CMUDict data. http://www.speech.cs.cmu.edu/cgi-bin/cmudict
        Args:
            file_or_path: file or path to cmu dictionary
            keep_ambiguous: keep entries with multiple possible pronunciations
        """

        self.valid_symbols = valid_symbols

        self._valid_symbol_set = set(self.valid_symbols)

        if isinstance(file_or_path, str):
            with open(file_or_path, encoding="latin-1") as f:
                entries = self._parse_cmudict(f)
        else:
            entries = self._parse_cmudict(file_or_path)
        if not keep_ambiguous:
            entries = {word: pron for word, pron in entries.items() if len(pron) == 1}
        self._entries = entries

    def __len__(self):
        return len(self._entries)

    def lookup(self, word):
        """Returns list of ARPAbet pronunciations of the given word."""
        return self._entries.get(word.upper())

    def _get_pronunciation(self, s):
        parts = s.strip().split(" ")
        for part in parts:
            if part not in self._valid_symbol_set:
                return None
        return " ".join(parts)

    def _parse_cmudict(self, file):
        _alt_re = re.compile(r"\([0-9]+\)")

        cmudict = {}
        for line in file:
            if len(line) and (line[0] >= "A" and line[0] <= "Z" or line[0] == "'"):
                parts = line.split("  ")
                word = re.sub(_alt_re, "", parts[0])
                pronunciation = self._get_pronunciation(parts[1])
                if pronunciation:
                    if word in cmudict:
                        cmudict[word].append(pronunciation)
                    else:
                        cmudict[word] = [pronunciation]
        return cmudict

class GlowTTSParser:
    def __init__(self, cmu_dict_path=None):
        """
        Parser for the glow tts model.
        Converts all characters to phonemes.
        Args:
            cmu_dict_path (str): Path to cmu dictionary
        """

        self.cmu_dict = None

        if cmu_dict_path:
            self.cmu_dict = CMUDict(cmu_dict_path, Ko_ARPAbet)

        self.valid_symbols = Ko_ARPAbet
        self._valid_symbol_set = set(self.valid_symbols)

        _pad        = '_'
        _eos        = '~'
        _sos        = '^'
        _special = "!'(),-.:;? "
        phoneme_symbols =  [_pad, _eos] + list(_special) + Ko_ARPAbet + [_sos]

        self.symbols = phoneme_symbols
        self._symbol_to_id = {s: i for i, s in enumerate(self.symbols)}
        self._id_to_symbol = {i: s for i, s in enumerate(self.symbols)}

    def __call__(self, text: str) -> Optional[List[int]]:
        return self.text_to_sequence(text, ['basic_cleaners'])


    def text_to_sequence(self, text, cleaner_names, sos_token = True, eos_token = True, dictionary=None):
        sequence = []
        tmp = convertSentence2Pronounce(text)
        tmp = tmp.split(' ')
        #print("text-> Pronounce", tmp)
        #print("\n\n")

        for token in tmp:
            token = ' ' if token == '@' else token
            #sequence.append(_phoneme_symbol_to_id[token])
            sequence.append(self._symbol_to_id[token])

        if sos_token:
            sequence = [self._symbol_to_id['^'], *sequence]
            #sequence.append(_phoneme_symbol_to_id['^']) + sequence
        if eos_token:
            sequence.append(self._symbol_to_id['~'])

        return sequence


if __name__ == '__main__':
    parser = GlowTTSKorParser()
    print(parser.text_to_sequence("이야 동작한다", ['basic_cleaners']))
