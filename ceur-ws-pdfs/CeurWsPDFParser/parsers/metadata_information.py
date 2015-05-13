#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Alexander'
import os, re
import PdfExtractionLib as pdf
import standfordParserWorker
def test_metadata():


    f_name = os.path.join(os.path.dirname(__file__), "pdfs", "Vol-315-paper3.pdf")

    dict_data = pdf.get_html_and_txt(f_name,  update_files = True)#, add_files = False, update_files = True)

    result_data = get_information(dict_data)

    a = 1
def get_information(dict_data):
    def prettify_bibliography(input_array):
        try:
            outpt = u""
            if not len(input_array):
                return outpt
            #input_data = u"{newline}".join([pdf.html2text(el[1]) for el in input_array[0]])
            input_data = u"{newline}".join([re.sub(r"<.*?>", " ", el[1].replace("<br>", "{newline}")) for el in input_array[0]])
            temp_array = get_bibliography_array(input_data)
            outpt = u"\n".join(temp_array)
        except Exception as err:
            print("prettify_bibliography -> {0}".format(err))
        finally:
            return outpt
    try:
        outpt_data = {
            # "title": None,
            # "authors": [],
            # "cited_works": [],
            # "grants": [],
            # "funding_agencies": [],
            # "EU_projects": [],
            # "new_ontologies": [],
            # "related_ontologies": []
        }

        article_parts = get_article_parts(dict_data.get("html", ""))
        outpt_data["header_part"] = u"\n".join([el[1] for el in article_parts[0]])
        outpt_data["abstract_part"] =  re.sub(r"<.*?>", "", article_parts[1])
        outpt_data["acknowledgement"] = re.sub(r"<.*?>", "", article_parts[2])
        outpt_data["bibliography"] = prettify_bibliography(article_parts[3])
        title, authors = get_inf_from_header(article_parts[0])
        related_ontos, new_ontologies_out = get_inf_about_ontologies(article_parts[1])
        cited_works = get_cited_works(article_parts[3])
        grants, funding_agencies, eu_projects = get_grants_and_finding_agencies(article_parts[2])
        if title != "":
            outpt_data["title"] = title
        if len(authors):
            outpt_data["authors"] = authors
        if len(cited_works):
            outpt_data["cited_works"] = cited_works
        if len(grants):
            outpt_data["grants"] = grants
        if len(funding_agencies):
            outpt_data["funding_agencies"] = funding_agencies
        if len(eu_projects):
            outpt_data["EU_projects"] = eu_projects
        if len(related_ontos):
            outpt_data["related_ontologies"] = related_ontos
        if len(new_ontologies_out):
            outpt_data["new_ontologies"] = new_ontologies_out
    except Exception as err:
        print("get_information -> {0}".format(err))
    finally:
        return outpt_data
def get_inf_about_ontologies(abstract):
    try:
        related_ontos = []
        new_ontologies_out = []

        stop_words = standfordParserWorker.read_stop_words()
        existontos = standfordParserWorker.read_existonto()

        text = re.sub(r"\s+", " ", re.sub(r"<.*?>", " ", abstract, re.U), re.U)
        text = re.sub(r"\(cid\:\d+\)", "", text)
        text = text.replace(r"\\", '"')

        if not len(text):
            return related_ontos

        tokens = [el.strip() for el in text.split(" ") if el.strip() != ""]
        if tokens[0].lower().find('abstract') != -1:
            tokens.pop(0)
            if not tokens[0][0].isalpha():
                tokens.pop(0)

        sentences = []
        cur_sentence = []
        for i in range(len(tokens)):
            #prev_word = else_tokens[i-1]
            cur_word = tokens[i]
            next_word = ""
            if i+1 < len(tokens):
                next_word = tokens[i+1]

            if len(cur_sentence) and cur_sentence[-1].endswith("-") and cur_sentence[-1] != '-':
                cur_sentence[-1] = u"{0}{1}".format(cur_sentence[-1][:-1], cur_word)
            else:
                cur_sentence.append(cur_word)
            if re.search(r"[.?!]$", cur_word, re.U) and cur_word.find("U.S.") == -1:
                if next_word == "":
                    if len(cur_sentence):
                        sentences.append(cur_sentence)
                        sentences[-1][-1] = sentences[-1][-1][:-1]
                        cur_sentence = []
                elif next_word[0].isupper():
                    if len(cur_sentence):
                        sentences.append(cur_sentence)
                        sentences[-1][-1] = sentences[-1][-1][:-1]
                        cur_sentence = []
        template_ontologies = [
            r"introduc\w+\b",
            r"propos\w+\b",
            r"present\b",
            r"propos\w+\b",
            r"describ\w+\b",
        ]

        for ind_sentence in range(len(sentences)):
            inds = [el for el in sentences[ind_sentence] if el.lower().find("ontolog") != -1]
            if not len(inds):
                continue
            ind_template = False

            for template in template_ontologies:
                inds = [el for el in sentences[ind_sentence] if re.search(template, el, re.UNICODE)]
                if len(inds):
                    ind_template = True

            if ind_template:
                #В парсер
                dependencies = standfordParserWorker.get_dependencies(u" ".join(sentences[ind_sentence]))
                for first_word, first_ind, second_word, second_ind in dependencies:
                    first_inds = [el for el in template_ontologies if re.search(el, first_word)]
                    sec_inds =  [el for el in template_ontologies if re.search(el, second_word)]
                    if len(first_inds) and second_word.lower().find("ontolog")!=-1:
                        ontology = get_ontology(second_ind, sentences[ind_sentence])
                        ontology = check_ontologies(ontology, stop_words)
                        exist_ontologies, new_ontologies = new_or_not_ontol(ontology, existontos)

                        if len(exist_ontologies):
                            related_ontos.extend(exist_ontologies)
                        if len(new_ontologies_out):
                            new_ontologies_out.append(new_ontologies_out)
                    if len(sec_inds) and first_word.lower().lower().find("ontolog") != -1:
                        ontology = get_ontology(second_ind, sentences[ind_sentence])
                        ontology = check_ontologies(ontology, stop_words)
                        exist_ontologies, new_ontologies = new_or_not_ontol(ontology, existontos)

                        if len(exist_ontologies):
                            related_ontos.extend(exist_ontologies)
                        if len(new_ontologies_out):
                            new_ontologies_out.append(new_ontologies_out)
            else:
                cur_sentence = u" ".join(sentences[ind_sentence])
                for ontol in existontos:
                    if cur_sentence.lower().find(ontol.lower()) != -1:
                        related_ontos.append(ontol)
    except Exception as err:
        print("get_inf_about_ontologies -> {0}".format(err))
    finally:
        return related_ontos, new_ontologies_out
def new_or_not_ontol(ontology, existontos):
    try:
        exist_ontol = []
        new_ontol = []

        for ontol_cand in ontology:
            if ontol_cand in existontos:
                exist_ontol.append(ontol_cand)
            else:
                new_ontol.append(ontol_cand)
    except Exception as err:
        print("new_or_not_ontol -> {0}".format(err))
    finally:
        return exist_ontol, new_ontol
def check_ontologies(ontologies, stop_words):
    try:
        outpt = []

        for ontol_cand in ontologies:
            if not ontol_cand in stop_words:
                outpt.append(ontol_cand)
    except Exception as err:
        print("check_ontologies -> {0}".format(err))
    finally:
        return outpt
def get_ontology(ind, sentences):
    try:
        outpt = []
        left_ontol = []
        for i in range(ind-1, ind-1-4, -1):
            if i < 0:
                break
            cur_word = sentences[i]
            if not re.search(r"[A-Z]", cur_word, re.U):
                break
            left_ontol.insert(0, cur_word)
        if len(left_ontol):
            left_ontol.append(sentences[i])
            outpt.append(u" ".join(left_ontol))
        right_ontol = []
        for i in range(ind+1, ind+1+4):
            if i >= len(sentences):
                break
            cur_word = sentences[i]
            if not re.search(r"[A-Z]", cur_word, re.U):
                break
            right_ontol.append(cur_word)
        if len(right_ontol):
            right_ontol.insert(0, sentences[i])
            outpt.append(u" ".join(right_ontol))
    except Exception as err:
        print("get_ontology -> {0}".format(err))
    finally:
        return outpt
def get_grants_and_finding_agencies(acknowledgents):
    try:
        grants = []
        eu_projects = []
        funding_agencies = []

        acknowledgents = re.sub(r"<.*?>", " ", acknowledgents, re.U).strip()
        acknowledgents = re.sub(r"pro +ject", "project", acknowledgents, re.U).strip()
        acknowledgents = re.sub(r"\(.*?\)", "", acknowledgents, re.U).strip()
        acknowledgents = re.sub(r" +([.!?])$", r"\1", acknowledgents, re.U)


        else_tokens = []
        for cur_token in [el for el in re.split(r" +", acknowledgents, re.U) if el.strip() != ""]:
            cur_work_token = re.sub(r"[.?!]$", "", cur_token, re.U).strip()

            if len(cur_work_token) and re.search(r"\d{3,}", cur_work_token) and cur_work_token[-1].isdigit():
                if re.search(r"[.?!]$", cur_token, re.U) and len(else_tokens):
                    else_tokens[-1] += cur_token[-1]
                grants.append({"id": cur_work_token})
            else:
                else_tokens.append(cur_token)

        sentences = []
        cur_sentence = []
        for i in range(len(else_tokens)):
            #prev_word = else_tokens[i-1]
            cur_word = else_tokens[i]
            next_word = ""
            if i+1 < len(else_tokens):
                next_word = else_tokens[i+1]

            cur_sentence.append(cur_word)
            if re.search(r"[.?!]$", cur_word, re.U) and cur_word.find("U.S.") == -1:
                if next_word == "":
                    if len(cur_sentence):
                        sentences.append(cur_sentence)
                        sentences[-1][-1] = sentences[-1][-1][:-1]
                        cur_sentence = []
                elif next_word[0].isupper():
                    if len(cur_sentence):
                        sentences.append(cur_sentence)
                        sentences[-1][-1] = sentences[-1][-1][:-1]
                        cur_sentence = []

        templates = [
            [r"by", r"under"],
            [r"funding from", r"under"],
            [r"by", r"in"],
            [r"by", r"in"],
            [r"by", r"within"],
            [r"by", r"funded"],
        ]

        next_templates = [
            r"by",
            r"funding",
            r"funding from",
        ]

        eu_templates = [
            r"\bEU\-funded\b",
            r"\bEU FP\d+\b",
            r"\bFP\d +European\b",
            r"\bEuropean +Union\b",
            r"\bFP\d+\b",
            r"\bEU +\d+th +Framework +Program\b",
            r"\bEuropean\b +\bUnion\b +\d+th\b +\bFramework\b +\bProgram\b"
        ]

        for i in range(len(sentences)):
            cur_sentence = sentences[i]

            flag = False

            for template in templates:
                first_search = template[0]
                sec_search = template[1]

                try:
                    ind_begin = cur_sentence.index(first_search)
                    end_template = cur_sentence.index(sec_search, ind_begin)
                    funding_agencies.append(u" ".join([el for el in cur_sentence[ind_begin+1:end_template] if el.strip() != "the"]))

                    cur_sentence = cur_sentence[:ind_begin] + cur_sentence[end_template+1:]
                    a = 1
                except Exception as err:
                    a = 1
            cur_sentence_new = u" ".join(cur_sentence)

            for second_template in next_templates:
                ind_template = cur_sentence_new.find(second_template)

                if ind_template != -1:
                    end_part = cur_sentence_new[ind_template+len(second_template):].strip()
                    if end_part.startswith("the "):
                        end_part = end_part[len("the "):].strip()
                    if len(end_part) and end_part[0].isupper():
                        for eu_template in eu_templates:
                            eu_re = re.search(eu_template, end_part, re.U)
                            if eu_re:
                                eu_grant = end_part[eu_re.start():]
                                if not eu_grant in eu_projects:
                                    eu_projects.append(eu_grant)
                            else:
                                if not end_part in funding_agencies:
                                    funding_agencies.append(end_part)
                    cur_sentence_new = cur_sentence_new[:ind_template].strip()
            for eu_template in eu_templates:
                eu_re = re.search(eu_template, cur_sentence_new, re.U)

                if eu_re:
                    before_part = cur_sentence_new[:eu_re.start()].strip().split(" ")
                    after_part = cur_sentence_new[eu_re.start():].strip().split(" ")

                    before_eu = []
                    for ind_before_eu in range(len(before_part)-1, len(before_part)-1-4, -1):
                        if ind_before_eu < 0:
                            break
                        if before_part[ind_before_eu][0].isupper() or re.search(r"(and)|(of)|(the)", before_part[ind_before_eu]):
                            before_eu.insert(0, before_part[ind_before_eu])
                    if len(before_eu):
                        before_eu = u" ".join(before_eu)
                        if not before_eu in eu_projects:
                            eu_projects.append(u" ".join(before_eu))

                    after_eu = []
                    for ind_after_eu in range(4):
                        if ind_after_eu == len(after_part):
                            break
                        if after_part[ind_after_eu][0].isupper() or re.search(r"(and)|(of)|(the)", after_part[ind_after_eu]):
                            after_eu.append(after_part[ind_before_eu])
                    if len(after_eu):
                        after_eu  = u" ".join(after_eu)
                        if not after_eu in eu_projects:
                            eu_projects.append()
        a = 1
    except Exception as err:
        print("get_grants_and_finding_agencies -> {0}".format(err))
    finally:
        return grants, funding_agencies, eu_projects
def get_cited_works(input_data):
    try:
        res_bibliography = []
        if not len(input_data):
            return res_bibliography
        #input_data = u"{newline}".join([pdf.html2text(el[1]) for el in input_data[0]])
        input_data = u"{newline}".join([re.sub(r"<.*?>", " ", el[1].replace("<br>", "{newline}")) for el in input_data[0]])
        #re.sub(r"<.*?>", " ", el[1].replace("<br>", "{newline}"))
        temp_array = get_bibliography_array(input_data)
        outpt = u"\n".join(temp_array)
        res_bibliography = get_bibliography(outpt)
        input_text = 1
    except Exception as err:
        print("get_cited_works -> {0}".format(err))
    finally:
        return res_bibliography
def get_bibliography(text):
    try:
        outpt = []
        if text == "":
            return outpt

        bib_items = text.split("\n")

        for i in range(len(bib_items)):
            cur_bib_item = re.sub(r"\(cid\:\d+\)", "", bib_items[i], re.U)
            if cur_bib_item == "":
                print("empty bib item -> {0}".format(i))
                continue
            cur_elem = {}


            year = [el for el in re.findall(r"\b(\d{4})\b", cur_bib_item) if 1900 < int(el) and int(el) < 2016]
            if len(year):
                for cur_year in year:
                    if test_year(cur_bib_item, cur_year):
                        cur_elem['year'] = int(year[0])
                        break
            doi = get_doi(cur_bib_item)
            begin_title = get_index_of_title(cur_bib_item)
            if begin_title is None:
                continue
            end_title = get_end_title(cur_bib_item, begin_title)
            cur_title = cur_bib_item[begin_title:end_title]

            cur_title = re.sub(r"\(\d+\)", "", cur_title)

            journal = get_journal(cur_bib_item, cur_title)
            if journal:
                cur_elem["journal"] = journal
            if doi:
                cur_elem["doi"] = doi
            if cur_title:
                cur_elem["title"] = cur_title

            if len(cur_elem):
                outpt.append(cur_elem)
        a = 1
    except Exception as err:
        print("get_bibliography -> {0}".format(err))
    finally:
        return outpt
def get_journal(text, title):
    try:
        journal = None
        if title == "":
            return journal
        splt = text.split(title)

        cand_journal = splt[1]
        end_journal = re.search(r"\d+\(\d+\)", cand_journal)
        if end_journal:
            journal = cand_journal[:end_journal.start()]
            upper_letter = re.search(r"[A-Z]", journal)
            journal = journal[upper_letter.start():].strip()
            while not journal[-1].isalpha():
                journal = journal[:-1]
            a = 1
        a = 1
    except Exception as err:
        print("get_journal -> {0}".format(err))
    finally:
        return journal
def get_end_title(cur_bib_item, begin_title):
    try:
        if cur_bib_item.find("Noppens,  O.,  Liebig,  T.,  Ontology  Patterns  and  Beyond") != -1:
            a = 1
        res_ind = len(cur_bib_item)
        if re.search(r"((\w{3,})\. )", cur_bib_item[begin_title:]):
            pos_end = re.search(r"((\w{3,})\. )", cur_bib_item[begin_title:])
            return begin_title+(pos_end.start()+len(pos_end.group(2)))
        elif re.search(r"\. +In\:", cur_bib_item[begin_title:]):
            pos_end = re.search(r"\. +In\:", cur_bib_item[begin_title:])
            return begin_title+pos_end.start()
        elif re.search(r" +\(\d+\)\, +http\:", cur_bib_item[begin_title:]):
            pos_end = re.search(r" +\(\d+\)\, +http\:", cur_bib_item[begin_title:])
            return begin_title+pos_end.start()
        elif re.search(r"(\",)|(\"\.)", cur_bib_item[begin_title:]):
            pos_end = re.search(r"(\",)|(\"\.)", cur_bib_item[begin_title:])
            return begin_title+pos_end.start()
        elif re.search(r"((\w{3,}), [A-Z])", cur_bib_item[begin_title:]):
            pos_end = re.search(r"((\w{3,}), [A-Z])", cur_bib_item[begin_title:])
            return begin_title+pos_end.end()-1
        elif cur_bib_item[begin_title:].find("*. ") != -1:
            return begin_title+cur_bib_item[begin_title:].find("*. ")
        elif re.search(r"\d\.\d\.", cur_bib_item[begin_title:]):
            pos_end = re.search(r"\d\.\d\.", cur_bib_item[begin_title:])
            return begin_title+pos_end.end()-1
        elif cur_bib_item[begin_title:].find("). ") != -1:
            return begin_title+cur_bib_item[begin_title:].find("). ")+1
        elif re.search(r" +\(\d+\)\, +\[", cur_bib_item[begin_title:]):
            pos_end = re.search(r" +\(\d+\)\, +\[", cur_bib_item[begin_title:])
            return begin_title+pos_end.start()
        elif re.search(r"[A-Z]{2}\. +[A-Z]", cur_bib_item[begin_title:]):
            pos_end = re.search(r"[A-Z]{2}\. +[A-Z]", cur_bib_item[begin_title:])
            return begin_title+pos_end.start() + 2
        elif re.search(r"\, +\d+", cur_bib_item[begin_title:]):
            pos_end = re.search(r"\, +\d+", cur_bib_item[begin_title:])
            return begin_title+pos_end.start()
        else:
            return len(cur_bib_item)
    except Exception as err:
        print("get_end_title -> {0}".format(err))
        return len(cur_bib_item)
def get_index_of_title(text):
    try:
        if not len(text):
            return None
        if text.find("H. J. Levesque") != -1:
            a = 1
        ind_begin = re.search(r"[A-Z]\.: ", text, re.U)
        if ind_begin:
            #test = text[ind_begin.end():]
            return ind_begin.end()
        elif re.search(r"\b[A-Z][a-z]+\: +\\[A-Z]", text, re.U):
            ind_begin = re.search(r"\b[A-Z][a-z]+\: +\\[A-Z]", text, re.U)
            #print(text[ind_begin.end()-1:])
            return ind_begin.end()
            a = 1
        elif re.search(r"ed\.\)\:", text):
            ind_begin = re.search(r"\)\:", text)
            return ind_begin.end()
        elif re.search(r"and +[A-Z][a-z]+ [A-Z][a-z]+\: +", text):
             ind_begin = re.search(r"and +[A-Z][a-z]+ [A-Z][a-z]+\: +", text)
             return ind_begin.end()
             a = 1
        elif re.search(r"and [A-Z][a-z]+ +[A-Z]\. +[A-Z][a-z]+\: ", text):
            ind_begin = re.search(r"and [A-Z][a-z]+ +[A-Z]\. +[A-Z][a-z]+\: ", text)
            return ind_begin.end()
        elif re.search(r"et al\.\:", text):
            ind_begin = re.search(r"et al\.\:", text)
            return ind_begin.end()
        elif re.search(r"\(\d+\)\.", text):
            ind_begin = re.search(r"\(\d+\)\.", text)
            return ind_begin.end()
        elif re.search(r"[A-Z](\.) [A-Z][a-z]+(\.|,) \\", text):
            pos_end_author_re = re.search(r"[A-Z]\. [A-Z][a-z]+(\.|,) \\", text)
            return pos_end_author_re.end()
        elif re.search(r"[A-Z]\. [A-Z][a-z]+:", text):
            cur_search = re.search(r"[A-Z]\. [A-Z][a-z]+:", text)
            return cur_search.end()
        elif re.search(r"^[A-Z]\.", text):
            cur_search = re.search(r"[A-Z]\. [A-Z][a-z]+\. [A-Z]", text)
            if cur_search:
                return cur_search.end()-1
            begin_title = re.sub(r"^[A-Z]\. [A-Z][a-z]+", "", text)
            ind_upper = 0
            for ind_chr in range(len(begin_title)):
                if begin_title[ind_chr].isupper():
                    ind_upper = ind_chr
                    break
            ind_back = len(text)-len(begin_title[ind_upper:])
            return ind_back
        elif re.search(r"^[A-Z][a-z]+ [A-Z]\.", text):
            last_author = re.search(r"[A-Z][a-z]+ [A-Z]\.\.? +[A-Z]", text)
            if last_author:
                return last_author.end()-1
            elif re.search(r"[A-Z]\.\. ", text):
                last_author = re.search(r"[A-Z]\.\. ", text)
                return last_author.end()
                #return
            elif re.search(r'[A-Z]\.[A-Z]\. +', text):
                last_author = re.search(r'[A-Z]\.[A-Z]\. +', text)
                return last_author.end()
            else:
                return 0
        elif re.search(r"^[A-Z][a-z]+ [A-Z][a-z]+", text):
            ind_dot = text.find(".")
            if ind_dot != -1:
                return ind_dot+1
            elif re.search(r"^[A-Z][a-z]+ [A-Z][a-z]+\, [A-Z]", text):
                ind_begin = re.search(r"^[A-Z][a-z]+ [A-Z][a-z]+\, [A-Z]", text)
                return ind_begin.end()-1
            return 0
        elif re.search(r"\.\: ", text):
            ind_begin = re.search(r"\.\:", text)
            return ind_begin.end()
        elif re.search(r"\, [A-Z]\., ", text):
            ind_begin = re.search(r"\, [A-Z]\., ", text)
            splt = text.split(".,")
            for ind_cur in range(len(splt)):
                if len([el for el in re.split(r"\W*", splt[ind_cur]) if len(el) > 2]) > 3:
                    #print(text[text.find(splt[ind_cur]):])
                    return text.find(splt[ind_cur])+1
            #return ind_begin.end()
        elif re.search(r"\, +[A-Z]\. +[A-Z]", text):
            ind_begin = re.search(r"\, +[A-Z]\. +[A-Z]", text)
            return ind_begin.end()-1
        elif re.search(r"\, +[A-Z]\.[A-Z]\. +[A-Z]", text):
            ind_begin = re.search(r"\, +[A-Z]\.[A-Z]\. +[A-Z]", text)
            return ind_begin.end()-1
        elif re.search(r"\, +[A-Z]\.\, +", text):
            ind_begin = re.search(r"\, +[A-Z]\.\, +", text)
            return ind_begin.end()
        elif re.search(r"[A-Z][a-z]+\. ([A-Z][a-z]+)", text):
            ind_begin = re.search(r"[A-Z][a-z]+\. ([A-Z][a-z]+)", text)
            return ind_begin.end()-1
        elif re.search(r"^[A-Z][a-z]+ +[A-Z]\. [A-Z]", text):
            ind_begin = re.search(r"^[A-Z][a-z]+ +[A-Z]\. [A-Z]", text)
            return ind_begin.end()-1
        elif re.search(r"\, +[A-Z]\.[A-Z]\.\, +[A-Z]", text):
            ind_begin = re.search(r"\, +[A-Z]\.[A-Z]\.\, +[A-Z]", text)
            return ind_begin.end()-1
        elif re.search(r"^[A-Z][a-z]+ +[A-Z]\. +[A-Z]", text, re.U):
            ind_begin = re.search(r"^[A-Z][a-z]+ +[A-Z]\. +[A-Z]", text)
            return ind_begin.end()-1
        elif re.search(r"[a-z]\, +[A-Z] +\: ", text):
            ind_begin = re.search(r"[a-z]\, +[A-Z] +\: ", text)
            return ind_begin.end()
        elif re.search(r"\, [A-Z]\.\:", text):
            ind_begin = re.search(r"\, [A-Z]\.\:", text)
            return ind_begin.end()
        elif text.find(u" \u201c") != -1:
            #print(text[text.find(u" \u201c")+2:])
            return text.find(u" \u201c")+2
        elif len(text) and text[0] == u"\u201c":
            return 1
        elif re.search(r"[A-Z]\.[A-Z]\.\, et al\. [A-Z]", text):
            ind_begin = re.search(r"[A-Z]\.[A-Z]\.\, et al\. [A-Z]", text)
            return ind_begin.end()-1
        elif re.search(r"[A-Z]\. +\(\d+\) +[A-Z]", text):
            ind_begin = re.search(r"[A-Z]\. +\(\d+\) +[A-Z]", text)
            return ind_begin.end()-1
        elif re.search(r"\, [A-Z]\. +\d+\. [A-Z]", text):
            ind_begin = re.search(r"\, [A-Z]\. +\d+\. [A-Z]", text)
            return ind_begin.end()-1
        elif re.search(r"and +[A-Z][a-z]+\, +[A-Z]", text):
            ind_begin = re.search(r"and +[A-Z][a-z]+\, +[A-Z]", text)
            return ind_begin.end()-1
        elif re.search(r"\b\w\b\. +\d+\. +[A-Z]", text):
            ind_begin = re.search(r"\w\. +\d+\. +[A-Z]", text)
            return ind_begin.end()-1
        else:
            a = 1
            return 0
    except Exception as err:
        print("get_index_of_title -> {0}".format(err))
        return 0
def get_doi(bib_item):
    try:
        res = None
        doi = [el for el in re.split(r"\W*", bib_item) if not el.isdigit() and re.search(r"\d{4,}", el)]
        if len(doi):
            for i in range(len(doi)):
                if re.search(r"\-|\.", doi[i]):
                    res = doi[i]
                    break
    except Exception as err:
        print("get_doi -> {0}".format(err))
    finally:
        return res
def test_year(elem, cur_year):
    res = False
    coords = elem.find(cur_year)
    if coords != -1:
        pos_cur = coords
        if pos_cur > 0 and elem[pos_cur-1] != "/":
            res = True
        else:
            a = 1
        return res
def get_bibliography_array(text):
    try:
        full_Articles = []
        ref_part = [el.strip() for el in text.strip().split("{newline}") if el.strip() != ""]

        flag = False
        for i in range(len(ref_part)):
            try:
                cur_re = re.search(r"^(\d{,2}\. )|(\[\d{,2}\])|(\[\w+\])", ref_part[i], re.UNICODE)
                if cur_re:
                    #a = cur_re.group()
                    full_Articles.append(ref_part[i][cur_re.end():].strip())
                else:
                    if full_Articles[-1].endswith('-'):
                        #print(ref_part[i])
                        full_Articles[-1] = u"{0}{1}".format(full_Articles[-1][:-1], ref_part[i])
                    else:
                        full_Articles[-1] += u" {0}".format(ref_part[i])
            except Exception as err:
                print(err)
                flag = True
                break
        if flag:
            text = re.sub(r"\[.*?\]", "", text.strip())
            ref_part = [el.strip() for el in text.split("{newline}") if el.strip() != ""]
            full_Articles = []
            for i in range(len(ref_part)):
                try:
                    cur_re = re.search(r"^[A-Z]\. ", ref_part[i], re.UNICODE)
                    if cur_re:
                        #a = cur_re.group()
                        full_Articles.append(ref_part[i].strip())
                        a = 1
                    else:
                        if full_Articles[-1].endswith('-'):
                            #print(ref_part[i])
                            full_Articles[-1] = u"{0}{1}".format(full_Articles[-1][:-1], ref_part[i])
                        else:
                            full_Articles[-1] += u" {0}".format(ref_part[i])
                except Exception as err:
                    print(err)
            a = 1

    except Exception as err:
        print("get_bibliography_array -> {0}".format(err))
    finally:
        return full_Articles
def get_inf_from_header(divs):
    try:
        if re.sub(r"<.*?>", "", divs[0][1]).strip() == "":
            divs.pop(0)
        title = ""
        authors_data = []
        flag = True
        font_name = ""
        title_tags = []
        else_tags = []
        flag_break = False
        font_size = -1
        for i in range(len(divs)):
            cur_div, cur_whole_div = divs[i]

            spans = get_all_tag_with_name("span", cur_whole_div)

            for j in range(len(spans)):
                cur_span, cur_whole_span = spans[j]

                params = get_params(cur_whole_span)
                cur_whole_text = re.sub(r"<.*?>", "", cur_whole_span, re.U).strip()
                if flag:
                    font_name = params.get("font-family", "")
                    flag = False
                else:
                    if font_name != params.get("font-family", ""):
                        ind_end_title_div = cur_whole_div.index(cur_whole_span)
                        pseudo_div = cur_whole_div[:ind_end_title_div]+r"</div>"
                        title_tags.append([get_params(cur_div), pseudo_div])
                        else_div_part = cur_whole_div[ind_end_title_div:]
                        else_tags.append([get_params(cur_div), else_div_part])

                        else_tags.extend([[get_params(el[0]), el[1]] for el in divs[i+1:]])
                        flag_break = True
                        break
                        a = 1
            if flag_break:
                break
            title_tags.append([get_params(cur_div), cur_whole_div])
        a = 1

        title_tags = sort_one_column(title_tags)
        title = " ".join([re.sub(r"<.*?>", "", el[1]) for el in title_tags]).strip()

        if re.sub(r"<.*?>", "", else_tags[0][1]).find("(cid:") != -1:
            else_tags.pop(0)
        elif re.sub(r"<.*?>", "", else_tags[0][1]).find(u'\u2217') != -1:
            else_tags.pop(0)
        text_first_div = [el for el in re.findall(r"\b[a-z]+\b", re.sub(r"<.*?>", "", else_tags[0][1]))]
        if len(text_first_div):
            title += " " + re.sub(r"<.*?>", "", else_tags[0][1])
            if len(else_tags):
                else_tags.pop(0)
        authors_data = get_authors_data(else_tags)
        #print(title)
        a = 1
    except Exception as err:
        print("get_inf_from_header -> {0}".format(err))
    finally:
        return title, authors_data
def get_article_parts(html_text):
    try:
        html_text = html_text.replace("\n", "").replace("\r", "")

        splt_pages = re.split("<div style=\"position\:absolute\; top\:\d+px\;\"><a name=\"\d+\">Page \d+</a></div>", html_text, re.UNICODE)
        #delete header part
        splt_pages = splt_pages[1:]

        [header, abstract] = get_header_and_abstract(splt_pages)
        [acknowledgements, references_block] = get_acknowledgements_references(splt_pages)

        a = 1
    except Exception as err:
        print("get_article_parts -> {0}".format(err))
    finally:
        return [header, abstract, acknowledgements, references_block]
def get_authors_data(divs):
    try:
        divs.sort(key = lambda m: m[0]["top"])
        authors_data = []

        div0_text = re.sub(r"<.*?>", "", divs[0][1])


        if re.search(r"\d\,", div0_text):
            authors_data = get_author_affilation_country_from_normal_teplate(divs)
            a = 1
        elif div0_text.find(",") == -1 and re.search(r"\d", div0_text):
            authors_data = get_author_affilation_country_from_best_teplate(divs)
        elif re.search(r"\band\b", div0_text) and div0_text.find(",") == -1:
            #authors_data = get_author_affilation_country_from_another_teplate(divs)
            authors_data = get_author_affilation_country_from_best_teplate(divs)
            if len(authors_data):
                authors = [el.strip() for el in re.split(r"\band\b", authors_data[0]["full_name"]) if el.strip() != -1]
                authors_data[0]["full_name"] = authors[0]
                authors_data.append({"full_name": authors[1], "organization": {}})
                authors_data[-1]["organization"]["title"]=authors_data[0]["organization"]["title"]
                if "country" in authors_data[0]["organization"]:
                    authors_data[-1]["organization"]["country"] = authors_data[0]["organization"]["country"]
            a = 1
        elif div0_text.find(",") != -1:
            a = 1
        else:
            authors_data = get_author_affilation_country_from_best_teplate(divs)
        #print(div0_text)
        a = 1
    except Exception as err:
        print("get_authors_data -> {0}".format(err))
    finally:
        return authors_data
def get_author_affilation_country_from_normal_teplate(divs):
    try:
        outpt = []
        names = []
        affil = []
        pochtas = []
        else_divs = []

        for i in range(len(divs)):
            cur_div, cur_whole_div = divs[i]
            cur_whole_text = re.sub(r"<.*?>", "", cur_whole_div).strip()

            if re.search(r"[A-Z][a-z]+\d", cur_whole_text):
                sub_splt = [el for el in re.sub(r"([A-Z][a-z]+)(\d+(,\d+,?)?)", r"\1||\2###", cur_whole_text, re.U).split("###") if el.strip() != ""]
                names.extend(sub_splt)
            elif re.search(r"^\d *[A-Z]", cur_whole_text):
                sub_splt = [re.sub(r",$", "", el.strip()) for el in re.sub(r"(\d+) *([A-Z])", r"###\1||\2", cur_whole_text, re.U).split("###") if el.strip() != ""]
                affil.extend(sub_splt)
            elif cur_whole_text.find("@") != -1 or re.search(r"([.@])[a-z]+(\-[a-z]+)?\.[a-z]{2,3}$", cur_whole_text, re.UNICODE):
                pochtas.append(cur_whole_text)
            elif cur_whole_text != "":
                else_divs.append(cur_whole_text)
        affil_hash = {}
        author_hash = {}

        for name in names:
            splt = name.split("||")
            if len(splt) == 2:
                author_hash[splt[0]] = [int(el) for el in re.findall(r"\d+", splt[1])]
        for af in affil:
            splt = af.split("||")
            if len(splt) == 2:
                #for num in re.findall(r"\d+", splt[1])
                affil_hash[int(splt[0])] = splt[1].strip() + " " + u" ".join(else_divs)
        if not len(affil_hash) and len(names) and len(else_divs):
            for k, v in names.items():
                affil_hash[v] = u" ".join(else_divs)
        for k, v_af in author_hash.items():
            for c_af in v_af:
                if c_af in affil_hash:
                    c_affil = affil_hash[c_af]

                    c_affil = affilation_by_skobka(c_affil)

                    outpt.append({"full_name": k})
                    if c_affil[0] != "":
                        outpt[-1]["organization"] = {}
                        outpt[-1]["organization"]["title"] = c_affil[0]
                    if c_affil[0] != "":
                        if not "organization" in outpt[-1]:
                            outpt[-1]["organization"] = {}
                        outpt[-1]["organization"]["country"] = c_affil[1]
                    a = 1
            a = 1
    except Exception as err:
        print("get_author_affilation_country_from_normal_teplate -> {0}".format(err))
    finally:
        return outpt
def get_author_affilation_country_from_best_teplate(divs):
    try:
        authors_inf = []
        divs.sort(key = lambda m: m[0]["top"])#cmp = mysorter, reverse = True)

        if True:#divs[0][0]["top"] == divs[1][0]["top"]:

            new_divs = []
            names = []
            else_divs = []

            for i in range(len(divs)):
                cur_div, cur_whole_div = divs[i]
                if cur_whole_div.find("sam.") != -1:
                    a = 1
                cur_whole_div = re.sub(r"(<span .*?>)(.+)<br>", r"\1\2</span>\1", cur_whole_div.replace(r"<br></span>", r"</span>"))
                spans = get_all_tag_with_name('span', cur_whole_div)
                step = cur_div.get("height")/len(spans)
                for j in range(len(spans)):
                    cur_span, cur_whole_span = spans[j]
                    cur_whole_text = re.sub(r"<.*?>", "", cur_whole_span)
                    cur_params = get_params(cur_span)

                    cur_top = step*j
                    temp_div_add = dict([(k,v) for k,v in cur_div.items()])
                    temp_div_add["top"] += cur_top
                    #temp_div_add["font-size"] = cur_params.
                    if len(cur_whole_text) > 1:
                        new_divs.append([temp_div_add, cur_whole_text])
            new_divs.sort(key = lambda m: m[0]["top"])



            base_div = new_divs[0][0]

            for temp_div_add, cur_whole_text in new_divs:
                    if base_div.get("top") == temp_div_add["top"] and base_div.get("left") <= temp_div_add.get("left"):
                        names.append([temp_div_add, cur_whole_text])
                    else:
                        else_divs.append([temp_div_add, cur_whole_text])
            for cur_div, cur_div_text in names:

                x0 = cur_div.get("left")
                x1 = cur_div.get("left") + cur_div.get("width")
                y = cur_div.get("top")

                cur_data = [cur_div_text]
                cur_falg = False
                cur_mail = [0]
                for j_ind in range(len(else_divs)):
                    else_div, else_text = else_divs[j_ind]
                    else_x = else_div.get("left") + else_div.get("width")/2
                    else_y = else_div.get("top")

                    if x0<=else_x and else_x < x1 and else_y >= y:
                        if re.search(r"([.@])[a-z]+(\-[a-z]+)?\.[a-z]{2,3}$", else_text, re.UNICODE) or else_text.find("@") != -1:

                            cur_mail.append( len(cur_data) )
                        cur_data.append(else_text)

                if len(cur_mail) == 2 and cur_mail[-1] != len(cur_data)-1:
                    try:

                        cur_data.pop(cur_mail[1])
                        cur_mail[-1] = len(cur_data)
                    except Exception as err:
                        print(err)
                j_ind = 1
                while j_ind < len(cur_mail):
                    part = cur_data[cur_mail[j_ind-1]:cur_mail[j_ind]]
                    if not len(part):
                        break
                    authors_inf.append({"full_name": part.pop(0).strip()})
                    authors_inf[-1]["organization"] = {}

                    if re.search(r"[a-z]+\.[a-z]{2,3}", part[-1]):
                        part.pop()
                    curr_affil = affilation_by_skobka(u" ".join(part).strip())
                    authors_inf[-1]["organization"]["title"] = curr_affil[0]
                    if curr_affil[1] != "":
                        authors_inf[-1]["organization"]["country"] = curr_affil[1]
                    cur_mail[j_ind] += 1
                    j_ind += 1
                a = 1
            a = 1


        a = 1
    except Exception as err:
        print("get_author_affilation_country_from_best_teplate -> {0}".format(err))
    finally:
        return authors_inf
def affilation_by_skobka(affilation_with_possible_country):
    try:
            skobki = affilation_with_possible_country.strip().endswith(")")
            if skobki:
                ind_begin_skobka = affilation_with_possible_country.rindex("(")

                return [affilation_with_possible_country[:ind_begin_skobka].strip(), affilation_with_possible_country[ind_begin_skobka+1:len(affilation_with_possible_country)-1]]
            elif re.search(r", +[A-Z][A-Za-z]+( [A-Z][A-Za-z]+)?$", affilation_with_possible_country, re.UNICODE):
                index_comma = affilation_with_possible_country.rindex(",")
                return [affilation_with_possible_country[:index_comma].strip(), affilation_with_possible_country[index_comma+1:len(affilation_with_possible_country)].strip()]
            elif re.search(r", +\w+ ([A-Z][A-Za-z]+)$", affilation_with_possible_country, re.UNICODE):
                res = re.search(r", +\w+ ([A-Z][A-Za-z]+)$", affilation_with_possible_country, re.UNICODE)
                t_res = res.group(1)
                return [affilation_with_possible_country[:res.start()].strip(), t_res]
            return [affilation_with_possible_country , '']
    except Exception as err:
            print("affilation_by_skobka -> {0}".format(err))
def get_index_of_div_references(cur_page):
    try:
        div_references = None
        text = re.sub(r"<.*?>", "", cur_page)
        if re.search(r"\bFig(ure)?\b", text):
            return None
        divs_all = get_all_tag_with_name("div", cur_page)

        for i in range(len(divs_all)):
            tag, whole_tag = divs_all[i]
            spans = get_all_tag_with_name("span", whole_tag)

            for j in range(len(spans)):
                span_tag, whole_span_tag = spans[j]
                text = re.sub(r"<.*?>", "", whole_span_tag)

                #print(text)
                splt = [el for el in re.split("\\W*", text) if not el.isdigit() and el.strip() != ""]

                if len(splt) == 1:
                    if splt[0].lower() == 'bibliography' or splt[0].lower() == 'references':
                        whole_span_tag = "".join([el[1] for el in spans[:j+1]])
                        return [whole_tag, whole_span_tag]
        return None
    except Exception as err:
        print("get_index_of_div_references -> {0}".format(err))
        return None
def is_two_column_checker(reference_pages):
    try:
        divs = [el for el in get_all_tag_with_name("div", reference_pages) if el[0].find(r'<div style="position:absolute; top:0px;">') == -1
                        and re.sub(r"<.*?>", "", el[1]).strip() != ""]
        params_dict = get_params(divs[0][0])

        length = params_dict.get("left", 0) + params_dict.get("width", 0)

        if length > 300:
            return False
        else:
            return True
        a = 1
    except Exception as err:
        print("is_two_column_checker -> {0}".format(err))
def sort_reference_pages(reference_page, two_columns):
    try:
        divs_all = [[get_params(el[0]), el[1]] for el in get_all_tag_with_name("div", reference_page)
                    if el[0].find(r'<div style="position:absolute; top:0px;">') == -1
                        and re.sub(r"<.*?>", "", el[1]).strip() != ""
                    ]



        if two_columns:
            divs_all = sort_two_columns(divs_all)
        else:
            divs_all = sort_one_column(divs_all)
        a = 1
    except Exception as err:
        print("sort_reference_pages -> {0}".format(err))
    finally:
        return divs_all
def get_references_divs(pages, ind_page_references_begin, references_begin_tag):
    try:
        if ind_page_references_begin < 0:
            return []
        reference_pages = pages[ind_page_references_begin:]
        reference_pages[0] = reference_pages[0][ reference_pages[0].index(references_begin_tag): ]

        is_two_column = is_two_column_checker(reference_pages[0])
        new_references = []
        for ref_page in reference_pages:
            text = re.sub(r"<.*?>", "", ref_page)
            if re.search(r"\bFig(ure)?\b", text):
                continue
            new_references.append(ref_page)
        for i in range(len(new_references)):
            new_references[i] = sort_reference_pages(new_references[i], is_two_column)
        return new_references
    except Exception as err:
        print("get_references_divs -> {0}".format(err))
        return []
def get_acknowledgements_references(pages):
    try:
        acknowledgemnts = u""
        references = []

        if len(pages) < 3:
            return [acknowledgemnts, references]

        ind_page_references_begin = -1
        references_begin_tag = ""
        references_span_begin = ""

        div_begin_acknowledgments = ""
        span_begin_acknowledgments = ""
        page_begin_acknowledgments = -1
        for i in range(len(pages)-1, 2, -1):
            cur_page = pages[i]

            ind_div_references = get_index_of_div_references(cur_page)
            if ind_div_references is not None:
                references_begin_tag = ind_div_references[0].replace(ind_div_references[1], "")
                ind_page_references_begin = i
                references_span_begin = ind_div_references[1]
                pages[i] = pages[i].replace(ind_div_references[1], "")
                break
        if ind_page_references_begin != -1:
            for i in range(ind_page_references_begin, ind_page_references_begin+1):
                cur_page = pages[i]

                divs_all = get_all_tag_with_name("div", cur_page)

                flag_not_found = False
                for ind_div in range(len(divs_all)):
                    tag, whole_tag = divs_all[ind_div]

                    #если нашел до начала библиографии, то не нашел
                    if whole_tag == references_begin_tag:
                        flag_not_found = True
                        break

                    spans_all = get_all_tag_with_name("span", whole_tag)

                    for cur_span, cur_whole_span in spans_all:
                        span_text = re.sub(r"<.*?>", "", cur_whole_span)

                        splt_span_words = re.findall(r"\w+", span_text)

                        if len(splt_span_words) == 1:
                            if re.search(r"acknowledgment", splt_span_words[0].lower()):
                                page_begin_acknowledgments = i
                                div_begin_acknowledgments = tag
                                span_begin_acknowledgments = cur_whole_span
                                flag_not_found = True
                                break
                if flag_not_found:
                    break

        references = get_references_divs(pages, ind_page_references_begin, references_begin_tag)

        if page_begin_acknowledgments > 0:
            if page_begin_acknowledgments == ind_page_references_begin:
                acknowledgemnts_begin = pages[page_begin_acknowledgments].index(span_begin_acknowledgments)+len(span_begin_acknowledgments)
                acknowldgements_end = pages[page_begin_acknowledgments].index(references_begin_tag, acknowledgemnts_begin)
                acknowledgemnts = pages[page_begin_acknowledgments][acknowledgemnts_begin:acknowldgements_end].strip()
                #print(acknowledgemnts)
            else:
                print("acknowledgements and bibliography on the different_pages")
        a = 1
    except Exception as err:
        print("get_acknowledgements_references -> {0}".format(err))
    finally:
        return [acknowledgemnts, references]
def get_header_and_abstract(pages):
    try:
        header = []
        abstract = ""
        if not len(pages):
            return header, abstract
        divs_all = get_all_tag_with_name("div", pages[0])
        ind_begin_abstract = get_index_abstract(divs_all)

        if ind_begin_abstract == -1:
            return header, abstract

        header = [el for el in divs_all[:ind_begin_abstract]]
        abstract = divs_all[ind_begin_abstract][1]
        a = 1
    except Exception as err:
        print("get_header_and_abstract -> {0}".format(err))
    finally:
        return [header, abstract]
def get_index_abstract(divs):
    try:
        index = -1
        for i in range(len(divs)):
            not_html = re.sub(r"<.*?>", "", divs[i][1])
            splt = [el for el in not_html.split(" ") if el.strip() != ""]
            if len(splt) > 30:
                index = i
                break
    except Exception as err:
        print("get_index_abstract -> {0}".format(err))
    finally:
        return index
def get_all_tag_with_name(what_search, html_text):
    try:
        outpt = []
        ind_first = html_text.find("<{0}".format(what_search))
        while True:
            try:
                end_tag = html_text.index(">", ind_first)+1
                end_what_search = html_text.index(r"</"+what_search+">", ind_first)+len(r"</"+what_search+">")

                tag_first = html_text[ind_first:end_tag]
                whole_cur_html = html_text[ind_first:end_what_search]
                outpt.append([tag_first, whole_cur_html])

                ind_first = html_text.index("<{0}".format(what_search), end_what_search)
            except Exception as err:
                break
    except Exception as err:
        print("get_all_tag_with_name -> {0}".format(err))
    finally:
        return outpt
def get_params(first_div_in_page):
    try:
        splt = {}
        ind_begin_params = first_div_in_page.index("style=\"")+len("style=\"")
        ind_end_params = first_div_in_page.index('"', ind_begin_params)


        for el in first_div_in_page[ind_begin_params:ind_end_params].split(";"):
            temp_split = el.split(":")
            if len(temp_split) != 2:
                continue
            if temp_split[1].strip().replace("px", "").isdigit():
                    splt[temp_split[0].strip()] = int(temp_split[1].strip().replace("px", ""))
            else:
                    splt[temp_split[0].strip()] = temp_split[1].strip()
        a = 1
    except Exception as err:
        print("get_params -> {0}".format(err))
    finally:
        return splt
def sort_one_column(divs_all):
    def mysorter(x, y):
        y1 = x[0].get("top", 0)
        y2 = y[0].get("top", 0)

        x1 = x[0].get("left", 0)
        x2 = y[0].get("left", 0)
        if y1 < y2:
            if x1 < x2:
                return 1
            return 0
        return -1
    try:
        divs_all.sort(cmp = mysorter, reverse = True)
    except Exception as err:
        print("sort_one_column -> {0}".format(err))
    finally:
        return divs_all
def sort_two_columns(divs):
    try:
        left = []
        right = []

        for div, whole_div in divs:
            if div.get("left") < 300:
                left.append([div, whole_div])
            else:
                right.append([div, whole_div])
            a = 1
        left = sort_one_column(left)
        left = sort_merge_intersections(left)
        right = sort_one_column(right)
        right = sort_merge_intersections(right)

        left.extend(right)

        # for div, whole_div in left:
        #     print(re.sub(r"<.*?>", "", whole_div))
        #     a  = 1
        a = 1
    except Exception as err:
        print("sort_two_columns -> {0}".format(err))
    finally:
        return left
def sort_merge_intersections(divs):
    try:
        outpt = []
        i = 0
        while i < len(divs):
            cur_div, cur_whole_div = divs[i]
            #print(cur_whole_div)


            cur_y0 = cur_div.get("top", 0)
            cur_y1 = cur_div.get("top", 0) + cur_div.get("height", 0)
            cur_x0 = cur_div.get("left", 0)
            cur_x1 = cur_div.get("left", 0) + cur_div.get("width", 0)
            cur_inds = []
            j = i+1
            while j <len(divs):
                temp_div, temp_whole_div = divs[j]

                temp_y0 = temp_div.get("top", 0)
                temp_x0 = cur_div.get("left", 0)

                if cur_y0 <= temp_y0 and temp_y0 < cur_y1 and cur_x0 <= temp_x0 and temp_x0 < cur_x1:
                    cur_inds.append([temp_div, temp_whole_div])
                else:
                    #i = j
                    break
                j+=1
            if len(cur_inds):
                merged_elem = merged_known([cur_div, cur_whole_div], cur_inds)
                outpt.append(merged_elem)
                i = j
            else:
                outpt.append(divs[i])
            i+=1
        # for cur_div, cur_whole_div in outpt:
        #     print(re.sub(r"<.*?>", "", cur_whole_div))
        a = 1
    except Exception as err:
        print("sort_merge_intersections -> {0}".format(err))
    finally:
        return outpt
def merged_known(base, subelems):
    try:
        outpt = []
        cur_div, cur_whole_div = base
        splt = cur_whole_div.split("<br>")

        for subelem_div, subelem_whole_div in subelems:
            index_to_add = int((subelem_div.get("top", 0) - cur_div.get("top"))/subelem_div.get("height") + 0.5)
            try:
                splt[index_to_add] += subelem_whole_div
            except Exception as err:
                splt[-1] += subelem_whole_div
        cur_whole_div = "<br>".join(splt)
        outpt = [cur_div, cur_whole_div]
        a = 1
    except Exception as err:
        print("merged_known -> {0}".format(err))
    finally:
        return outpt
if __name__ == "__main__":
    test_metadata()