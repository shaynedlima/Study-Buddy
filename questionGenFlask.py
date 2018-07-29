from flask import Flask, render_template, url_for, request, send_from_directory
import json



arrQuestions = []
def nlp(text):
	from thesaurus import Word
	import string

	def extract_candidate_words(text, good_tags=set(['JJ','JJR','JJS','NN','NNP','NNS','NNPS'])):
		import itertools, nltk, string

		# exclude candidates that are stop words or entirely punctuation
		punct = set(string.punctuation)
		stop_words = set(nltk.corpus.stopwords.words('english'))
		# tokenize and POS-tag words
		tagged_words = itertools.chain.from_iterable(nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text)))
		# filter on certain POS tags and lowercase all words
		candidates = [word.lower() for word, tag in tagged_words if tag in good_tags and word.lower() not in stop_words and not all(char in punct for char in word)]

		return candidates

	def score_keyphrases_by_textrank(text, n_keywords=0.2):
		from itertools import takewhile, tee, izip

		import networkx, nltk

		# tokenize for all words, and extract *candidate* words
		words = [word.lower()
				for sent in nltk.sent_tokenize(text)
				for word in nltk.word_tokenize(sent)]
		candidates = extract_candidate_words(text)
		# build graph, each node is a unique candidate
		graph = networkx.Graph()
		graph.add_nodes_from(set(candidates))
		# iterate over word-pairs, add unweighted edges into graph
		def pairwise(iterable):
			"""s -> (s0,s1), (s1,s2), (s2, s3), ..."""
			a, b = tee(iterable)
			next(b, None)
			return izip(a, b)

		for w1, w2 in pairwise(candidates):
			if w2:
				graph.add_edge(*sorted([w1, w2]))
		# score nodes using default pagerank algorithm, sort by score, keep top n_keywords
		ranks = networkx.pagerank(graph)
		if 0 < n_keywords < 1:
			n_keywords = int(round(len(candidates) * n_keywords))
		word_ranks = {word_rank[0]: word_rank[1] for word_rank in sorted(ranks.iteritems(), key=lambda x: x[1], reverse=True)[:n_keywords]}
		keywords = set(word_ranks.keys())
		# merge keywords into keyphrases
		keyphrases = {}
		j = 0
		for i, word in enumerate(words):
			if i < j:
				continue
			if word in keywords:
				kp_words = list(takewhile(lambda x: x in keywords, words[i:i+10]))
				avg_pagerank = sum(word_ranks[w] for w in kp_words) / float(len(kp_words))
				keyphrases[' '.join(kp_words)] = avg_pagerank
				# counter as hackish way to ensure merged keyphrases are non-overlapping
				j = i + len(kp_words)

		return sorted(keyphrases.iteritems(), key=lambda x: x[1], reverse=True)

	# text = "The movement of water around our planet is vital to life as it supports plants and animals. Powered by the Sun, the water cycle is happening all the time, though some parts of the cycle take hundreds of years (for example, some of the Earth's water is frozen in polar regions or lying in underground reservoirs and not included in the constant movement of water through evaporation, condensation and precipitation)."

	# text = "The functional and organic CNS consequences of marijuana have received great scrutiny. Marijuana use is well recognized to distort sensory perception and impair motorcoordination, but these acute effects generally clear in 4 to 5 hours. With continued use, these changes may progress to cognitive and psychomotor impairments, such as the inability to judge time, speed, and distance. Among adolescents, such impairment often leads to automobile accidents. Marijuana increases the heart rate and sometimes blood pressure and it may cause angina in a person with coronary artery disease. The lungs are affected by chronic marijuana smoking; laryngitis, pharyngitis, bronchitis, cough, hoarseness, and asthmalike symptoms all have been described, along with mild but significant airway obstruction. Smoking a marijuana cigarette, compared with a tobacco cigarette, is associated with a 3-fold increase in the amount of tar inhaled and retained in the lungs, as a consequence of deeper inhalation and longer breath holding."

	#text = "Histone methylation usually reversibly represses DNA transcription, but can activate it in some cases depending on methylation location. Histone acetylation relaxes DNA coiling, allowing for transcription. DNA methylation at CpG islands represses transcription. A nucleoside is a base and a deoxyribose (sugar). Deamination of cytosine makes uracil. Deamination of adenine makes guanine."

	# print(score_keyphrases_by_textrank(text))
	# print(extract_candidate_words(text))
	string = text.split('.')
	keyphraserank = score_keyphrases_by_textrank(text)
	#print('=================================================')
	#print(text)
	#print('=================================================')
	for phraserank in keyphraserank:
		phrase, rank = phraserank
		#print('************')
		print(phrase)
		#print('************')
		#print(phrase)
		#print(w.synonyms())

		word_of_interest = phrase

		word_of_interest = word_of_interest.lower()
		#word we are replacing
		quiz_sentence = ""

		#for sentence in string:
		#     if word_of_interest in sentence.lower():
		#         quiz_sentence = sentence
		#         print(string)
		#         string.remove(sentence)
		#         print(string)

		i = 0
		while (i < len(string)):
			sentence = string[i]
			if word_of_interest in sentence.lower():
				quiz_sentence = sentence
				string.remove(sentence)
				break
			i+=1


		question_blanked = quiz_sentence.lower().replace(" " + word_of_interest, " ____").strip()
		if len(question_blanked) > 0:
			question_blanked = question_blanked[0].upper() + question_blanked[1:]
			arrQuestions.append((question_blanked, word_of_interest))



app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/quizFromText.html')
def quizFromText():
	return render_template("quizFromText.html")

@app.route('/quizFromFile.html')
def quizFromFile():
	return render_template("quizFromFile.html")

@app.route('/quizFromCamera.html')
def quizFromCamera():
	return render_template("quizFromCamera.html")


@app.route('/quizPage.html', methods=['GET', 'POST'])
def quizPage():

	jsonarr = json.dumps(arrQuestions)
	print('hey')
	print(jsonarr)

	return render_template("quizPage.html", jsonarr=jsonarr)

text = ''

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    text = request.form['text']
    del arrQuestions[:]
    nlp(text)
    jsonarr = json.dumps(arrQuestions)
    print(jsonarr)

    return render_template("quizPage.html", jsonarr=jsonarr)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('images', path)

@app.route('/profile/<username>')
def profile(username):
	return "Hey there %s" % username

if __name__ == "__main__":
	app.run(debug=True)
