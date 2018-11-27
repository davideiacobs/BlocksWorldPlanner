import nltk
from pyswip import Prolog
import speech_recognition as sr


class NLP:

    def __init__(self):
        self._chunkGram = r"""
                              object: {<JJ>?<NN><NNP>?|<NNP>}
                              verb_at_beginning: {^<VB.?><.+>+}
                              knowledge: {<object><VB.?>|<EX><VB.?><DT>?<object>}
                              knowledge_phrase: {<knowledge><IN><DT>?<object>|<knowledge><JJ>|<knowledge><DT>?<object>}
                             """
        self._chunkParser = nltk.RegexpParser(self._chunkGram)
        self._chunked = None  # Chunked sentence currently processing

    def process(self, sentence, debug=False):
        token = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(token)
        self._chunked = self._chunkParser.parse(tagged)
        if debug:
            self._chunked.draw()

    def isQuestion(self):
        for subtree in self._chunked.subtrees(filter=lambda t: t.label() == 'verb_at_beginning' and t.leaves()[-1][0] == '?'):
            return True
        return False

    def isKnowledge(self):
        for subtree in self._chunked.subtrees(filter=lambda t: t.label() == 'knowledge'):
            return True
        return False

    def isAction(self):
        for subtree in self._chunked.subtrees(filter=lambda t: t.label() == 'verb_at_beginning' and t.leaves()[-1][0] != '?'):
            return True
        return False

    def getObjects(self):
        object = []
        for subtree in self._chunked.subtrees(filter=lambda t: t.label() == 'object'):
            obj = []
            for leaf in subtree.leaves():
                obj.append(leaf)
            object.append(obj)
        return object

    def add_knowledge_obj(self, obj):
        verb = None
        name = None
        adj = None
        for token in obj:
            if token[1] == "NN":
                verb = token[0].lower()
            elif token[1] == "NNP":
                name = token[0].lower()
            elif token[1] == "JJ":
                adj = token[0].lower()
        if verb and name:
            prolog.assertz(verb+"("+name+")")
        if adj and name:
            prolog.assertz(adj+"("+name+")")

    def add_knowledge_phrase(self):
        obj1 = None
        prep = None
        obj2 = None
        adj = None
        for subtree in self._chunked.subtrees(filter=lambda t: t.label() == 'knowledge_phrase'):
            for knowledge in subtree.subtrees(filter=lambda t1: t1.label() == 'knowledge'):
                for obj in knowledge.subtrees(filter=lambda t2: t2.label() == 'object'):
                    for leaf in obj.leaves():
                        if leaf[1] == "NNP":
                            if obj1 is None:
                                obj1 = leaf[0].lower()
                            else:
                                obj2 = leaf[0].lower()
                        elif leaf[1] == "NN":
                            obj2 = leaf[0].lower()
            for objs in subtree.subtrees(filter=lambda t3: t3.label() == 'object'):
                for leaf in objs.leaves():
                    if leaf[1] == "NNP":
                        if leaf[0] is not obj1:
                            obj2 = leaf[0].lower()
                    elif leaf[1] == "NN":
                        if leaf[0] is not obj1:
                            obj2 = leaf[0].lower()
            for rest in subtree.subtrees(filter=lambda t4: t4.label() != 'knowledge' and t4.label() != 'object'):
                for leaf in rest.leaves():
                    if leaf[1] == 'IN':
                        prep = leaf[0].lower()
                    if leaf[1] == 'JJ':
                        adj = leaf[0].lower()
        if prep and obj1 and obj2:
            prolog.assertz(prep+"("+obj1+","+obj2+")")
        elif obj1 and adj:
            prolog.assertz(adj+"("+obj1+")")

    def make_query(self):
        obj1 = None
        prep = None
        obj2 = None
        adj = None
        for subtree in self._chunked.subtrees(filter=lambda t: t.label() == 'verb_at_beginning'):
            for obj in subtree.subtrees(filter=lambda t2: t2.label() == 'object'):
                res = self.query_obj(obj)
                if res:
                    for token in obj:
                        if token[1] == 'NNP' or (token[1] == 'NN' and (token[0] == 'table' or (token[0] == 'block' and obj1 is not None))):
                            if obj1:
                                obj2 = token[0].lower()
                            else:
                                obj1 = token[0].lower()
                        elif token[1] == 'JJ':
                            adj = token[0].lower()
                else:
                    return False
            if obj2 != 'block' and adj:
                adj = None
            for p in subtree.subtrees(filter=lambda t3: t3.label() != 'object'):
                for token in p:
                    if len(token) > 1:
                        if token[1] == 'IN':
                            prep = token[0].lower()
                        elif token[1] == 'JJ':
                            adj = token[0].lower()
            if obj1 and obj2 and prep:
                try:
                    return bool(list(prolog.query(prep+"("+obj1+","+obj2+")")))
                except Exception:
                    return False
            elif obj1 and adj:
                try:
                    return bool(list(prolog.query(adj + "(" + obj1 + ")")))
                except Exception:
                    return False
            elif obj1 and obj2:
                if obj2 == 'block':
                    try:
                        return bool(list(prolog.query(obj2 + "(" + obj1 + ")")))
                    except Exception as e:
                        return False

    def query_obj(self, obj):
        adj = None
        verb = None
        name = None
        for token in obj:
            if token[1] == 'JJ':
                adj = token[0].lower()
            elif token[1] == 'NNP':
                name = token[0].lower()
            elif token[1] == 'NN':
                verb = token[0].lower()
        if adj and name:
            try:
                return bool(list(prolog.query(adj+"("+name+")")))
            except Exception:
                return False
        elif verb and name:
            try:
                return bool(list(prolog.query(verb+"("+name+")")))
            except Exception:
                return False
        else:
            return True

    def make_action(self):
        obj1 = None
        prep = None
        obj2 = None
        for subtree in self._chunked.subtrees(filter=lambda t: t.label() == 'verb_at_beginning'):
            for obj in subtree.subtrees(filter=lambda t2: t2.label() == 'object'):
                for token in obj:
                        if token[1] == 'NNP' or (token[1] == 'NN' and (token[0] == 'table')):
                            if obj1:
                                obj2 = token[0].lower()
                            else:
                                obj1 = token[0].lower()
            for p in subtree.subtrees(filter=lambda t3: t3.label() != 'object'):
                for token in p:
                    if len(token) > 1:
                        if token[1] == 'IN':
                            prep = token[0].lower()
        if prep and obj1 and obj2:
            return prep + "(" + obj1 + "," + obj2 + ")"
        else:
            return None


if __name__ == '__main__':

    nlp = NLP()

    prolog = Prolog()

    prolog.consult("rules.pl")
    choice = None
    while True:
        if not choice:
            choice = raw_input("Type \"voice\" for request commands using voice or \"text\" for request commands by text: ")
        if choice == "text":
            sentence = raw_input("Type: ")
        elif choice == "voice":
            r = sr.Recognizer()
            with sr.Microphone() as source:  # use the default microphone as the audio source
                r.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
                print("Say: ")
                audio = r.listen(source)  # listen for the first phrase and extract it into audio data
                print('Wait..')
            try:
                sentence = r.recognize_google(audio, language="english")
                if sentence.split(" ")[0] == 'is':
                    sentence = sentence+"?"
                print("You said: " + sentence)  # recognize speech using Google Speech Recognition
            except Exception:  # speech is unintelligible
                print("Could not understand audio")
                continue
        else:
            choice = None
            continue
        nlp.process(sentence)
        objs = nlp.getObjects()
        if nlp.isKnowledge():
            for obj in objs:
                nlp.add_knowledge_obj(obj)
            nlp.add_knowledge_phrase()
        elif nlp.isQuestion():
            resp = nlp.make_query()
            if resp is None:
                print("False (your sentence may not be correct)")
            else:
                print("Answer: "+str(resp))
        else:
            sentence = sentence[0].lower() + sentence[1:]
            if nlp.isAction():
                s = nlp.make_action()
                if s is not None:
                    print('GOAL: '+s)
                    res = True
                    try:
                        list(prolog.query("do(["+s+"])"))
                        if bool(list(prolog.query(s))):
                            print("Goal reached!")
                            moves = list(prolog.query("move(X,Y,Z)"))
                            print("New positions: ")
                        else:
                            print("Please require a correct action and in a more precise way..")
                            res = False
                    except Exception:
                        print("Sorry, I'm unable to satify your request.")
                    if res:
                        l = list(prolog.query("on(X,Y)"))
                        for block in l:
                            if block['Y'] != 'table':
                                print(block['X'].upper()+" is on "+block['Y'].upper())
                            else:
                                print(block['X'].upper()+" is on "+block['Y'])
                else:
                    print("Your sentence does not seem to be correct.")
            else:
                print("Your sentence does not seem to be correct.")