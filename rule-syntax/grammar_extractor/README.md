1. Prerequisite

    run the following commands
    ```bash
    $ pip install benepar
    $ python -m spacy download en_core_web_sm
    ```

2. Usage

    run `par_sent.py`
    
    
    
    
    
    # Grammar extraction rules
    
    # Extract grammar phenomena from treebanks
    
    ## Key Treebank tags that are useful
    
    ### POS tags for tense and voice
    
    **VB**：动词基础形式（除be动词外，其它动词VB与VBP一般同形，在树库中有的标了VB有的标了VBP）
    
    **VBD**：动词过去式
    
    **VBG**：动名词/动词现在分词
    
    **VBN**：过去分词
    
    **VBP**：非第三人称单数形式
    
    **VBZ**：第三人称单数形式
    
    **MD**：情态动词will/would/should等，这里我们只关注构成一般将来时的will
    
    ### Consituency tags for clause
    
    **S** - simple declarative clause, i.e. one that is not introduced by a (possible empty) subordinating conjunction or a *wh*-word and that does not exhibit subject-verb inversion.
    **SBAR** - Clause introduced by a (possibly empty) subordinating conjunction. 连词引导的从句（包括宾从和定从）
    **SBARQ** - Direct question introduced by a *wh*-word or a *wh*-phrase. Indirect questions and relative clauses should be bracketed as SBAR, not SBARQ. (wh开头的疑问句，是真的疑问句）
    **SINV** - Inverted declarative sentence, i.e. one in which the subject follows the tensed verb or modal. （倒装句）
    **SQ** - Inverted yes/no question, or main clause of a *wh*-question, following the *wh*-phrase in SBARQ. 
    
    **WHADJP** - *Wh*-adjective Phrase. Adjectival phrase containing a *wh*-adverb, as in *how hot*. （疑问词修饰形容词的短语）
    **WHAVP** - *Wh*-adverb Phrase. Introduces a clause with an NP gap. May be null (containing the 0 complementizer) or lexical, containing a *wh*-adverb such as *how* or *why*. （疑问词修饰副词）
    **WHNP** - *Wh*-noun Phrase. Introduces a clause with an NP gap. May be null (containing the 0 complementizer) or lexical, containing some *wh*-word, e.g. *who*, *which book*, *whose daughter*, *none of which*, or *how many leopards*. （疑问词修饰名词）
    **WHPP** - *Wh*-prepositional Phrase. Prepositional phrase containing a *wh*-noun phrase (such as *of which* or *by whose authority*) that either introduces a PP gap or is contained by a WHNP. （疑问词+介词）（这种也是定从）
    
    ### Markers
    
    markers_of_present_perfect_tense = [
        "has",
        "have",
        "'ve",
    ]
    markers_of_past_perfect_tense = [
        "had",
        "'d",
    ]
    markers_of_present_continuous_tense = [
        "is",
        "am",
        "'m"
        "are",
        "'re",
    ]
    markers_of_past_continuous_tense = [
        "was",
        "were",
    ]
    markers_of_future_tense = [
        "will",
        "'ll",
    ]
    markers_of_object_clause = [
        "whether",
        "if",
        "who",
        "whose",
        "what",
        "whatever",
        "which",
        "whichever",
        "when",
        "where",
        "how",
        "why",
        "that"
    ]
    markers_of_attributive_clause = [
        "who",
        "whom",
        "which",
        "that",
        "whose",
        "where",
        "why",
        "when",
    ]
    
    
    
    ### Example trees
    
    example_sentences = [
        "(TOP (S (NP (DT A) (NN record) (NN date)) (VP (VBZ has) (RB n't) (VP (VBN been) (VP (VBN set)))) (. .)))",
        "(TOP (S (NP (NNP Richard) (NNP Stoltzman)) (VP (VBZ has) (VP (VBN taken) (NP (DT a) (NN gentler) (, ,) (ADJP (RBR more) (JJ audience-friendly)) (NN approach)))) (. .)))",
        "(TOP (S (VP (VP (VB Come)) (VP (VB see) (SBAR (WHADVP (WRB how)) (S (NP (PRP we)) (VP (VBP continue) (NP (DT this) (NN tradition))))))) (. .) ('' '')))",
        "(TOP (S (NP (PRP i)) (VP (VBP think) (SBAR (S (NP (NNP Miramar)) (VP (VBD was) (NP (NP (DT a) (JJ famous) (NN goat) (NN trainer)) (CC or) (NP (NN something))))))) (. .)))",
        "(TOP (SINV (`` ``) (S (S (NP (NP (DT Those)) (SBAR (WHNP (WP who)) (S (S (VP (VBP have) (NP (DT no) (NN money)))) (CC and) (S (VP (VBP are) (RB n't) (VP (VBG buying))))))) (VP (VB think) (SBAR (S (NP (NP (PRP it))) (VP (VBZ 's) (ADJP (JJ right)) (S (VP (TO to) (VP (NN refrain))))))))) (, ,) (CC but) (S (NP (NP (DT those)) (PP (IN with) (NP (NN money))) (SBAR (WHNP (WP who)) (S (VP (VBP want) (S (VP (TO to) (VP (VB buy) (PP (IN for) (NP (PRP themselves)))))))))) (VP (VBP pay) (NP (DT no) (NN attention))))) (, ,) ('' '') (VP (VBZ says)) (NP (NP (DT an) (NN official)) (PP (IN of) (NP (DT the) (NN Japan-U.S) (. .) (NNP Business) (NNP Council)))) (. .)))",
        "(TOP (S (SBARQ (WHNP (WP Who)) (SQ (VBZ is) (NP (NN artist) (NNP Gunther) (NNP Uecker)))) (, ;) (S (VP (VB explain))) (. ?)))",
        "(TOP (SBARQ (UCP (WHADVP (WRB Where)) (CC and) (WHPP (IN to) (WHNP (WP whom)))) (SQ (VBP do) (NP (PRP you)) (VP (VB want) (S (NP (PRP it)) (VP (VBN faxed))))) (. ?)))",
        "(TOP (S (NP (DT A) (CD 1970) (NN evaluation)) (VP (VBD said) (SBAR (S (NP (NNP Bush)) (VP (VP (`` '') (ADVP (RB clearly)) (VBZ stands) (PRT (RP out)) (PP (IN as) (NP (DT a) (NML (JJ top) (NN notch)) (NML (NN fighter) (NN interceptor)) (NN pilot))) ('' '')) (CC and) (VP (VBD was) (`` '') (NP (NP (DT a) (JJ natural) (NN leader)) (SBAR (WHNP (WP whom)) (S (NP (PRP$ his) (NNS contemporaries)) (VP (VBP look) (PP (IN to)) (PP (IN for) (NP (NN leadership)))))))))))) (. .) ('' '')))",
        "(TOP (SINV (VP (VBD Came)) (NP (NP (DT the) (NN disintegration)) (PP (IN of) (NP (NP (DT the) (NNPS Beatles) (POS ')) (NNS minds))) (PP (IN with) (NP (NP (NN LSD)) (SBAR (WHNP (WDT which)) (S (VP (VBZ has) (VP (VBN caused) (, ,) (PP (IN among) (NP (NNS others))) (, ,) (NP (NP (NP (JJ schizophrenic) (NNS lyrics)) (PP (JJ such) (IN as) (S (`` '') (NP (PRP I)) (VP (VBP am) (NP (DT the) (NNP Walrus))) ('' '')))) (CC and) (NP (NP (JJ incoherent) (JJ schizophrenic) (JJ musical) (NNS expositions)) (PP (IN like) (NP (`` '') (NNP Revolution) (NNP number) (CD 9) ('' '')))))))))))) (. .)))"
    ]
    
    
    
    
    
    ## Pipeline
    
    ### 1. Parser
    
    Use the newest constituency parser (contributed by Sen Yang) based on [Berkeley Neural Parser](https://spacy.io/universe/project/self-attentive-parser) (benepar). Given an input of sentences, the parse first split the text to separate sentences, then **output a parsed tree** to each sentence respectively.
    
    ### 2. Rule-based Grammar Extractor
    
    Given a parsed tree (constituency/POS tags), we go through a breath-first traversal. 
    
    We store the extracted result into a dict.
    
    For each Constituency `label`,  we apply a bunch of rules as follows:
    
    sud code
    
    ```plain
    if label is SBARQ:
        dict['question'] is True (it's a question)
    if label is NP:
        go to children
        if children is InternalTreebankNode:
            if children.label is SBAR:
                go to children's_children
                if children's_children.label is S:
                    dict['attributive clause - that'] is True (it's a attributive clause conducted by that)
                if children's_children.label is WHNP:
                go to children's_children's_children
                if children's_children's_children.word in markers_of_attributive_clause:
                    dict['attributive clause - {word}] is True (it's a attributive clause conducted by "word")
    if label is VP:
        go to children
        if children is LeafTreebankNode:
            if children.word in markers_of_future_tense:
                dict['simple future tense'] is True
            elif children.tag is VB:
                dict['simple present tense'] is True
            elif children.tag is VBP:
            ...
            ...
            ...
    return grammars, sentence
    ```