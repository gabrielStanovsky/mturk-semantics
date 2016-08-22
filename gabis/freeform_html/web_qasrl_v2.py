import hashlib
from os import listdir
import datetime
from threading import Lock
from os.path import join

import cherrypy
import docopt


class QaSrlTask:

    def __init__(self, candidatesDir, outputFilename):
        self.lock = Lock()
        self.user_id_counter = 1000
        self.candidates = self.load_candidates(candidatesDir)
        
        with open('./closedClass.txt') as fin:
            self.closedClassWords = [word for line in fin for word in line.strip().split() if word]
            
        print 'Loaded all {0} candidates:'.format(len(self.candidates))
        candidates_as_param = '\n'.join(self.candidates.keys()) 
        print candidates_as_param
        with open('./candidates.parameters', 'w') as fout:
            fout.write(candidates_as_param)
            
        self.outputFilename = outputFilename
        self.LOGIN_HTML = self.load_html('html/login_qasrl.html')
        self.QASRL_HTML = self.load_html('html/qasrl_v2.html')
        self.THANKS_HTML = self.load_html('html/thanks_qasrl.html')

    def prep_sent_for_hash(self, sent, predicates):
        sentToks = sent.split(' ')
        ret =  sent + '_'.join(['_'.join([str(predIndex), sentToks[predIndex]]) for predIndex, _ in predicates])
        print "hashing: {0}".format(ret)
        return ret 

    def load_candidates(self, path):
        candidates = []
        files = [join(path, f) for f in listdir(path)]
        for f in files:
            sentence, predicates = self.read_qasrl_file(f)
            if all(['is' not in inflections for (_, inflections) in predicates]):
                # Remove Copulas - note - this will remove entire sentence if there's one copula, 
                # TODO: probably only reasonable for the single predicate methodology. 
                h = hashlib.new('sha1')
                h.update(self.prep_sent_for_hash(sentence, predicates))
                candidates.append((h.hexdigest(), (sentence, predicates)))
        return dict(candidates)

    @staticmethod
    def read_qasrl_file(path):
        print "opening {0}".format(path)
        with open(path) as fin:
            lines = [line.strip() for line in fin if line.strip()]
        sentence = lines[0]
        predicates = []
        for line in lines[1:]:
            target = line.split('\t')
            pred_index, inflections = int(target[0]), target[1:]
            inflections = sorted(set(inflections))
            predicates.append((pred_index, inflections))
        return sentence, predicates

    @staticmethod
    def load_html(path):
        with open(path) as fin:
            html = fin.read()
        with open('html/style_qasrl.css') as fin:
            css = fin.read()
        with open('html/awesomplete.js') as fin:
            awesomplete_js = fin.read()
        with open('html/awesomplete.css') as fin:
            awesomplete_css = fin.read()
        with open(path[:-5] + '.js') as fin:    
            javascript = fin.read()
        return html.replace('CSS_STUB', css).replace('SCRIPT_STUB', javascript).replace('JS_AWESOMPLETE_STUB', awesomplete_js).replace('CSS_AWESOMPLETE_STUB', awesomplete_css)

    @cherrypy.expose
    def index(self):
        with self.lock:
            html = self.LOGIN_HTML
            candidate_options = [(candidate_id, sentence[0][:40] + '...')
                                 for candidate_id, sentence in self.candidates.iteritems()]
            candidate_options = [CANDIDATE_HTML.replace('CANDIDATE_ID', candidate_id).replace('CANDIDATE', candidate)
                                 for candidate_id, candidate in candidate_options]
            html = html.replace('CANDIDATES', ''.join(candidate_options))
        return html

    @cherrypy.expose
    def qasrl(self, **kwargs):
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        else:
            user_id = str(self.user_id_counter)
            self.user_id_counter += 1

        candidate_id = kwargs['candidate_id']
        sentence, predicates = self.candidates[candidate_id]

        if 'num_verb' in kwargs:
            num_verb = int(kwargs['num_verb'])
            if num_verb >= len(predicates):
                return self.thanks(**kwargs)

            questions_str = kwargs['questions_str']
            answers_token_str = kwargs['answers_token_str']
        else:
            num_verb = 0
            questions_str = ''
            answers_token_str = ''

        html = self.QASRL_HTML
        html = html.replace('USER_ID', user_id)
        html = html.replace('CANDIDATE_ID', candidate_id)
        html = html.replace('NUM_VERB', str(num_verb + 1))
        html = html.replace('QUESTIONS_STR', questions_str)
        html = html.replace('ANSWERS_TOKEN_STR', answers_token_str)

        pred_index, inflections = predicates[num_verb]
        predWord = sentence.split(' ')[pred_index]
        
        html = html.replace('CLOSED_CLASS_WORDS_STUB', ','.join(self.closedClassWords + inflections + [predWord]))
        
        html = html.replace('PRED_INDEX', str(pred_index))
        html = html.replace('SENTENCE', self.generate_sentence_html(sentence, pred_index))
        html = html.replace('PRED_INFLECTION', '\n'.join(['''<label><input type="radio" name="TRG" value="{0}" onclick="updateLiveQuestion(this);"> {0} </label><br>'''.format(infl) for infl in inflections]))
        html = html.replace('AUX_OPTIONS', '\n'.join(['<label><input type="radio" name="AUX" value="{0}" onclick="updateLiveQuestion(this);"> {0} </label><br>'.format(aux) for aux in AUX_OPTIONS]))

        tree_pps = set(sentence.split(' ')).intersection(ALL_PREPOSITIONS)
        pps = sorted(tree_pps.union(DEFAULT_PREPOSITIONS))
        html = html.replace('PP_OPTIONS', '\n'.join(['<label><input type="radio" name="PP" value="{0}" onclick="updateLiveQuestion(this);"> {0} </label><br>'.format(pp) for pp in pps]))
        html = html.replace('PH3_OPTIONS', '\n'.join(['<label><input type="radio" name="PH3" value="{0}" onclick="updateLiveQuestion(this);"> {0} </label><br>'.format(ph3) for ph3 in ['someone', 'something', 'somewhere', 'do', 'doing', 'do something', 'doing something']]))

        return html

    @staticmethod
    def generate_sentence_html(sentence, pred_index=-1):
        return ' '.join([TOKEN_HTML.replace('TINDEX', str(ti)).replace('TOKEN', t)
                         if ti != pred_index else '<span class="emph">{0}</span>'.format(t)
                         for ti, t in enumerate(sentence.split(' '))])

    @cherrypy.expose
    def thanks(self, **kwargs):
        with self.lock:
            now = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            user_id = kwargs['user_id']
            candidate_id = kwargs['candidate_id']
            sentence, predicates = self.candidates[candidate_id]
            questions_str = kwargs['questions_str']
            answers_token_str = kwargs['answers_token_str']

            h = hashlib.new('sha1')
            h.update(''.join(('Toda', user_id, candidate_id, 'Gabi')))
            code = ''.join((user_id, 'X', candidate_id, 'X', h.hexdigest()))

            annotation = '\t'.join([now, user_id, candidate_id, code, sentence, questions_str, answers_token_str])
            with open(self.outputFilename, 'a') as fout:
                print >>fout, annotation
                print annotation

            html = self.THANKS_HTML.replace('CODE', code)
        return html


# CONSTANTS (HTML) #

CANDIDATE_HTML = """
<option value="CANDIDATE_ID">CANDIDATE</option>
"""

TOKEN_HTML = """<span class="token" id="TINDEX" onclick="selectWord(this)">TOKEN</span>"""


# CONSTANTS (PREPOSITIONS) #

DEFAULT_PREPOSITIONS = set(['about', 'at', 'by', 'for', 'in', 'of', 'to', 'with'])

ALL_PREPOSITIONS = set(['aboard', 'about', 'above', 'across', 'after', 'against', 'ahead', 'along', 'amid', 'among', 'anti', 'around', 'as', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by', 'concerning', 'considering', 'despite', 'down', 'during', 'except', 'excepting', 'excluding', 'following', 'for', 'from', 'in', 'inside', 'into', 'like', 'minus', 'near', 'of', 'off', 'on', 'onto', 'opposite', 'outside', 'over', 'past', 'per', 'plus', 'regarding', 'round', 'save', 'since', 'than', 'through', 'to', 'toward', 'towards', 'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with', 'within', 'without'])

AUX_OPTIONS = ['is', 'are', 'was', 'were', 'does', 'do', 'did', 'has', 'have', 'had', 'can', 'could', 'may', 'might', 'will', 'would', 'should', 'must']# "is not", "are not", "was not", "were not", "does not", "do not", "did not", "has not", "have not", "had not", "cannot", "could not", 'may not', 'might not', "will not", "would not", "should not", "must not"]


# MAIN #

if __name__ in ['__main__', '__builtin__']:
    args = docopt.docopt("""
        Usage:
            web_qasrl.py [options]

        Options:
            --port NUM  [default: 17171]
            --candidates [default: ./web/qasrl_candidates/]
            --out FILENAME [default: annotations]
    """)
    print "port is:", args['--port']
    print args

    cherrypy.config.update({"server.socket_port" : int(args["--port"])})
    cherrypy.config.update({"server.socket_host" : "0.0.0.0"})
    cherrypy.quickstart(QaSrlTask(args['--candidates'], args['--out']))
