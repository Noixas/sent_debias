from __future__ import absolute_import, division, print_function
import numpy as np
import json
import os
import logging
import argparse
from scipy import spatial
import torch
import itertools
from itertools import combinations
import collections
import pickle

# word embeddings
import gensim
import gensim.downloader as api
from gensim.utils import tokenize
from eval_utils import isInSet

# first party
import weat
from run_classifier import get_encodings, compute_gender_dir, get_tokenizer_encoder
from run_classifier import get_def_examples
from bias_data.def_sent_utils import *
from my_debiaswe import my_we

logger = logging.getLogger(__name__)

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
					datefmt = '%m/%d/%Y %H:%M:%S',
					level = logging.INFO)

DATA_DIR = "../bias_data/gender_tests/"
MAX_SEQ_LENGTH = 128
DEVICE = torch.device("cuda") if torch.cuda.is_available() else None

'''
Example usage:
CUDA_VISIBLE_DEVICES=2 python eval_bias.py \
	--model_path aaai-results/qnli/debias/ \
	--debias \
	--def_pairs_name large_real \
	--model qnli \
	--output_name large_real

CUDA_VISIBLE_DEVICES=3 python eval_bias.py \
	--model_path aaai-results/cola/old_biased \
	--debias \
	--def_pairs_name domain5 \
	--model biased_cola \
	--output_name domain5

python eval_bias.py --debias --def_pairs_name wikitext --output
_name dummy --model pretrained
'''

def load_json(sent_file):
    ''' Load from json. We expect a certain format later, so do some post processing '''
    logger.info("Loading %s..." % sent_file)
    all_data = json.load(open(sent_file, 'r'))
    data = {}
    for k, v in all_data.items():
        examples = v["examples"]
        data[k] = examples
    return all_data  # data

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--model_path",
						type=str,
						default="bert-base-uncased",
						help="Path of the model to be evaluated")
	parser.add_argument("--debias",
						action='store_true',
						help="Whether to debias.")
	parser.add_argument("--equalize",
						action='store_true',
						help="Whether to equalize.")
	parser.add_argument("--def_pairs_name", default="large_real", type=str,
						help="Name of definitional sentence pairs.")
	parser.add_argument("--model", "-m", type=str, default="dummy")
	parser.add_argument("--output_name", type=str, required=True)
	parser.add_argument("--encode_only", action='store_true')
	args = parser.parse_args()
	args.results_dir = os.path.join("acl_bias_eval_results", args.model)
	args.do_lower_case = True
	args.cache_dir = None
	args.local_rank = -1
	args.max_seq_length = 128
	args.eval_batch_size = 8
	args.n_samples = 100000
	args.parametric = True
	args.tune_bert = False
	args.normalize = True

	# word embeddings
	args.word_model = 'fasttext-wiki-news-subwords-300'
	wedata_path = 'my_debiaswe/data'
	args.wedata_path = wedata_path
	args.definitional_filename = os.path.join(wedata_path, 'definitional_pairs.json')
	args.equalize_filename = os.path.join(wedata_path, 'equalize_pairs.json')
	args.gendered_words_filename = os.path.join(wedata_path, 'gender_specific_complete.json')

	return args

def binary_weat(targets, attributes):
	targetOne = []
	targetTwo = []
	for x in targets[0]:
		targetOne.append(_binary_s(x, attributes))
	for y in targets[1]:
		targetTwo.append(_binary_s(y, attributes))

	weat_score = np.absolute(sum(targetOne) - sum(targetTwo))

	wtmp = [_binary_s(t, attributes) for t in targets[0] + targets[1]]
	effect_std = np.std(wtmp)
	num = np.absolute((sum(targetOne)/float(len(targetOne)) - sum(targetTwo)/float(len(targetTwo))))
	effect_size = (num/effect_std)
	return weat_score, effect_size

def _binary_s(target, attributes):
	groupOne = []
	groupTwo = []
	for ai in attributes[0]:
		groupOne.append(spatial.distance.cosine(target, ai))
	for aj in attributes[1]:
		groupTwo.append(spatial.distance.cosine(target, aj))
	return sum(groupOne)/float(len(groupOne)) - sum(groupTwo)/float(len(groupTwo))
	# return np.absolute(sum(groupOne)/float(len(groupOne)) - sum(groupTwo)/float(len(groupTwo)))

def save_dict_to_json(D, output_eval_file):
	# D = {"eval_loss": 0.5, "train_loss": 0.99, "nya": {"hello": 3.1, "world": 9.9}}
	# output_eval_file = 'data.json'
	with open(output_eval_file, 'w') as f:
		json.dump(D, f)

	# with open(output_eval_file, 'rb') as f:
	# 	data = json.load(f)
	# print(data)

def run_binary_weat_test(encs):
	targ1 = list(encs['targ1']['encs'].values())
	targ2 = list(encs['targ2']['encs'].values())
	attr1 = list(encs['attr1']['encs'].values())
	attr2 = list(encs['attr2']['encs'].values())
	targets = [targ1, targ2]
	attributes = [attr1, attr2]
	weat_score, effect_size = binary_weat(targets, attributes)
	return weat_score, effect_size


def evaluate(args, def_pairs, smoothing=False, word_level=False):
	
	if (not args.encode_only):
		if (not os.path.exists(args.results_dir)): os.makedirs(args.results_dir)
		results_path = os.path.join(args.results_dir, args.output_name)
		if (not smoothing and os.path.exists(results_path)): 
			print("Results already evaluated in {}".format(results_path))
			return

	results = []
	all_tests_dict = dict()

	tokenizer, bert_encoder = get_tokenizer_encoder(args, DEVICE)
	gd = None
	if (args.debias):
		gd = compute_gender_dir(DEVICE, tokenizer, bert_encoder, def_pairs, 
			args.max_seq_length, word_level=word_level)
		logger.info("Computed (gender) bias direction")
24edscfsgsgsegtset
24edscfsgsgsegtset
24edscfsgsgsegtset24edscfsgsgsegtset
24edscfsgsgsegtset
24edscfsgsgsegtsetv

24edscfsgsgsegtset
24edscfsgsgsegtset
24edscfsgsgsegtsetv
24edscfsgsgsegtset
24edscfsgsgsegtset24edscfsgsgsegtset

	with open(args.gendered_words_filename, "r") as f:
		gender_specific_words = json.load(f)
	specific_set = set(gender_specific_words)

	for test_id in ['6', '6b', '7', '7b', '8', '8b']:
		filename = "sent-weat{}.jsonl".format(test_id)
		sent_file = os.path.join(DATA_DIR, filename)
		data = load_json(sent_file)

		encs = get_encodings(args, data, tokenizer, bert_encoder, gd, 
			DEVICE, word_level=word_level, specific_set=specific_set)
		if (args.encode_only):
			if (args.debias):
				outfile_name = 'debiased_encs{}.pkl'.format(test_id)
			else:
				outfile_name = 'biased_encs{}.pkl'.format(test_id)

			with open(os.path.join(args.results_dir, outfile_name), 'wb') as outfile:
				pickle.dump(encs, outfile)
			continue
		'''
		encs: targ1, targ2, attr1, attr2
		         -> category
		         -> encs
		         	-> (id1, sent1_emb), (id2, sent2_emb), ...
		'''
		esize, pval = weat.run_test(encs, n_samples=args.n_samples, parametric=args.parametric)
		
		# weat_score, effect_size = run_binary_weat_test(encs)
		# results.append("{}: esize={} pval={} | w_score={} esize={}".format(filename, 
		# 	esize, pval, weat_score, effect_size))
		# test_results = {"esize": esize, "pval": pval, "weat_score": weat_score, "effect_size": effect_size}

		result = "{}: esize={} pval={}".format(filename, esize, pval)
		print(filename, result)
		results.append(result)
		test_results = {"esize": esize, "pval": pval}
		
		all_tests_dict[filename] = test_results

	if (args.encode_only): return
	# print and save results
	for result in results: logger.info(result)
	results_path = os.path.join(args.results_dir, args.output_name)
	if (not smoothing):
		save_dict_to_json(all_tests_dict, results_path)
		return

	# smoothing
	if (os.path.exists(results_path)): # merge results
		with open(results_path, 'rb') as f:
			old_dict = json.load(f)
			for filename in old_dict:
				test_results = old_dict[filename]
				for metric in ["esize", "pval"]:
					test_results[metric].append(all_tests_dict[filename][metric])
			save_dict_to_json(old_dict, results_path)
	else:
		for filename in all_tests_dict:
			for metric in ["esize", "pval"]:
				all_tes ts_dict[filename][metric] = [all_tests_dict[filename][metric]]
		save_dict_to_json(all_tests_dict, results_path)

def eval_sent_debias():
	args = parse_args()
	def_pairs_name = args.def_pairs_name
	size_prefix = "allsize"
	accdomain_prefix = "accdomain"
	domain_prefix = "moredomain"
	if (def_pairs_name.startswith(size_prefix)):
		# evaluate model 
		bucket_list = get_single_domain_in_buckets()
		indices = np.arange(len(bucket_list))

		size = int(def_pairs_name[len(size_prefix):])
		
		choices_list = list(combinations(indices, size))
		logger.info(choices_list)
		for choices in choices_list:
			logger.info(choices)
			chosen_buckets = [bucket_list[i] for i in choices]
			def_pairs = []
			for bucket in chosen_buckets:
				def_pairs += bucket
			evaluate(args, def_pairs, smoothing=True)
	elif (def_pairs_name.startswith(accdomain_prefix)):
		domain_list = get_all_domains(1000)
		for domain in domain_list: print("domain size={}".format(len(domain)))
		indices = np.arange(len(domain_list))

		size = int(def_pairs_name[len(accdomain_prefix):])
		choices_list = list(combinations(indices, size))
		logger.info(choices_list)
		for choices in choices_list:
			logger.info(choices)
			chosen_buckets = [domain_list[i] for i in choices]
			def_pairs = []
			for bucket in chosen_buckets:
				def_pairs += bucket
			evaluate(args, def_pairs, smoothing=True)
	elif (def_pairs_name.startswith(domain_prefix)):
		indices = np.arange(4) # 4 domains
		size = int(def_pairs_name[len(domain_prefix):])
		choices_list = list(combinations(indices, size))

		fixed_size = 1080
		domain_size = int(fixed_size / size)
		logger.info("{} samples per domain; domain: {}".format(domain_size, choices_list))
		domain_list = get_all_domains(domain_size)
		for choices in choices_list: 
			logger.info(choices)
			chosen_buckets = [domain_list[i] for i in choices]
			def_pairs = []
			for bucket in chosen_buckets: def_pairs += bucket
			evaluate(args, def_pairs, smoothing=True)

	else:
		def_pairs = get_def_pairs(def_pairs_name)
		evaluate(args, def_pairs, smoothing=False)


def test_word():
	fasttext_model300 = api.load('fasttext-wiki-news-subwords-300')
	emb = fasttext_model300.word_vec("a")

	emb = fasttext_model300.word_vec("hello")

# class WordEvaluator(object):
# 	"""docstring for Evaluator"""
# 	def __init__(self, args):
# 		super(WordEvaluator, self).__init__()
# 		self.args = args

# 		# define files for evaluation
# 		self.filenames = []
# 		for i in [6, 7, 8]:
# 			self.filenames.append("sent-weat{}.jsonl".format(i))
# 			self.filenames.append("sent-weat{}b.jsonl".format(i))
# 		self.word_filenames = []
# 		for i in [6, 7, 8]:
# 			self.word_filenames.append("weat{}.jsonl".format(i))
# 			self.word_filenames.append("weat{}b.jsonl".format(i))

# 		self.vocab = self.init_vocab() # 190 words
# 		self.expand_specific_vocab()
		
# 		self.E = my_we.WordEmbedding(args.word_model, self.vocab)
# 		if (args.debias): self.debias()

# 	# def is_specific(self, word):
# 	# 	gender_specific_words = self.gender_specific_words
# 	# 	for wi in [word, my_pluralize(word), my_singularize(word)]:
# 	# 		if (wi in gender_specific_words): return True
# 	# 		if (wi.lower() in gender_specific_words): return True
# 	# 	return False

# 	def init_vocab(self):
# 		print("Initializing vocab for evaluation...")
# 		vocab = set()
# 		for filename in self.filenames:
# 			sent_file = os.path.join(DATA_DIR, filename)
# 			data = load_json(sent_file)
# 			for key in ['targ1', 'targ2', 'attr1', 'attr2']:
# 				texts = data[key]['examples']
# 				for text in texts:
# 					words = set(tokenize(text))
# 					vocab = vocab.union(words)

# 		args = self.args
# 		with open(args.definitional_filename, "r") as f:
# 			definitional = json.load(f)
# 		# print("definitional", definitional)

# 		with open(args.equalize_filename, "r") as f:
# 			equalize = json.load(f)
# 		# print("equalize", equalize)

# 		with open(args.gendered_words_filename, "r") as f:
# 			gender_specific_words = json.load(f)
# 		print("gender specific", len(gender_specific_words), gender_specific_words[:10])

# 		for pair in definitional:
# 			vocab = vocab.union(set(pair))

# 		for pair in equalize:
# 			if (pair[0] in vocab): vocab.add(pair[1])
# 			if (pair[1] in vocab): vocab.add(pair[0])

# 		print("Vocabulary size {}.".format(len(vocab)))
# 		assert('gal' in vocab)

# 		self.definitional = definitional
# 		self.equalize = equalize
# 		self.gender_specific_words = gender_specific_words
		
# 		return vocab

# 	# expanding gender_specific_full to gender_specific_complete
# 	# with gender specific words from tests.
# 	def expand_specific_vocab(self):
# 		# expand gender specific words 
# 		gender_specific_words = set(self.gender_specific_words)
# 		for word_filename in self.word_filenames:
# 			word_file = os.path.join(DATA_DIR, word_filename)
# 			data = load_json(word_file)
# 			for key in ['targ1', 'targ2', "attr1", "attr2"]:
# 				category = data[key]["category"]
# 				print("category={}".format(category))
# 				if (not "male" in category.lower()): continue
# 				words = data[key]["examples"]
# 				print(words)
# 				gender_specific_words = gender_specific_words.union(set(words))
# 		self.gender_specific_words = list(gender_specific_words)

# 	def debias(self):
# 		print("debiasing...")
# 		definitional = self.definitional
# 		equalize = self.equalize
# 		gender_specific_words = self.gender_specific_words

# 		gender_direction = my_we.doPCA(definitional, self.E).components_[0]
# 		specific_set = set(gender_specific_words)
# 		for i, w in enumerate(self.vocab):
# 			if (not isInSet(w, specific_set)):
# 				self.E.vecs[i] = my_we.drop(self.E.vecs[i], gender_direction)
# 		self.E.normalize()

# 		# Equalize
# 		equalize_subset = []
# 		for pair in equalize:
# 			if (pair[0] in self.vocab):
# 				equalize_subset.append(pair)
# 		candidates = {x for e1, e2 in equalize_subset for x in [(e1.lower(), e2.lower()),
# 														 (e1.title(), e2.title()),
# 														 (e1.upper(), e2.upper())]}
# 		# print(candidates)
# 		for (a, b) in candidates:
# 			if (a in self.E.index and b in self.E.index):
# 				y = my_we.drop((self.E.v(a) + self.E.v(b)) / 2, gender_direction)
# 				z = np.sqrt(1 - np.linalg.norm(y)**2)
# 				if (self.E.v(a) - self.E.v(b)).dot(gender_direction) < 0:
# 					z = -z
# 				self.E.vecs[self.E.index[a]] = z * gender_direction + y
# 				self.E.vecs[self.E.index[b]] = -z * gender_direction + y
# 		self.E.normalize()
# 		print("finished debiasing")


# 	def get_sent_embedding(self, sent):
# 		words = tokenize(sent)
# 		# word_embeddings = np.array([self.model.word_vec(w) for w in words]) # T x W(300)
# 		word_embeddings = np.array([self.E.v(w) for w in words]) # T x W(300)
# 		sent_embeddings = np.mean(word_embeddings, axis=0)
# 		return sent_embeddings

# 	def get_encodings(self, data):
# 		results = collections.defaultdict(dict)
# 		for key in ['targ1', 'targ2', 'attr1', 'attr2']:
# 			texts = data[key]['examples']
# 			category = data[key]['category'].lower()
# 			logger.info("category={}".format(category))

# 			results[key]['category'] = category
# 			encs = dict()
# 			for i, text in enumerate(texts):
# 				encs[text] = self.get_sent_embedding(text)
# 			results[key]['encs'] = encs

# 		return results

# 	def evaluate(self):
# 		args = self.args
# 		if (not os.path.exists(args.results_dir)): os.makedirs(args.results_dir)
# 		results_path = os.path.join(args.results_dir, args.output_name)
# 		results = []
# 		all_tests_dict = dict()

# 		for filename in self.filenames:
# 			sent_file = os.path.join(DATA_DIR, filename)
# 			data = load_json(sent_file)
# 			encs = self.get_encodings(data)
# 			esize, pval = weat.run_test(encs, n_samples=args.n_samples, parametric=args.parametric)

# 			result = "{}: esize={} pval={}".format(filename, esize, pval)
# 			print(filename, result)
# 			results.append(result)
# 			test_results = {"esize": esize, "pval": pval}
			
# 			all_tests_dict[filename] = test_results

# 		# print and save results
# 		for result in results: logger.info(result)
# 		results_path = os.path.join(args.results_dir, args.output_name)

# 		save_dict_to_json(all_tests_dict, results_path)
# 		return

def test_fastText():
	args = parse_args()
	evaluator = WordEvaluator(args)
	evaluator.evaluate()

def test_bertword():
	args = parse_args()
	def_pairs = json.load(open(args.definitional_filename, "r"))
	evaluate(args, def_pairs, smoothing=False, word_level=True)

def store_encodings():
	args = parse_args()
	def_pairs = get_all()
	evaluate(args, def_pairs, word_level=False)

if __name__ == '__main__':
	store_encodings()





