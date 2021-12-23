import benepar, spacy
from trees import load_trees, tree_from_str, InternalTreebankNode, LeafTreebankNode
import re

#现在完成
markers_of_present_perfect_tense = [
    "has",
    "have",
    "'ve",
    "Has",
    "Have",
]
#过去完成
markers_of_past_perfect_tense = [
    "had",
    "Had",
    "'d",
]
#现在进行
markers_of_present_continuous_tense = [
    "is",
    "Is",
    "am",
    "Am",
    "'m",
    "are",
    "Are",
    "'re",
]
#过去进行
markers_of_past_continuous_tense = [
    "was",
    "Was",
    "were",
    "Were",
]
#未来时
markers_of_future_tense = [
    "will",
    "Will",
    "'ll",
]
#宾语从句
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
    "that",
]
#定语从句
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
#状语从句
markers_of_adverbial_clause = [
    "if",
    "Whether",
    "for",
    "otherwise",
    "Until",
    "until",
    "When",
    "when",
    "unless",
    "Unless",
    "wherever",
    "Wherever",
    "after",
    "After",
    "before",
    "Before",
    "while",
    "While",
    "because",
    "Because",
    "since",
    "Since",
    "as",
    "As",
    "so",
    "So",
    "than",
    "whereas",
    "Whereas",
    "though",
    "Though",
    "Although",
    "although",
    "where",
    "Where",
    "once",
    "Once",
    "Everywhere",
    "everywhere",
]

# link verbs
link_verbs = [
    "am",
    "is",
    "are",
    "'m",
    "'s",
    "'re",
    "was",
    "were",
    "tasted",
    "feels",
    "felt",
    "looks",
    "looked",
    "smells",
    "smelt",
    "sounds",
    "sounded",
    "tastes",
    "seemed",
    "seems",
    "appeared",
    "gets",
    "got",
    "became",
    "turn",
    "turned",
    "grow",
    "grew",
    "come",
    "came",
    "go",
    "gone",
    "fall",
    "fell",
    "run",
    "ran",
    "gets",
    "becomes",
    "turns",
    "grows",
    "makes",
    "comes",
    "goes",
    "falls",
    "runs",
    "remain",
    "remained",
    "keep",
    "kept",
    "stay",
    "stayed",
    "continue",
    "continued",
    "stand",
    "stood",
    "rest",
    "rested",
    "lie",
    "lied",
    "hold",
    "held",
    "remains",
    "keeps",
    "stays",
    "continues",
    "stands",
    "rests",
    "lies",
    "holds",

]



parsing_model = "./benepar_en3"

nlp = spacy.load("en_core_web_sm")

if spacy.__version__.startswith('2'):
    nlp.add_pipe(benepar.BeneparComponent(parsing_model))
else:
    nlp.add_pipe("benepar", config={"model": parsing_model})


# input_sentences should have multiple sentences and it would be split into several sentences. 
# input_sentences1 = "Jennifer, a fourteen-year-old girl, who has won a gold medal in the International Math Olympics, is an honor to our school."
# input_sentences = "This is the little girl whose parents were killed in the great earthquake"
with open('sents.txt','r') as f:
    for line in f:
        input_sentences=line.strip()

        doc = nlp(input_sentences)
        sents = list(doc.sents)
        parse_list = []
        for sent in sents:
            parse_list.append(sent._.parse_string)


        def grammar(tree):
            grammar_dict = {}
            tokens = [_.word for _ in tree.leaves()]
            sentence = " ".join(tokens)
            node_stack = [tree]
            children = [_ for _ in node_stack[0].children]

            if re.findall(" in order that ", sentence) != []:
                grammar_dict['状语从句 - 目的 - in order that'] = True
            elif re.findall(" times ", sentence) != []:
                grammar_dict['状语从句 - 比较 - times'] = True
            elif re.findall(" as.*as ", sentence) != []:
                grammar_dict['状语从句 - 比较 - as'] = True
            elif re.findall(" [Nn]o matter ", sentence) != []:
                grammar_dict['状语从句 - 让步 - no matter'] = True
            elif re.findall(" the way.*do ", sentence) != []:
                grammar_dict['状语从句 - 方式 - the way'] = True
            elif re.findall(" so.*that ", sentence) != []:
                grammar_dict['状语从句 - 结果 - so...that'] = True
            elif re.findall(" such.*that ", sentence) != []:
                grammar_dict['状语从句 - 结果 - such...that'] = True

            for n, child in enumerate(children[:-1]):
                child_next = children[n+1]
                if isinstance(child, InternalTreebankNode) and child.label == "NP":
                    if isinstance(child_next, InternalTreebankNode) and child_next.label == "VP":
                        vp_nodes = [_ for _ in child_next.children]
                        tags = [_.tag for _ in child_next.leaves()]
                        count = 0
                        for tag in tags:
                            if tag in ["NN", "NNP", "NNS", "PRP"]:
                                count += 1
                        if count == 0:
                            grammar_dict['主谓'] = True
                        elif isinstance(vp_nodes[0], LeafTreebankNode) and vp_nodes[0].word in link_verbs:
                            grammar_dict['主系表'] = True
                        elif isinstance(vp_nodes[-1], InternalTreebankNode) and vp_nodes[-1].label != "NP":
                            grammar_dict['主谓宾宾补'] = True
                        elif count > 1:
                            grammar_dict['主谓间宾直宾'] = True
                        else:
                            grammar_dict['主谓宾'] = True


            while node_stack:
                curr_node = node_stack[0]
                node_stack = node_stack[1:]
                node_stack += [_ for _ in curr_node.children if isinstance(_, InternalTreebankNode)]
                # question is easy to spot
                if curr_node.label == "SQ":
                    grammar_dict['疑问句'] = True
                    sq_nodes = [_ for _ in curr_node.children]

                    if isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag in ["VBP", "VBZ"]:
                        count = 0
                        for leaf in curr_node.leaves():
                            if leaf.tag == "VBG":
                                count += 1
                        if count > 0:
                            grammar_dict['现在进行时'] = True
                        elif sq_nodes[0].word in markers_of_present_perfect_tense:
                            count = 0
                            for leaf in curr_node.leaves():
                                if leaf.tag == "VBN":
                                    count += 1
                            if count > 0:
                                grammar_dict['现在完成时'] = True
                            else:
                                grammar_dict['一般现在时'] = True
                        else:
                            grammar_dict['一般现在时'] = True
                    elif isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag == "VBD":
                        count = 0
                        for leaf in curr_node.leaves():
                            if leaf.tag == "VBG":
                                count += 1
                        if count > 0:
                            grammar_dict['过去进行时'] = True
                        else:
                            grammar_dict['一般过去时'] = True
                    elif isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag == "MD":
                        if sq_nodes[0].word in markers_of_future_tense:
                            grammar_dict['一般将来时'] = True

                elif curr_node.label == "SBARQ":
                    sbarq_nodes = [_ for _ in curr_node.children]
                    if isinstance(sbarq_nodes[0], InternalTreebankNode) and sbarq_nodes[0].label == "WHADVP":
                        whadvp_nodes = [_ for _ in sbarq_nodes[0].children]
                        if isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].tag in ["WRB", "WP"]:
                            grammar_dict['特殊疑问句 - {}'.format(whadvp_nodes[0].word)] = True
                    if isinstance(sbarq_nodes[1], InternalTreebankNode) and sbarq_nodes[1].label == "SQ":
                        sq_nodes = [_ for _ in sbarq_nodes[1].children]
                        count = 0
                        count1 = 0
                        for leaf in curr_node.leaves():
                            if leaf.tag == "VBG":
                                count += 1
                            if leaf.tag == "VBN":
                                count1 += 1
                        if isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag == "VBD" and count == 0 and count1 == 0:
                            grammar_dict['一般过去时'] = True
                        elif isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag == "VBP" and count == 0 and count1 == 0:
                            grammar_dict['一般现在时'] = True
                        elif isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag == "MD" and count == 0 and count1 == 0:
                            grammar_dict['一般将来时'] = True


                elif curr_node.label == "SBAR":
                    sbar_nodes = [_ for _ in curr_node.children]
                    if isinstance(sbar_nodes[0], LeafTreebankNode) and sbar_nodes[0].word == "that":
                        if sentence.split(" ")[0] == "Now":
                            grammar_dict['状语从句 - now that'] = True
                    for sbar_node in sbar_nodes:

                        if isinstance(sbar_node, LeafTreebankNode) and sbar_node.word == "If":
                            grammar_dict['状语从句 - if'] = True
                        elif isinstance(sbar_node, LeafTreebankNode) and sbar_node.word in markers_of_adverbial_clause:
                            grammar_dict['状语从句 - {}'.format(sbar_node.word)] = True
                        elif isinstance(sbar_node, InternalTreebankNode) and sbar_node.label == "WHADVP":
                            whadvp_nodes = [_ for _ in sbar_node.children]
                            if isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].word in markers_of_adverbial_clause:
                                grammar_dict['状语从句 - {}'.format(whadvp_nodes[0].word)] = True
                        elif isinstance(sbar_node, InternalTreebankNode) and sbar_node.label == "ADVP":
                            advp_nodes = [_ for _ in sbar_node.children]
                            if isinstance(advp_nodes[0], LeafTreebankNode) and advp_nodes[0].word in markers_of_adverbial_clause:
                                grammar_dict['状语从句 - {}'.format(advp_nodes[0].word)] = True

                elif curr_node.label == "NP":
                    np_nodes = [_ for _ in curr_node.children]
                    for i, np_node in enumerate(np_nodes):
                        if isinstance(np_node, InternalTreebankNode) and np_node.label == "SBAR":
                            sbar_nodes = [_ for _ in np_node.children]
                            if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "S":
                                grammar_dict['定语从句 - that'] = True
                            for sbar_node in sbar_nodes:
                                if isinstance(sbar_node, InternalTreebankNode) and sbar_node.label == "WHNP":
                                    whnp_nodes = [_ for _ in sbar_node.children]
                                    for whnp_node in whnp_nodes:
                                        if isinstance(whnp_node, InternalTreebankNode) and whnp_node.label == "WHNP":
                                            whnp_nodes_1 = [_ for _ in whnp_node.children]
                                            if isinstance(whnp_nodes_1[0], LeafTreebankNode):
                                                if whnp_nodes_1[0].word in markers_of_attributive_clause:
                                                    if i >= 2 and "," in sentence.split(" "):
                                                        grammar_dict['定语从句 - 非限制性 - {}'.format(whnp_nodes_1[0].word)] = True
                                                    else:
                                                        grammar_dict['定语从句 - {}'.format(whnp_nodes_1[0].word)] = True
                                        elif isinstance(whnp_node, InternalTreebankNode) and whnp_node.label == "WHPP":
                                            whpp_nodes = [_ for _ in whnp_node.children]
                                            for whpp_node in whpp_nodes:
                                                if isinstance(whpp_node, InternalTreebankNode) and whpp_node.label == "WHNP":
                                                    whnp_nodes_1 = [_ for _ in whpp_node.children]
                                                    if isinstance(whnp_nodes_1[0], LeafTreebankNode) and whnp_nodes_1[0].word in markers_of_attributive_clause:
                                                        grammar_dict['定语从句 - {}'.format(whnp_nodes_1[0].word)] = True
                                        elif isinstance(whnp_nodes[0], LeafTreebankNode):
                                                if whnp_nodes[0].word in markers_of_attributive_clause:
                                                    if i >= 2 and "," in sentence.split(" "):
                                                        grammar_dict['定语从句 - 非限制性 - {}'.format(whnp_nodes[0].word)] = True
                                                    else:
                                                        grammar_dict['定语从句 - {}'.format(whnp_nodes[0].word)] = True
                                elif isinstance(sbar_node, InternalTreebankNode) and sbar_node.label == "WHPP":
                                    whpp_nodes = [_ for _ in sbar_node.children]
                                    for whpp_node in whpp_nodes:
                                        if isinstance(whpp_node, InternalTreebankNode) and whpp_node.label == "WHNP":
                                            whnp_nodes = [_ for _ in whpp_node.children]
                                            for whnp_node in whnp_nodes:
                                                if isinstance(whnp_node,
                                                              InternalTreebankNode) and whnp_node.label == "WHNP":
                                                    whnp_nodes_1 = [_ for _ in whnp_node.children]
                                                    if isinstance(whnp_nodes_1[0], LeafTreebankNode):
                                                        if whnp_nodes_1[0].word in markers_of_attributive_clause:
                                                            if i >= 2 and "," in sentence.split(" "):
                                                                grammar_dict['定语从句 - 非限制性 - {}'.format(
                                                                    whnp_nodes_1[0].word)] = True
                                                            else:
                                                                grammar_dict[
                                                                    '定语从句 - {}'.format(whnp_nodes_1[0].word)] = True
                                                elif isinstance(whnp_nodes[0], LeafTreebankNode) and whnp_nodes[0].word in markers_of_attributive_clause:
                                                    if i >= 2 and "," in sentence.split(" "):
                                                        grammar_dict[
                                                            '定语从句 - 非限制性 - {}'.format(whnp_nodes[0].word)] = True
                                                    else:
                                                        grammar_dict['定语从句 - {}'.format(whnp_nodes[0].word)] = True
                                elif isinstance(sbar_node, InternalTreebankNode) and sbar_node.label == "WHADVP":
                                    whadvp_nodes = [_ for _ in sbar_node.children]
                                    for whadvp_node in whadvp_nodes:
                                        if isinstance(whadvp_node, InternalTreebankNode) and whadvp_node.label == "WHNP":
                                            whnp_nodes = [_ for _ in whadvp_node.children]
                                            for whnp_node in whnp_nodes:
                                                if isinstance(whnp_node,
                                                              InternalTreebankNode) and whnp_node.label == "WHNP":
                                                    whnp_nodes_1 = [_ for _ in whnp_node.children]
                                                    if isinstance(whnp_nodes_1[0], LeafTreebankNode):
                                                        if whnp_nodes_1[0].word in markers_of_attributive_clause:
                                                            if i >= 2 and "," in sentence.split(" "):
                                                                grammar_dict['定语从句 - 非限制性 - {}'.format(
                                                                    whnp_nodes_1[0].word)] = True
                                                            else:
                                                                grammar_dict[
                                                                    '定语从句 - {}'.format(whnp_nodes_1[0].word)] = True
                                        elif isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].word in markers_of_attributive_clause:
                                            if i >= 2 and "," in sentence.split(" "):
                                                grammar_dict['定语从句 - 非限制性 - {}'.format(whadvp_nodes[0].word)] = True
                                            else:
                                                    grammar_dict['定语从句 - {}'.format(whadvp_nodes[0].word)] = True
                        elif isinstance(np_node, InternalTreebankNode) and np_node.label == "PP":
                            pp_nodes = [_ for _ in np_node.children]
                            for pp_node in pp_nodes:
                                if isinstance(pp_node, InternalTreebankNode) and pp_node.label == "SBAR":
                                    sbar_nodes = [_ for _ in pp_node.children]
                                    if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                        whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                        if isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].word in markers_of_attributive_clause:
                                            if i >= 2 and "," in sentence.split(" "):
                                                grammar_dict['定语从句 - 非限制性 - {}'.format(whadvp_nodes[0].word)] = True
                                            else:
                                                    grammar_dict['定语从句 - {}'.format(whadvp_nodes[0].word)] = True



                # we investigate verb tense in verb phrases
                elif curr_node.label == "VP":
                    curr_children = [_ for _ in curr_node.children]
                    if len(curr_children) > 1:
                        if isinstance(curr_children[0], LeafTreebankNode) and curr_children[0].tag in ["VB", "VBG", "RB", "VBD", "VBP", "VBZ"]:
                            if isinstance(curr_children[1], InternalTreebankNode) and curr_children[1].label == "VP":
                                vp_nodes = [_ for _ in curr_children[1].children]
                                if isinstance(vp_nodes, LeafTreebankNode) and vp_nodes.tag == "VBN":
                                    grammar_dict['被动语态'] = True
                    if isinstance(curr_children[0], LeafTreebankNode) and curr_children[0].tag == "TO":
                        grammar_dict['非谓语动词 - 动词不定式'] = True
                    if isinstance(curr_children[0], LeafTreebankNode) and curr_children[0].tag == "VBG":
                        grammar_dict['非谓语动词 - 动词ing'] = True
                    if isinstance(curr_children[0], LeafTreebankNode) and curr_children[0].tag == "VBN":
                        grammar_dict['非谓语动词 - 动词ed'] = True

                    for i, child in enumerate(curr_children):
                        if isinstance(child, InternalTreebankNode) and child.label == "PP":
                            pp_nodes = [_ for _ in child.children]
                            for pp_node in pp_nodes:
                                if isinstance(pp_node, InternalTreebankNode) and pp_node.label == "SBAR":
                                    sbar_nodes = [_ for _ in pp_node.children]
                                    if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[
                                        0].label == "S":
                                        grammar_dict['宾语从句 - that'] = True
                                    elif isinstance(sbar_nodes[0], LeafTreebankNode) and sbar_nodes[0].tag == "IN" and sbar_nodes[0].word in markers_of_object_clause:
                                        grammar_dict['宾语从句 - {}'.format(sbar_nodes[0].word)] = True
                                    elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[
                                        0].label == "WHNP" and sentence.split(' ')[0] != "There":
                                        whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                        if isinstance(whadvp_nodes[0], LeafTreebankNode):
                                            if whadvp_nodes[0].word in markers_of_object_clause:
                                                grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                                    elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[
                                        0].label == "WHADVP":
                                        whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                        if whadvp_nodes[0].word in markers_of_object_clause:
                                            grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True

                        elif isinstance(child, InternalTreebankNode) and child.label == "ADJP":
                            adjp_nodes = [_ for _ in child.children]
                            for adjp_node in adjp_nodes:
                                if isinstance(adjp_node, InternalTreebankNode) and adjp_node.label == "PP":
                                    pp_nodes = [_ for _ in adjp_node.children]
                                    for pp_node in pp_nodes:
                                        if isinstance(pp_node, InternalTreebankNode) and pp_node.label == "SBAR":
                                            sbar_nodes = [_ for _ in pp_node.children]
                                            if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "S":
                                                grammar_dict['宾语从句 - that'] = True
                                            elif isinstance(sbar_nodes[0], LeafTreebankNode) and sbar_nodes[0].tag == "IN" and sbar_nodes[0].word in markers_of_object_clause:
                                                grammar_dict['宾语从句 - {}'.format(sbar_nodes[0].word)] = True
                                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[
                                                0].label == "WHNP" and sentence.split(' ')[0] != "There":
                                                whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                                if isinstance(whadvp_nodes[0], LeafTreebankNode):
                                                    if whadvp_nodes[0].word in markers_of_object_clause:
                                                        grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[
                                                0].label == "WHADVP":
                                                whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                                if whadvp_nodes[0].word in markers_of_object_clause:
                                                    grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                                elif isinstance(adjp_node, InternalTreebankNode) and adjp_node.label == "SBAR":
                                    sbar_nodes = [_ for _ in adjp_node.children]
                                    if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "S":
                                        grammar_dict['宾语从句 - that'] = True
                                    elif isinstance(sbar_nodes[0], LeafTreebankNode) and sbar_nodes[0].tag == "IN" and sbar_nodes[0].word in markers_of_object_clause:
                                        grammar_dict['宾语从句 - {}'.format(sbar_nodes[0].word)] = True
                                    elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[
                                        0].label == "WHNP" and sentence.split(' ')[0] != "There":
                                        whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                        if isinstance(whadvp_nodes[0], LeafTreebankNode):
                                            if whadvp_nodes[0].word in markers_of_object_clause:
                                                grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                                    elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[
                                        0].label == "WHADVP":
                                        whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                        if whadvp_nodes[0].word in markers_of_object_clause:
                                            grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True


                        elif isinstance(child, InternalTreebankNode) and child.label == "SBAR":
                            sbar_nodes = [_ for _ in child.children]
                            if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "S":
                                grammar_dict['宾语从句 - that'] = True
                            elif sbar_nodes[1] and isinstance(sbar_nodes[1], LeafTreebankNode) and sbar_nodes[1].tag == "IN":
                                if isinstance(sbar_nodes[0], LeafTreebankNode) and sbar_nodes[0].tag == "IN":
                                    marker = ""
                                    for sbar_node in sbar_nodes:
                                        if isinstance(sbar_node, LeafTreebankNode) and sbar_node.tag == "IN":
                                            marker = marker + sbar_node.word + " "
                                    grammar_dict['状语从句 - {}'.format(marker)] = True
                            elif isinstance(sbar_nodes[0], LeafTreebankNode) and sbar_nodes[0].tag == "IN" and sbar_nodes[0].word in markers_of_object_clause:
                                if sbar_nodes[0].word == "if":
                                    if i > 1 and "asked" not in sentence.split(" ") and "ask" not in sentence.split(" ") and "tell" not in sentence.split(" ") and "told" not in sentence.split(" "):
                                        grammar_dict['状语从句 - if'] = True
                                    else:
                                        grammar_dict['宾语从句 - if'] = True
                                elif sbar_nodes[0].word == "where":
                                    if i > 1 and "asked" not in sentence.split(" ") and "ask" not in sentence.split(" ") and "tell" not in sentence.split(" ") and "told" not in sentence.split(" "):
                                        grammar_dict['状语从句 - where'] = True
                                    else:
                                        grammar_dict['宾语从句 - where'] = True
                                elif sbar_nodes[0].word == "when":
                                    if i > 1 and "asked" not in sentence.split(" ") and "ask" not in sentence.split(" ") and "tell" not in sentence.split(" ") and "told" not in sentence.split(" "):
                                        grammar_dict['状语从句 - when'] = True
                                    else:
                                        grammar_dict['宾语从句 - when'] = True
                                else:
                                    grammar_dict['宾语从句 - {}'.format(sbar_nodes[0].word)] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHNP" and sentence.split(' ')[0] != "There":
                                whnp_nodes = [_ for _ in sbar_nodes[0].children]
                                if isinstance(whnp_nodes[0], LeafTreebankNode) and whnp_nodes[0].word in markers_of_object_clause:
                                    if i < 2:
                                        grammar_dict['宾语从句 - {}'.format(whnp_nodes[0].word)] = True
                                    elif i >= 2 and "," in sentence.split(" "):
                                        grammar_dict['定语从句 - 非限制性 - {}'.format(whnp_nodes[0].word)] = True
                                    else:
                                        grammar_dict['宾语从句 - {}'.format(whnp_nodes[0].word)] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                if isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].word in markers_of_object_clause:
                                    if whadvp_nodes[0].word == "if":
                                        if i > 1 and "asked" not in sentence.split(" ") and "ask" not in sentence.split(
                                                " ") and "tell" not in sentence.split(
                                                " ") and "told" not in sentence.split(" "):
                                            grammar_dict['状语从句 - if'] = True
                                        else:
                                            grammar_dict['宾语从句 - if'] = True
                                    elif whadvp_nodes[0].word == "where":
                                        if i > 1 and "asked" not in sentence.split(" ") and "ask" not in sentence.split(
                                                " ") and "tell" not in sentence.split(
                                                " ") and "told" not in sentence.split(" "):
                                            grammar_dict['状语从句 - where'] = True
                                        else:
                                            grammar_dict['宾语从句 - where'] = True
                                    elif whadvp_nodes[0].word == "when":
                                        if i > 1 and "asked" not in sentence.split(" ") and "ask" not in sentence.split(
                                                " ") and "tell" not in sentence.split(
                                                " ") and "told" not in sentence.split(" "):
                                            grammar_dict['状语从句 - when'] = True
                                        else:
                                            grammar_dict['宾语从句 - when'] = True
                                    elif i < 2:
                                        grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                                    elif i >= 2 and "," in sentence.split(" "):
                                        grammar_dict['定语从句 - 非限制性 - {}'.format(whadvp_nodes[0].word)] = True
                                    else:
                                        grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True



                        elif isinstance(child, InternalTreebankNode) and child.label == "ADJP":
                            adjp_nodes = [_ for _ in child.children]
                            if isinstance(adjp_nodes[1], InternalTreebankNode) and adjp_nodes[1].label == "SBAR":
                                sbar_nodes = [_ for _ in adjp_nodes[1].children]
                                if sbar_nodes[0].word in markers_of_object_clause:
                                    grammar_dict['宾语从句 - {}'.format(sbar_nodes[0].word)] = True
                        elif isinstance(child, InternalTreebankNode) and child.label == "ADVP":
                            advp_nodes = [_ for _ in child.children]
                            marker = ""
                            for leaf in advp_nodes[0].leaves():
                                if leaf.tag == "RB":
                                    marker = marker + leaf.word + " "
                            for n, advp_node in enumerate(advp_nodes):
                                if isinstance(advp_node, InternalTreebankNode) and advp_node.label == "SBAR":
                                    sbar_nodes = [_ for _ in advp_node.children]
                                    if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                        whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                        if isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].word in markers_of_object_clause:
                                            if n < 2:
                                                grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                                            elif i >= 2 and "," in sentence.split(" "):
                                                grammar_dict['定语从句 - 非限制性 - {}'.format(whadvp_nodes[0].word)] = True
                                            else:
                                                grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                                    elif isinstance(sbar_nodes[0], LeafTreebankNode) and sbar_nodes[0].tag == "IN":
                                        grammar_dict['状语从句 - {}'.format(marker + sbar_nodes[0].word)] = True

                elif curr_node.label == "S":
                    s_nodes = [_ for _ in curr_node.children]
                    for curr_node in s_nodes:
                        if isinstance(curr_node, LeafTreebankNode):
                            if curr_node.word == "for":
                                grammar_dict['状语从句 - for'] = True
                            elif curr_node.word == "or":
                                grammar_dict['状语从句 - or'] = True
                        elif isinstance(curr_node, InternalTreebankNode):
                            if curr_node.label == "VP":
                                curr_children = [_ for _ in curr_node.children]

                                for temp_node in curr_children:
                                    if isinstance(temp_node, LeafTreebankNode):
                                        if temp_node.word in markers_of_future_tense:
                                            grammar_dict['一般将来时'] = True
                                        elif temp_node.tag == "VB":
                                            grammar_dict['一般现在时'] = True
                                        elif temp_node.tag == "VBP":
                                            if temp_node.word in markers_of_present_continuous_tense:
                                                count = 0
                                                for leaf in curr_node.leaves():
                                                    if leaf.tag == "VBG":
                                                        count += 1
                                                if count > 0:
                                                    grammar_dict['现在进行时'] = True
                                                else:
                                                    grammar_dict['一般现在时'] = True
                                            elif temp_node.word in markers_of_present_perfect_tense:
                                                count = 0
                                                for leaf in curr_node.leaves():
                                                    if leaf.tag == "VBN":
                                                        count += 1
                                                if count > 0:
                                                    grammar_dict['现在完成时'] = True
                                                else:
                                                    grammar_dict['一般现在时'] = True
                                            else:
                                                grammar_dict['一般现在时'] = True

                                        elif temp_node.tag == "VBD":
                                            if temp_node.word in markers_of_past_continuous_tense:
                                                count = 0
                                                for leaf in curr_node.leaves():
                                                    if leaf.tag == "VBG":
                                                        count += 1
                                                if count > 0:
                                                    grammar_dict['过去进行时'] = True
                                            elif temp_node.word in markers_of_past_perfect_tense:
                                                count = 0
                                                for leaf in curr_node.leaves():
                                                    if leaf.tag == "VBN":
                                                        count += 1
                                                if count > 0:
                                                    grammar_dict['过去完成时'] = True
                                            else:
                                                grammar_dict['一般过去时'] = True

                                        elif temp_node.tag == "VBZ":
                                            if temp_node.word in markers_of_present_continuous_tense:
                                                count = 0
                                                for leaf in curr_node.leaves():
                                                    if leaf.tag == "VBG":
                                                        count += 1
                                                if count > 0:
                                                    grammar_dict['现在进行时'] = True
                                                else:
                                                    grammar_dict['一般现在时'] = True
                                            elif temp_node.word in markers_of_present_perfect_tense:
                                                count = 0
                                                for leaf in curr_node.leaves():
                                                    if leaf.tag == "VBN":
                                                        count += 1
                                                if count > 0:
                                                    grammar_dict['现在完成时'] = True
                                                else:
                                                    grammar_dict['一般现在时'] = True
                                            else:
                                                grammar_dict['一般现在时'] = True

                                    elif isinstance(temp_node, InternalTreebankNode):
                                        node_children = [_ for _ in temp_node.children]
                                        node_child = node_children[0]
                                        if isinstance(node_child, InternalTreebankNode) and node_child.label == "VP":
                                            new_node = [_ for _ in node_child.children][0]
                                            if isinstance(new_node, LeafTreebankNode):
                                                if new_node.word in markers_of_future_tense:
                                                    grammar_dict['一般将来时'] = True
                                                elif new_node.tag == "VB":
                                                    grammar_dict['一般现在时'] = True
                                                elif new_node.tag == "VBP":
                                                    if new_node.word in markers_of_present_continuous_tense:
                                                        count = 0
                                                        for leaf in curr_node.leaves():
                                                            if leaf.tag == "VBG":
                                                                count += 1
                                                        if count > 0:
                                                            grammar_dict['现在进行时'] = True
                                                        else:
                                                            grammar_dict['一般现在时'] = True
                                                    elif new_node.word in markers_of_present_perfect_tense:
                                                        count = 0
                                                        for leaf in curr_node.leaves():
                                                            if leaf.tag == "VBN":
                                                                count += 1
                                                        if count > 0:
                                                            grammar_dict['现在完成时'] = True
                                                        else:
                                                            grammar_dict['一般现在时'] = True
                                                    else:
                                                        grammar_dict['一般现在时'] = True
                                                elif new_node.tag == "VBD":
                                                    if new_node.word in markers_of_past_continuous_tense:
                                                        count = 0
                                                        for leaf in curr_node.leaves():
                                                            if leaf.tag == "VBG":
                                                                count += 1
                                                        if count > 0:
                                                            grammar_dict['过去进行时'] = True
                                                        else:
                                                            grammar_dict['一般过去时 '] = True
                                                    elif new_node.word in markers_of_past_perfect_tense:
                                                        count = 0
                                                        for leaf in curr_node.leaves():
                                                            if leaf.tag == "VBN":
                                                                count += 1
                                                        if count > 0:
                                                            grammar_dict['过去完成时'] = True
                                                        else:
                                                            grammar_dict['一般过去时'] = True
                                                elif new_node.tag == "VBZ":
                                                    if new_node.word in markers_of_present_perfect_tense:
                                                        count = 0
                                                        for leaf in curr_node.leaves():
                                                            if leaf.tag == "VBN":
                                                                count += 1
                                                        if count > 0:
                                                            grammar_dict['现在完成时'] = True
                                                        else:
                                                            grammar_dict['一般现在时'] = True

            
                else:
                    continue



            grammars = []
            for key in grammar_dict:
                if grammar_dict[key]:
                    grammars.append(key)
            for i in ['when', 'where']:
                if '定语从句 - 非限制性 - {}'.format(i) in grammars:
                    grammars.remove('状语从句 - {}'.format(i))
                elif '定语从句 - {}'.format(i) in grammars:
                    grammars.remove('状语从句 - {}'.format(i))
            return grammars, sentence



        for sente in parse_list:
            # with open('treebank.txt','a+') as ff:
            #     ff.write(sente)
            #     ff.write('\n')
            example_tree = tree_from_str(sente)
            result = grammar(example_tree)
            print(result)
            with open('output.txt','a+') as nf:
                nf.write(str(result))
                nf.write('\n')





