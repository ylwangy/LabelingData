Grammar Extractor is a lightweight, easy-to-deploy tool for grammar extraction from plain English sentences. 

It consists of two components, First is a neural sentence parser based on the 'benepar' package (Berkeley Neural Parser)(The parser was provided by Sen Yang). We first trained a model that can turn a natural sentence into a treebank (In linguistic, a treebank is a parsed text corpus that annotates syntactic or semantic sentence structure), which can be demonstrated as follows:

The second part is a rule-based grammar extractor. Given the treebank of a sentence, the extractor is able to identify every tense usage of verbs (simple present tense, simple future tense, simple past tense, present continuous tense, present perfect tense, past perfect tense, past continuous tense), also outputs the classification of clauses (object clauses and their marker words, attributive clause and their marker words, adverbial clauses and their marker words). These are done with hand-crafted rules. These rules are very accurate on gold-labeled treebanks, while sophisticated when it comes to designing them.
The treebanks that the model parsed have both POS tags and consituency labels. POS tags are good indicators of verb tenses and voices. Consituency labels are good indicators for clauses classification.

POS tags for tenses and voices
**VB**：动词基础形式（除be动词外，其它动词VB与VBP一般同形，在树库中有的标了VB有的标了VBP）

**VBD**：动词过去式

**VBG**：动名词/动词现在分词

**VBN**：过去分词

**VBP**：非第三人称单数形式

**VBZ**：第三人称单数形式

**MD**：情态动词will/would/should等，这里我们只关注构成一般将来时的will

Consituency labels for clauses classification
**S** - simple declarative clause, i.e. one that is not introduced by a (possible empty) subordinating conjunction or a *wh*-word and that does not exhibit subject-verb inversion.
**SBAR** - Clause introduced by a (possibly empty) subordinating conjunction. 连词引导的从句（包括宾从和定从）
**SBARQ** - Direct question introduced by a *wh*-word or a *wh*-phrase. Indirect questions and relative clauses should be bracketed as SBAR, not SBARQ. (wh开头的疑问句，是真的疑问句）
**SINV** - Inverted declarative sentence, i.e. one in which the subject follows the tensed verb or modal. （倒装句）
**SQ** - Inverted yes/no question, or main clause of a *wh*-question, following the *wh*-phrase in SBARQ. 

**WHADJP** - *Wh*-adjective Phrase. Adjectival phrase containing a *wh*-adverb, as in *how hot*. （疑问词修饰形容词的短语）
**WHAVP** - *Wh*-adverb Phrase. Introduces a clause with an NP gap. May be null (containing the 0 complementizer) or lexical, containing a *wh*-adverb such as *how* or *why*. （疑问词修饰副词）
**WHNP** - *Wh*-noun Phrase. Introduces a clause with an NP gap. May be null (containing the 0 complementizer) or lexical, containing some *wh*-word, e.g. *who*, *which book*, *whose daughter*, *none of which*, or *how many leopards*. （疑问词修饰名词）
**WHPP** - *Wh*-prepositional Phrase. Prepositional phrase containing a *wh*-noun phrase (such as *of which* or *by whose authority*) that either introduces a PP gap or is contained by a WHNP. （疑问词+介词）（这种也是定从）

I will explain this with running examples. (All the examples are from the excel that QuPeiYin offers)

Tense

Present continous tense
Given the sentence "Are you going to Tianjing tomorrow? " 
The sentence is feed into our parser, then a tree is generated like this: 
(SQ (VBP Are) (NP (PRP you)) (VP (VBG going) (PP (IN to) (NP (NNP Tianjing))) (NP (NN tomorrow))) (. ?))
The output of our model is:
(['question', 'simple_present_tense'], 'Are you going to Tianjing tomorrow ? ')

Simple present tense
Given the sentence "She usually goes to school at 8:00."
tree:
(S (NP (PRP She)) (ADVP (RB usually)) (VP (VBZ goes) (PP (IN to) (NP (NN school))) (PP (IN at) (NP (CD 8:00)))) (. .))
output: (['simple_present_tense'], 'She usually goes to school at 8:00 .')

Simple past tense
Given the sentence "

clause
attributive clause - that
Given the sentence "There are some people in San Francisco that would dispute that.", 
(['simple_present_tense', 'attributive clause - that'], 'There are some people in San Francisco that would dispute that .')
...
