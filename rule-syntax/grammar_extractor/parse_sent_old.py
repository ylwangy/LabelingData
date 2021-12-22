import benepar, spacy
from trees import load_trees, tree_from_str, InternalTreebankNode, LeafTreebankNode
import re

#现在完成
markers_of_present_perfect_tense = [
    "has",
    "have",
    "'ve",
]
#过去完成
markers_of_past_perfect_tense = [
    "had",
    "'d",
]
#现在进行
markers_of_present_continuous_tense = [
    "is",
    "am",
    "'m",
    "are",
    "'re",
]
#过去进行
markers_of_past_continuous_tense = [
    "was",
    "were",
]
#未来时
markers_of_future_tense = [
    "will",
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
    "that"
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
    "unless",
    "wherever",
    "after",
    "before",
    "while",
    "because",
    "since",
    "as",
    "so",
    "than",
    "whereas",
    "though",
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
    "seemed"
    "seems",
    "appeared",
    "gets"
    "got",
    "became",
    "turn",
    "turned",
    "grow",
    "grew",
    "come",
    "came"
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
                    grammar_dict['一般疑问句'] = True
                    sq_nodes = [_ for _ in curr_node.children]
                    count = 0
                    for leaf in curr_node.leaves():
                        if leaf.tag == "VBG":
                            count += 1
                    if isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag in ["VBP", "VBZ"]:
                        if count > 0:
                            grammar_dict['现在进行时'] = True
                        else:
                            grammar_dict['一般现在时'] = True
                    elif isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag == "VBD":
                        if count > 0:
                            grammar_dict['过去进行时'] = True
                        else:
                            grammar_dict['一般过去时'] = True
                elif curr_node.label == "S":
                    s_nodes = [_ for _ in curr_node.children]
                    if s_nodes.label == "SBARQ":
                        sbarq_nodes = [_ for _ in s_nodes.children]
                        if isinstance(sbarq_nodes, InternalTreebankNode) and sbarq_nodes.label == "WHADVP":
                            if isinstance(sbarq_nodes[0], LeafTreebankNode) and sbarq_nodes[0].tag in ["WRB", "WP"]:
                                grammar_dict['特殊疑问句 - {}'.format(sbarq_nodes[0].word)] = True
                                if isinstance(sbarq_nodes[1], InternalTreebankNode) and sbarq_nodes[1].label == "SQ":
                                    sq_nodes = [_ for _ in sbarq_nodes.children]
                                    if isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag == "VBD":
                                        grammar_dict['一般过去时'] = True
                                    elif isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag == "VBP":
                                        grammar_dict['一般现在时'] = True
                                    elif isinstance(sq_nodes[0], LeafTreebankNode) and sq_nodes[0].tag == "MD":
                                        grammar_dict['一般将来时'] = True
                    elif curr_node.label == "VP":
                        curr_children = [_ for _ in curr_node.children]

                        for temp_node in curr_children:

                            if isinstance(temp_node, LeafTreebankNode):
                                if temp_node.word in markers_of_future_tense:
                                    grammar_dict['一般将来时'] = True
                                elif temp_node.tag == "MD":
                                    grammar_dict['一般将来时'] = True
                                elif temp_node.tag == "VB":
                                    grammar_dict['一般现在时'] = True
                                elif temp_node.tag == "VBP":
                                    try:
                                        if temp_node.word in markers_of_present_continuous_tense \
                                                and isinstance(curr_children[1], InternalTreebankNode) \
                                                and curr_children[1].label == "VP":
                                            grammar_dict['现在进行时'] = True
                                        elif temp_node.word in markers_of_present_continuous_tense \
                                                and isinstance(curr_children[2], InternalTreebankNode) \
                                                and curr_children[2].label == "VP":
                                            grammar_dict['现在进行时'] = True
                                        elif temp_node.word in markers_of_present_perfect_tense \
                                                and isinstance(curr_children[1], InternalTreebankNode) \
                                                and curr_children[1].label == "VP":
                                            grammar_dict['现在完成时'] = True
                                        elif temp_node.word in markers_of_present_perfect_tense \
                                                and isinstance(curr_children[2], InternalTreebankNode) \
                                                and curr_children[2].label == "VP":
                                            grammar_dict['现在完成时'] = True
                                        else:
                                            grammar_dict['一般现在时'] = True
                                    except:
                                        grammar_dict['一般现在时'] = True
                                elif temp_node.tag == "VBD":
                                    try:
                                        if temp_node.word in markers_of_past_continuous_tense \
                                                and isinstance(curr_children[1], InternalTreebankNode) \
                                                and curr_children[1].label == "VP":
                                            vp_nodes = [_ for _ in curr_children[1].children]
                                            if vp_nodes[0] == "VBG":
                                                grammar_dict['过去进行时'] = True

                                        elif temp_node.word in markers_of_past_continuous_tense \
                                                and isinstance(curr_children[2], InternalTreebankNode) \
                                                and curr_children[2].label == "VP":
                                            vp_nodes = [_ for _ in curr_children[1].children]
                                            if vp_nodes[0] == "VBG":
                                                grammar_dict['过去进行时'] = True
                                        elif temp_node.word in markers_of_past_perfect_tense \
                                                and isinstance(curr_children[1], InternalTreebankNode) \
                                                and curr_children[1].label == "VP":
                                            vp_nodes = [_ for _ in curr_children[1].children]
                                            if vp_nodes[0] == "VBG":
                                                grammar_dict['过去进行时'] = True
                                        elif temp_node.word in markers_of_past_perfect_tense \
                                                and isinstance(curr_children[2], InternalTreebankNode) \
                                                and curr_children[2].label == "VP":
                                            grammar_dict['过去完成时'] = True
                                        else:
                                            grammar_dict['一般过去时'] = True
                                    except:
                                        grammar_dict['一般过去时'] = True
                                elif temp_node.tag == "VBZ":
                                    count = 0
                                    for leaf in curr_node.leaves():
                                        if leaf.tag == "VBG":
                                            count += 1
                                    if temp_node.word in markers_of_present_continuous_tense and count > 0:
                                        grammar_dict['现在进行时'] = True
                                    # elif temp_node.word in markers_of_present_perfect_tense
                                    else:
                                        grammar_dict['一般现在时'] = True

                # elif curr_node.label == "VBP":
                #     grammar_dict['一般现在时'] = True


                # Noun phrases are linked to 定语从句
                elif curr_node.label == "NP":
                    curr_children = [_ for _ in curr_node.children]
                    try:
                        if isinstance(curr_children[1], InternalTreebankNode) and curr_children[1].label == "SBAR":
                            sbar_nodes = [_ for _ in curr_children[1].children]
                            if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "S":
                                grammar_dict['定语从句 - that'] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHNP":
                                whnp_nodes = [_ for _ in sbar_nodes[0].children]
                                if whnp_nodes[0].word in markers_of_attributive_clause:
                                    grammar_dict['定语从句 - {}'.format(whnp_nodes[0].word)] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHPP":
                                whpp_nodes = [_ for _ in sbar_nodes[0].children]
                                if isinstance(whpp_nodes[1], InternalTreebankNode) and whpp_nodes[1].label == "WHNP":
                                    whnp_nodes = [_ for _ in whpp_nodes[1].children]
                                    if whnp_nodes[0].word in markers_of_attributive_clause:
                                        grammar_dict['定语从句 - {}'.format(whnp_nodes[0].word)] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                whnp_nodes = [_ for _ in sbar_nodes[0].children]
                                if whnp_nodes[0].word in markers_of_attributive_clause:
                                    grammar_dict['定语从句 - {}'.format(whnp_nodes[0].word)] = True
                        elif isinstance(curr_children[2], InternalTreebankNode) and curr_children[2].label == "SBAR":
                            sbar_nodes = [_ for _ in curr_children[2].children]
                            if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "S":
                                grammar_dict['定语从句 - 非限制性 - that'] = True

                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHNP":
                                whnp_nodes = [_ for _ in sbar_nodes[0].children]
                                if whnp_nodes[0].word in markers_of_attributive_clause:
                                    grammar_dict['定语从句 - 非限制性 - {}'.format(whnp_nodes[0].word)] = True
                                for whnp_node in whnp_nodes:
                                    if isinstance(whnp_node, InternalTreebankNode) and whnp_node.label == "WHPP":
                                        whpp_nodes = [_ for _ in whnp_node.children]
                                        for whpp_node in whpp_nodes:
                                            if isinstance(whpp_node,
                                                          InternalTreebankNode) and whpp_node.label == "WHNP":
                                                whnp_nodes_1 = [_ for _ in whpp_node.children]
                                                if isinstance(whnp_nodes_1[0], LeafTreebankNode) and whnp_nodes_1[
                                                    0].tag == "WDT":
                                                    grammar_dict[
                                                        '定语从句 - {}'.format(whnp_nodes_1[0].word)] = True
                                                elif isinstance(whnp_nodes_1[0], LeafTreebankNode) and whnp_nodes_1[
                                                    0].tag == "WP":
                                                    grammar_dict[
                                                        '定语从句 - {}'.format(whnp_nodes_1[0].word)] = True

                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHPP":
                                whpp_nodes = [_ for _ in sbar_nodes[0].children]
                                if isinstance(whpp_nodes[1], InternalTreebankNode) and whpp_nodes[1].label == "WHNP":
                                    whnp_nodes = [_ for _ in whpp_nodes[1].children]
                                    if whnp_nodes[0].word in markers_of_attributive_clause:
                                        grammar_dict['定语从句 - 非限制性 - {}'.format(whnp_nodes[0].word)] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                whnp_nodes = [_ for _ in sbar_nodes[0].children]
                                if whnp_nodes[0].word in markers_of_attributive_clause:
                                    grammar_dict['定语从句 非限制性 - {}'.format(whnp_nodes[0].word)] = True
                    except:
                        continue


                # we investigate verb tense in verb phrases
                elif curr_node.label == "VP":
                    curr_children = [_ for _ in curr_node.children]

                    for temp_node in curr_children:

                        if isinstance(temp_node, LeafTreebankNode):
                            if temp_node.word in markers_of_future_tense:
                                grammar_dict['一般将来时'] = True
                            elif temp_node.tag == "MD":
                                grammar_dict['一般将来时'] = True
                            elif temp_node.tag == "VB":
                                grammar_dict['一般现在时'] = True
                            elif temp_node.tag == "VBP":
                                try:
                                    if temp_node.word in markers_of_present_continuous_tense \
                                            and isinstance(curr_children[1], InternalTreebankNode) \
                                            and curr_children[1].label == "VP":
                                        grammar_dict['现在进行时'] = True
                                    elif temp_node.word in markers_of_present_continuous_tense \
                                            and isinstance(curr_children[2], InternalTreebankNode) \
                                            and curr_children[2].label == "VP":
                                        grammar_dict['现在进行时'] = True
                                    elif temp_node.word in markers_of_present_perfect_tense \
                                            and isinstance(curr_children[1], InternalTreebankNode) \
                                            and curr_children[1].label == "VP":
                                        grammar_dict['现在完成时'] = True
                                    elif temp_node.word in markers_of_present_perfect_tense \
                                            and isinstance(curr_children[2], InternalTreebankNode) \
                                            and curr_children[2].label == "VP":
                                        grammar_dict['现在完成时'] = True
                                    else:
                                        grammar_dict['一般现在时'] = True
                                except:
                                    grammar_dict['一般现在时'] = True
                            elif temp_node.tag == "VBD":
                                try:
                                    if temp_node.word in markers_of_past_continuous_tense \
                                            and isinstance(curr_children[1], InternalTreebankNode) \
                                            and curr_children[1].label == "VP":
                                        vp_nodes = [_ for _ in curr_children[1].children]
                                        if vp_nodes[0] == "VBG":
                                            grammar_dict['过去进行时'] = True

                                    elif temp_node.word in markers_of_past_continuous_tense \
                                            and isinstance(curr_children[2], InternalTreebankNode) \
                                            and curr_children[2].label == "VP":
                                        vp_nodes = [_ for _ in curr_children[1].children]
                                        if vp_nodes[0] == "VBG":
                                            grammar_dict['过去进行时'] = True
                                    elif temp_node.word in markers_of_past_perfect_tense \
                                            and isinstance(curr_children[1], InternalTreebankNode) \
                                            and curr_children[1].label == "VP":
                                        vp_nodes = [_ for _ in curr_children[1].children]
                                        if vp_nodes[0] == "VBG":
                                            grammar_dict['过去进行时'] = True
                                    elif temp_node.word in markers_of_past_perfect_tense \
                                            and isinstance(curr_children[2], InternalTreebankNode) \
                                            and curr_children[2].label == "VP":
                                        grammar_dict['过去完成时'] = True
                                    else:
                                        grammar_dict['一般过去时'] = True
                                except:
                                    grammar_dict['一般过去时'] = True
                            elif temp_node.tag == "VBZ":
                                count = 0
                                for leaf in curr_node.leaves():
                                    if leaf.tag == "VBG":
                                        count += 1
                                if temp_node.word in markers_of_present_continuous_tense and count > 0:
                                    grammar_dict['现在进行时'] = True
                                # elif temp_node.word in markers_of_present_perfect_tense
                                else:
                                    grammar_dict['一般现在时'] = True



                                # elif temp_node.word in markers_of_present_perfect_tense \
                                #         and isinstance(curr_children[1], InternalTreebankNode) \
                                #         and curr_children[1].label == "VP":
                                #     grammar_dict['现在完成时'] = True
                                #
                                # elif temp_node.word in markers_of_present_perfect_tense \
                                #         and isinstance(curr_children[2], InternalTreebankNode) \
                                #         and curr_children[2].label == "VP":
                                #     grammar_dict['现在完成时'] = True
                                # else:
                                #     grammar_dict['一般现在时'] = True



                        elif isinstance(temp_node, InternalTreebankNode):
                            if temp_node.label == "SBAR":
                                sbar_nodes = [_ for _ in temp_node.children]
                                if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHNP":
                                    whnp_nodes = [_ for _ in sbar_nodes[0].children]
                                    if isinstance(whnp_nodes[0], LeafTreebankNode) and whnp_nodes[0].word in markers_of_attributive_clause:
                                        grammar_dict['定语从句 - {}'.format(whnp_nodes[0].word)] = True
                                elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                    whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                    if isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].word in markers_of_attributive_clause:
                                        grammar_dict['定语从句 - {}'.format(whadvp_nodes[0].word)] = True
                            elif temp_node.label == "NP":
                                np_nodes = [_ for _ in temp_node.children]
                                for np_node in np_nodes:
                                    if isinstance(np_node, InternalTreebankNode) and np_node.label == "PP":
                                        pp_nodes = [_ for _ in np_node.children]
                                        for pp_node in pp_nodes:
                                            if isinstance(pp_node, InternalTreebankNode) and pp_node.label == "SBAR":
                                                sbar_nodes = [_ for _ in pp_node.children]
                                                if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                                    whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                                    if isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].word in markers_of_attributive_clause:
                                                        grammar_dict['定语从句 - {}'.format(whadvp_nodes[0].word)] = True
                                    elif isinstance(np_node, InternalTreebankNode) and np_node.label == "SBAR":
                                        sbar_nodes = [_ for _ in np_node.children]
                                        if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[
                                            0].label == "WHNP":
                                            whnp_nodes = [_ for _ in sbar_nodes[0].children]
                                            for whnp_node in whnp_nodes:
                                                if isinstance(whnp_node,
                                                              InternalTreebankNode) and whnp_node.label == "WHPP":
                                                    whpp_nodes = [_ for _ in whnp_node.children]
                                                    for whpp_node in whpp_nodes:
                                                        if isinstance(whpp_node,
                                                                      InternalTreebankNode) and whpp_node.label == "WHNP":
                                                            whnp_nodes_1 = [_ for _ in whpp_node.children]
                                                            if isinstance(whnp_nodes_1[0], LeafTreebankNode) and \
                                                                    whnp_nodes_1[
                                                                        0].tag == "WDT":
                                                                grammar_dict[
                                                                    '定语从句 - {}'.format(
                                                                        whnp_nodes_1[0].word)] = True
                                                            elif isinstance(whnp_nodes_1[0], LeafTreebankNode) and \
                                                                    whnp_nodes_1[
                                                                        0].tag == "WP":
                                                                grammar_dict[
                                                                    '定语从句 - {}'.format(
                                                                    whnp_nodes_1[0].word)] = True
                            elif temp_node.label == "ADVP":
                                advp_nodes = [_ for _ in temp_node.children]
                                for advp_node in advp_nodes:
                                    if isinstance(advp_node, InternalTreebankNode) and advp_node.label == "SBAR":
                                        sbar_nodes = [_ for _ in advp_node.children]
                                        if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                            whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                            if isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].tag == "WRB":
                                                grammar_dict['定语从句 - 非限制性 - {}'.format(whadvp_nodes[0].word)] = True



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
                                        try:
                                            if new_node.word in markers_of_present_continuous_tense \
                                                    and isinstance(curr_children[1], InternalTreebankNode) \
                                                    and curr_children[1].label == "VP":
                                                grammar_dict['现在进行时'] = True
                                            elif new_node.word in markers_of_present_continuous_tense \
                                                    and isinstance(curr_children[2], InternalTreebankNode) \
                                                    and curr_children[2].label == "VP":
                                                grammar_dict['现在进行时'] = True
                                            elif new_node.word in markers_of_present_perfect_tense \
                                                    and isinstance(curr_children[1], InternalTreebankNode) \
                                                    and curr_children[1].label == "VP":
                                                grammar_dict['现在完成时'] = True
                                            elif new_node.word in markers_of_present_perfect_tense \
                                                    and isinstance(curr_children[2], InternalTreebankNode) \
                                                    and curr_children[2].label == "VP":
                                                grammar_dict['现在完成时'] = True
                                        except:
                                            grammar_dict['一般现在时'] = True
                                    elif new_node.tag == "VBD":
                                        try:
                                            if new_node.word in markers_of_past_continuous_tense \
                                                    and isinstance(curr_children[1], InternalTreebankNode) \
                                                    and curr_children[1].label == "VP":
                                                vp_nodes = [_ for _ in curr_children[1].children]
                                                if vp_nodes[0] == "VBG":
                                                    grammar_dict['过去进行时'] = True
                                            elif new_node.word in markers_of_past_continuous_tense \
                                                    and isinstance(curr_children[2], InternalTreebankNode) \
                                                    and curr_children[2].label == "VP":
                                                vp_nodes = [_ for _ in curr_children[1].children]
                                                if vp_nodes[0] == "VBG":
                                                    grammar_dict['过去进行时'] = True
                                            elif new_node.word in markers_of_past_perfect_tense \
                                                    and isinstance(curr_children[1], InternalTreebankNode) \
                                                    and curr_children[1].label == "VP":
                                                grammar_dict['过去完成时'] = True
                                            elif new_node.word in markers_of_past_perfect_tense \
                                                    and isinstance(curr_children[2], InternalTreebankNode) \
                                                    and curr_children[2].label == "VP":
                                                grammar_dict['过去完成时'] = True
                                            else:
                                                grammar_dict['一般过去时'] = True
                                        except:
                                            grammar_dict['一般过去时'] = True
                                    elif new_node.tag == "VBZ":
                                        try:
                                            if new_node.word in markers_of_present_perfect_tense \
                                                    and isinstance(curr_children[1], InternalTreebankNode) \
                                                    and curr_children[1].label == "VP":
                                                grammar_dict['现在完成时'] = True
                                            elif new_node.word in markers_of_present_perfect_tense \
                                                    and isinstance(curr_children[2], InternalTreebankNode) \
                                                    and curr_children[2].label == "VP":
                                                grammar_dict['现在完成时'] = True
                                            else:
                                                grammar_dict['一般现在时'] = True
                                        except:
                                            grammar_dict['一般现在时'] = True

                    for child in curr_children:
                        if isinstance(child, InternalTreebankNode) and child.label == "PP":
                            pp_nodes = [_ for _ in child.children]
                            for pp_node in pp_nodes:
                                if isinstance(pp_node, InternalTreebankNode) and pp_node.label == "NP":
                                    np_nodes = [_ for _ in pp_node.children]
                                    for np_node in np_nodes:
                                        if isinstance(np_node, InternalTreebankNode) and np_node.label == "SBAR":
                                            sbar_nodes = [_ for _ in np_node.children]
                                            if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                                whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                                if isinstance(whadvp_nodes[0], LeafTreebankNode) and whadvp_nodes[0].tag == "WRB":
                                                    grammar_dict['定语从句 - {}'.format(whadvp_nodes[0].word)] = True
                                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHNP":
                                                whnp_nodes = [_ for _ in sbar_nodes[0].children]
                                                for whnp_node in whnp_nodes:
                                                    if isinstance(whnp_node, InternalTreebankNode) and whnp_node.label == "WHPP":
                                                        whpp_nodes = [_ for _ in whnp_node.children]
                                                        for whpp_node in whpp_nodes:
                                                            if isinstance(whpp_node, InternalTreebankNode) and whpp_node.label == "WHNP":
                                                                whnp_nodes_1 = [_ for _ in whpp_node.children]
                                                                if isinstance(whnp_nodes_1[0], LeafTreebankNode) and whnp_nodes_1[0].tag == "WDT":
                                                                    grammar_dict['定语从句 - {}'.format(whnp_nodes_1[0].word)] = True
                                                                elif isinstance(whnp_nodes_1[0], LeafTreebankNode) and whnp_nodes_1[0].tag == "WP":
                                                                    grammar_dict['定语从句 - {}'.format(whnp_nodes_1[0].word)] = True
                                            else:
                                                grammar_dict['定语从句 - 非限制性 - which'] = True
                                elif isinstance(pp_node, InternalTreebankNode) and pp_node.label == "S":
                                    grammar_dict['定语从句 - 非限制性 - which'] = True


                    try:
                        if isinstance(curr_children[1], InternalTreebankNode) and curr_children[1].label == "SBAR":
                            sbar_nodes = [_ for _ in curr_children[1].children]
                            if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "S":
                                grammar_dict['宾语从句 - that'] = True
                            elif isinstance(sbar_nodes[0], LeafTreebankNode) and sbar_nodes[0].tag == "IN":
                                grammar_dict['宾语从句 - {}'.format(sbar_nodes[0].word)] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHNP" and sentence.split(' ')[0] != "There":
                                whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                if whadvp_nodes[0].word in markers_of_object_clause:
                                    grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                if whadvp_nodes[0].word in markers_of_object_clause:
                                    grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                        elif isinstance(curr_children[1], InternalTreebankNode) and curr_children[1].label == "ADJP":
                            adjp_nodes = [_ for _ in curr_children[1].children]
                            if isinstance(adjp_nodes[1], InternalTreebankNode) and adjp_nodes[1].label == "SBAR":
                                sbar_nodes = [_ for _ in adjp_nodes[1].children]
                                if sbar_nodes[0].word in markers_of_object_clause:
                                    grammar_dict['宾语从句 - {}'.format(sbar_nodes[0].word)] = True
                        elif isinstance(curr_children[1], LeafTreebankNode) and curr_children[1].tag == ",":
                            break
                        elif isinstance(curr_children[2], InternalTreebankNode) and curr_children[2].label == "SBAR":
                            sbar_nodes = [_ for _ in curr_children[2].children]
                            if isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "S":
                                grammar_dict['宾语从句 - that'] = True
                            elif isinstance(sbar_nodes[0], LeafTreebankNode) and sbar_nodes[0].tag == "IN":
                                grammar_dict['宾语从句 - {}'.format(sbar_nodes[0].word)] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHNP" and sentence.split(' ')[0] != "There":
                                whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                if whadvp_nodes[0].word in markers_of_object_clause:
                                    grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True
                            elif isinstance(sbar_nodes[0], InternalTreebankNode) and sbar_nodes[0].label == "WHADVP":
                                whadvp_nodes = [_ for _ in sbar_nodes[0].children]
                                if whadvp_nodes[0].word in markers_of_object_clause:
                                    grammar_dict['宾语从句 - {}'.format(whadvp_nodes[0].word)] = True

                    except:
                        continue


                        # elif isinstance(temp_node, InternalTreebankNode):
                        #     try:
                elif curr_node.label == "SBAR":
                    curr_children = [_ for _ in curr_node.children]
                    try:
                        child = curr_children[0]
                        if isinstance(child, LeafTreebankNode) and child.tag == "IN" and child.word in markers_of_adverbial_clause:
                            grammar_dict['状语从句 - {}'.format(child.word)] = True
                    except:
                        continue
                else:
                    continue
            grammars = []
            for key in grammar_dict:
                if grammar_dict[key]:
                    grammars.append(key)
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





