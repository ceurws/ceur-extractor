#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, codecs, sys

from bs4 import BeautifulSoup
import PdfExtractionLib as pdf

if sys.version[0] == '3':
    import html.entities as htmlentitydefs
    unicode = str
    unichr = chr
else:
    import htmlentitydefs

def test_main():
    debug = True

    if debug:
        #f_name = os.path.join(os.path.dirname(__file__), "pdfs", "Vol-903-paper-06.pdf")
        f_name = r"D:\JOB\SemanticChallenge\pdf_task\MyPDFLib\evaluation_pdfs\Vol-1044-paper-04.pdf"
        dict_data = pdf.get_html_and_txt(f_name,  update_files = False, add_files = True)

        result_data = get_information(dict_data, f_name)
    else:
        input_dir = r"D:\JOB\SemanticChallenge\pdf_task\MyPDFLib\evaluation_pdfs"

        for filename in os.listdir(input_dir):

            fullname = os.path.join(input_dir, filename)
            if not filename.endswith(".pdf"):
                continue
            #print(filename)
            dict_data = pdf.get_html_and_txt(fullname,  update_files = False, add_files = True)
            get_information(dict_data, filename)
def get_information(dict_data, fullname):
    try:
        article_parts = get_article_parts(dict_data.get("html", ""))


        authors = get_authors(article_parts[0], fullname)
        # print(u"\n".join([ el[4]  for el in article_parts[0]]))
        # if article_parts[2] == "":
        #     print("No acknowledgements {0}".format(fullname))
        # if article_parts[3] == "":
        #     print("No bibliography {0}".format(fullname))
    except Exception as err:
        print("get_inforamtion -> {0}".format(err))
def get_authors(header_part, fullname):
    try:
        authors = []

        authors = get_authors_by_mail(header_part, fullname)
    except Exception as err:
        print("get_authors -> {0}".format(err))
def get_authors_by_mail(header_part, fullname):
    try:
        mails = []
        for cur_div_i in range(len(header_part)):
            cur_div = header_part[cur_div_i]
            splt = re.split(r" +", cur_div[5], re.UNICODE)

            temp_mails = [[elem.strip() for elem in el[:el.find("@")].split(",")] for el in splt if el.find("@") != -1]

            for temp_mail in temp_mails:
                for cur_tipa_mail in temp_mail:
                    tipa_names = [el.lower() for el in re.findall(r"\b([A-Za-z]{4,})\b", cur_tipa_mail)]

                    if len(tipa_names):
                        mails.append([cur_div_i, tipa_names])


        names_div = []
        if len(mails):
            print(mails)
            for cur_div_i in range(len(header_part)):
                cur_div = header_part[ cur_div_i ]
                cur_div_tokens = [ el.strip().lower() for el in re.split(r"\W*", cur_div[5]) ]

                for cur_div_token_i in range(len(cur_div_tokens)):
                    cur_div_token = cur_div_tokens[cur_div_token_i]
                    if len(cur_div_token) < 4:
                        continue
                    cur_div_flag = False
                    for cur_mail in mails:
                        if cur_mail[0] == cur_div_i:
                            continue
                        cur_flag = False
                        for cur_part_name in cur_mail[1]:
                            a = 1
                            if cur_part_name.find(cur_div_token) != -1 or cur_div_token.find(cur_part_name) != -1:
                                #print(cur_part_name)
                                #print(cur_div_token)
                                cur_flag = True
                                break
                        if cur_flag:
                            cur_div_flag = True
                            break
                    if cur_div_flag:
                        print( cur_div[5] )
                        names_div.append([cur_div_i, cur_div[5]])
                        break

        if len(names_div):
            names_div.sort(key = lambda m: m[0])
            print(u"{0} title -> {1}".format(fullname, u" ".join([el[5] for el in header_part[:names_div[0][0]]])))
        a = 1
    except Exception as err:
        print("get_authors_by_mail")
def get_article_parts(input_html):
    try:
        if not len(input_html):
            return [], "", "", []
        input_html = input_html.replace("\n", "").replace("\r", "")
        splt_pages = re.split("<div style=\"position\:absolute\; top\:\d+px\;\"><a name=\"\d+\">Page \d+</a></div>", input_html, re.UNICODE)

        if len(splt_pages):
            splt_pages.pop(0)
        header_part = []
        abstract = u""
        if len(splt_pages):
            [header_part, abstract] = get_header_and_abstract(splt_pages[0])
            [ackowledgements, references] = get_ackowledgements_references(splt_pages)
    except Exception as err:
        print("get_article_parts -> {0}".format(err))
    finally:
        return [header_part, abstract, ackowledgements, references]
def get_ackowledgements_references(pages):
    try:
        acnowledgements_part = ""

        references_part = ""
        whole_html = u"{NEW_PAGE}".join(pages)
        references = []

        div_begin_references = ""
        span_begin_references = ""
        div_begin_acknowledgements = ""
        span_begin_acknowledgements = ""
        acknow_flag = True
        reference_flag = True
        for i in range(len(pages)-1, len(pages)-1-4, -1):
            if i < 2:
                break

            cur_page = pages[i]

            #cur_soup = BeautifulSoup(cur_page)

            #divs = cur_soup.find_all('div')
            divs = get_all_tag_with_name("div", cur_page)

            for i_div in range(len(divs)):
                #spans = BeautifulSoup(unicode(divs[i_div])).find_all('span')
                #print(divs[i_div][1])
                spans = get_all_tag_with_name("span", divs[i_div][1])

                for ind_span in range(len(spans)):
                    #print(spans[ind_span][2])
                    #if re.search(r"^\d*\.? *(Acknowledgments?)|(ACKNOWLEDGMENTS?)|", spans[ind_span].text, re.UNICODE):
                    if re.search(r"^\d*\.? *(Acknowledgements?)|(ACKNOWLEDGMENTS?)", spans[ind_span][2], re.UNICODE):

                        div_begin_acknowledgements = divs[i_div][0]
                        ind_end = div_begin_acknowledgements.find(">")
                        div_begin_acknowledgements = div_begin_acknowledgements[:ind_end+1]
                        span_begin_acknowledgements = spans[ind_span][1]
                        #print(span_begin_acknowledgements)
                        acknow_flag = False
                        #print(spans[ind_span][1])
                        #break
                    #if re.search(r"^\d*\.? *(References?)|(REFERENCES)|(Bibliography)|(BIBLIOGRAPHY)", spans[ind_span].text, re.UNICODE):
                    if re.search(r"^\d*\.? *(References?)|(REFERENCES)|(Bibliography)|(BIBLIOGRAPHY)", spans[ind_span][2], re.UNICODE) and reference_flag:
                        if div_begin_references != divs[i_div][1]:
                            div_begin_references = divs[i_div][1]
                            ind_end = div_begin_references.find(">")
                            div_begin_references = div_begin_references[:ind_end+1]
                            span_begin_references = spans[ind_span][1]
                            #print(span_begin_references)
                            reference_flag = False
                        a = 1
                    if not reference_flag and not acknow_flag:
                        break
        if div_begin_acknowledgements != "" and div_begin_references != "":
            acnowledgements_part = whole_html[whole_html.find(div_begin_acknowledgements):whole_html.find(div_begin_references)]
            acnowledgements_part = acnowledgements_part[acnowledgements_part.find(span_begin_acknowledgements):]
            a = 1
            #print(acnowledgements_part)
        if div_begin_references != "":
            references_part = whole_html[whole_html.find(div_begin_references):]
            references_part = get_references_divs(references_part.split("{NEW_PAGE}"), 0, div_begin_references)
            if len(references_part) and len(references_part[0]):
                array_to_del = []
                for ind_div_t in range(len(references_part[0])):
                    try:
                        references_part[0] = [[el[0], el[1].replace(span_begin_references, "")] for el in references_part[0]]
                        cur_text = get_normal_text(references_part[0][ind_div_t][1])
                        if cur_text == "" or re.search(r"^\d*\.? *(References?)|(REFERENCES)|(Bibliography)|(BIBLIOGRAPHY)", cur_text, re.UNICODE):
                            array_to_del.append(ind_div_t)
                            a = 1
                            #references_part[0].pop(0)
                        else:
                            break
                    except Exception as err:
                        print(err)
                array_to_del.sort(reverse=True)
                for ar_to_del in array_to_del:
                    references_part[0].pop(ar_to_del)
                a = 1
                a = 1
            #print(references_part)

        a = 1
    except Exception as err:
        print("get_ackowledgements_references -> {0}".format(err))
    finally:
        return acnowledgements_part, references_part
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
def get_header_and_abstract(first_page):
    try:

        divs = sort_divs_on_page_by_top(first_page)

        divs_header = []
        div_abstract = u""
        for i_div in range(len(divs)):
            try:
                if i_div == 15:
                    a = 1
                cur_div = divs[i_div]
                #spans = BeautifulSoup(u" ".format(cur_div[4])).find_all("span")
                spans = get_all_tag_with_name("span", cur_div[4])

                header_spans = []
                else_spans = []
                flag_end = False
                for ind_span in range(len(spans)):
                    #print(spans[ind_span][2])
                    #if spans[ind_span].text.find("Abstract") != -1 or len(re.split(r"\W*", spans[ind_span].text)) > 20:
                    if spans[ind_span][2].find("Introduction") != -1:
                        flag_end = True
                        break
                    if spans[ind_span][2].find("ABSTRACT") != -1 or spans[ind_span][2].find("Abstract") != -1 or len(re.split(r"\W*", spans[ind_span][2])) > 20:
                        #else_spans = [u"{0}".format(el) for el in spans[ind_span:]]
                        flag_end = True
                        break
                    if not flag_end:
                        header_spans.append(u"{0}".format(spans[ind_span]))
                if flag_end:
                    if not len(header_spans) and not re.search(r"Introduction", cur_div[5], re.I):
                        div_abstract = cur_div
                    a = 1
                    break
                divs_header.append([cur_div[-1], cur_div[-3]])
            except Exception as err:
                print(err)
        if len(div_abstract):
            div_abstract = div_abstract[5]
        a = 1

        a = 1
    except Exception as err:
        print("get_header_and_abstract -> {0}".format(err))
    finally:
        return [divs_header, div_abstract]
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
def sort_divs_on_page_by_top(soup):
    try:
        divs = []
        for cur_div in get_all_tag_with_name('div', soup):
        #for cur_div in soup.find_all('div'):
            #[x, y, width, height] = get_coords( cur_div.get("style") )
            [x, y, width, height] = get_coords( get_params( cur_div[0] ) )
            divs.append([x, y, width, height, cur_div[1], get_normal_text(cur_div[1]), cur_div[0]])
        divs.sort(key = lambda m: m[1])
    except Exception as err:
        print("sort_divs_on_page_by_top -> {0}".format(err))
    finally:
        return divs
def get_coords(style_string):
    try:
        x = style_string.get("left", -1)
        y = style_string.get("top", -1)
        width = style_string.get("width", -1)
        height = style_string.get("left", -1)

        # tops = [int(el) for el in re.findall(r"top\:(\d+)px\;", style_string, re.UNICODE)]
        # widths = [int(el) for el in re.findall(r"width\:(\d+)px\;", style_string, re.UNICODE)]
        # left = [int(el) for el in re.findall(r"left\:(\d+)px\;", style_string, re.UNICODE)]
        # heights = [int(el) for el in re.findall(r"height\:(\d+)px\;", style_string, re.UNICODE)]
        # if len(tops):
        #     y = tops[0]
        # if len(widths):
        #     width = widths[0]
        # if len(left):
        #     x= left[0]
        # if len(heights):
        #     height = heights[0]
        a = 1
    except Exception as err:
        print("get_style_coord -> {0}".format(err))
    finally:
        return [x, y, width, height]
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
                whole_text = get_normal_text(whole_cur_html)
                outpt.append([tag_first, whole_cur_html, whole_text])

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
def get_normal_text(input_text):
    def char_from_entity(match):
        code = htmlentitydefs.name2codepoint.get(match.group(1), 0xFFFD)
        return unichr(code)
    try:
        input_text = re.sub(r"<.*?>", " ", input_text)
        input_text = re.sub(r"&#(\d+);", lambda m: unichr(int(m.group(1))), input_text)
        input_text = re.sub(r"&([A-Za-z]+);", char_from_entity, input_text)
        input_text = input_text.replace("  ", " ").strip()
    except Exception as err:
        print("get_normal_text -> {0}".format(err))
    finally:
        return input_text
if __name__ == "__main__":
    test_main()