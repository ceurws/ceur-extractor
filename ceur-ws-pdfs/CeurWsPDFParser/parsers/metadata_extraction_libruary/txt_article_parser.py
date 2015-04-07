__author__ = 'Alexander'

import os, re, codecs, sys
import pdf_extraction_lib

if sys.version[0] == '3':
    unichr = chr
    unicode = str
def main():
    test_dir = False
    if test_dir:
        input_dir = r"D:\JOB\SemanticChallenge\pdf_task\pdfs"

        files = [elem for elem in os.listdir(input_dir)]

        for file_id in range(1, len(files)):
            if not files[file_id].endswith(".pdf"):
                continue
            fullname = os.path.join(input_dir, files[file_id])
            out_filename = os.path.join(input_dir, files[file_id].replace(".pdf", ".csv"))

            inp_data = pdf_extraction_lib.get_html_and_txt(fullname)

            works = get_cited_works(inp_data["txt"])

            write_csv(out_filename, files[file_id], works)
            a = 1
    else:
        txt_article_name = os.path.join('temp_dir', "1.txt")
        out_file = txt_article_name.replace(".txt", ".csv")

        fh = codecs.open(txt_article_name, 'rb')
        text = fh.read(os.path.getsize(txt_article_name)).decode("UTF-8")
        fh.close()

        works = get_cited_works(text)

        write_csv(out_file, 'test', works)




def write_csv(out_file, txt_article_name, works):
    features = [
        'title',
        'journal',
        'doi',
        'year',
    ]
    wh = codecs.open(out_file, 'w', encoding = "UTF-8")
    wh.write("filename\t")
    for feature in features:
        wh.write("{0}\t".format(feature))
    wh.write("\n")
    for elem in works:
        wh.write("{0}\t".format(txt_article_name))
        for feature in features:
            wh.write("{0}\t".format(elem.get(feature, "")))
        wh.write("\n")
    wh.close()
    a = 1
def get_cited_works(input_text):
    try:
        works_array = []
        ind_references = -1
        what_find = "\nReferences"
        ind_references = input_text.find(what_find)
        if ind_references == -1:
            what_find = "REFERENCES"
            ind_references_re = re.search(r"REFERENCES", input_text, re.MULTILINE)
            if ind_references_re:
                ind_references = ind_references_re.start()
        if ind_references == -1:
            what_find = "\fReferences"
            ind_references = input_text.find(what_find)
        if ind_references != -1:
            ind_references += len("\nReferences")
            ref_part = input_text[ind_references:].strip()

            ind_f = ref_part.find("\f")
            if ind_f != -1:
                try:
                    enf_f = ref_part.index("\f", ind_f+1)
                    ref_part = ref_part[:ind_f] + ref_part[enf_f+1:]
                except Exception as err:
                    ref_part = ref_part.replace("\f", "")
            ref_part = ref_part.replace("\r", "")
            splt = [el.strip() for el in ref_part.split("\n\n") if el.strip() != ""]
            if re.search(r"^\d+$", splt[-1].strip()) or re.search(r"^\d+[^.]", splt[-1]):
                splt.pop()
                ref_part = "\n".join(splt)

            bibliography_array = get_bibliography_array(ref_part)

            works_array = get_inf_from_bib_array(bibliography_array)
            a = 1
    except Exception as err:
        print("get_cited_works -> {0}".format(err))
    finally:
        return works_array
def get_inf_from_bib_array(bibliography_array):
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
    try:
        outpt = []
        for i in range(len(bibliography_array)):
            elem = bibliography_array[i]

            elem = re.sub(r"\(cid:\d+\)", "", elem)

            if elem.strip() == "":
                continue
            if i == 12:
                a = 1
            cur_elem = {}

            #get_year
            #test = re.findall(r"[^\\]\b(\d{4})\b[^\\]", elem)
            year = [el for el in re.findall(r"\b(\d{4})\b", elem) if 1900 < int(el) and int(el) < 2016]
            if len(year):
                for cur_year in year:
                    if test_year(elem, cur_year):
                        cur_elem['year'] = int(year[0])
                        break

            doi = [el for el in re.split(r"\W*", elem) if not el.isdigit() and re.search(r"\d{4,}", el)]
            if len(doi):
                if re.search(r"\-|\.", doi[0]):
                    cur_elem["doi"] = delete_not_printable(doi[0])


            title = get_title(elem)

            if title == '':
                print("Couldn't find title in {0}".format(elem))
                continue
                a = 1
            else:
                ind_upper = 0
                for ind_chr in range(len(title)):
                    if title[ind_chr].isupper():
                        ind_upper = ind_chr
                        break
                cur_elem['title'] = delete_not_printable(title[ind_upper:])
            a = 1

            journal = get_journal(elem, cur_elem['title'])
            cur_elem["journal"] = delete_not_printable(journal)
            if cur_elem["title"] != "":
                print("{0} {1}".format(i, cur_elem))
                outpt.append(cur_elem)
        #print(outpt)
        a = 1
    except Exception as err:
        print("get_inf_from_bib_array -> {0}".format(err))
    finally:
        return outpt
def delete_not_printable(string):
    try:
        replacable = {
            28: 'fi',
        }
        unicode_not_printable = 29
        inds = [ord(el) for el in string]

        for ind in inds:
            if ind <= unicode_not_printable:
                string = string.replace(unichr(ind), replacable.get(ind, ""))

        return string
    except Exception as err:
        print("delete_not_printable -> {0}".format(err))
def get_journal(text, title):
    try:
        journal = "0"
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
def get_title(text):
    try:
        text = re.sub(r"\(cid:\d+\)", "", text).strip()
        title = ""
        cur_search = re.search(r"\b[A-Za-z]\.:", text)
        if cur_search:
            begin_title = text[cur_search.end():].strip()
            end_title_re = re.search(r"((\w{3,})\. )|(\",)", begin_title)
            if end_title_re:
                title = begin_title[:end_title_re.start()+len(end_title_re.group(2))].strip()
            else:
                end_title_re = re.search(r"((\w{3,}), [A-Z])", begin_title)
                if end_title_re:
                    title = begin_title[:end_title_re.start()+len(end_title_re.group(2))].strip()
                a = 1
            a = 1
        #elif re.search(r"[A-Z]\. [A-Z][a-z]+\. \\", text):
        elif re.search(r"[A-Z](\.) [A-Z][a-z]+(\.|,) \\", text):
            pos_end_author_re = re.search(r"[A-Z]\. [A-Z][a-z]+(\.|,) \\", text)
            begin_title = text[pos_end_author_re.end():]
            end_title_re = re.search(r"(\w{3,}\. )|(\",)|(\"\.)", begin_title)
            if end_title_re:
                title = begin_title[:end_title_re.start()].strip()
            a = 1
        elif re.search(r"^[A-Z]\.", text):
            cur_search = re.search(r"[A-Z]\. [A-Z][a-z]+\. [A-Z]", text)
            if cur_search:
                begin_title = text[cur_search.end()-1:].strip()
                a = 1
##                end_title_re = re.search(r"(\w{3,}\. )|(\",)", begin_title)
##                if end_title_re:
##                    title = begin_title[:end_title_re.start()].strip()
            else:
                cur_search = re.search(r"[A-Z]\. [A-Z][a-z]+:", text)
                if cur_search:
                    begin_title = text[cur_search.end():].strip()

                else:
                    begin_title = re.sub(r"^[A-Z]\. [A-Z][a-z]+", "", text)
                    ind_upper = 0
                    for ind_chr in range(len(begin_title)):
                        if begin_title[ind_chr].isupper():
                            ind_upper = ind_chr
                            break
                    begin_title = begin_title[ind_upper:]
                a = 1
            end_title_re = re.search(r"(\w{3,}\. )|(\",)|(\"\.)", begin_title)
            if end_title_re:
                title = begin_title[:end_title_re.start()].strip()
            a = 1
        elif re.search(r"^[A-Z][a-z]+ [A-Z]\.", text):
            last_author = re.search(r"[A-Z][a-z]+ [A-Z]\. [A-Z]", text)
            if last_author:
                begin_title = text[last_author.end()-1:]
                end_title_re = re.search(r"((\w{3,})\. )|(\",)", begin_title)
                if end_title_re:
                    title = begin_title[:end_title_re.start()+len(end_title_re.group(2))].strip()
            a = 1
        elif re.search(r"^[A-Z][a-z]+ [A-Z][a-z]+", text):
            ind_dot = text.find(".")
            if ind_dot != -1:
                begin_title = text[ind_dot+1:].strip()
                pos_end = begin_title.find(".")
                title = begin_title[:pos_end]
            a = 1
        else:
            end_title_re = re.search(r"\w{3,}\.|(\",)", text)
            if end_title_re:
                title = text[:end_title_re.start()].strip()

            a = 1
    except Exception as err:
        print("get_title -> {0}".format(err))
    finally:
        return title
def get_bibliography_array(text):
    try:
        full_Articles = []
        ref_part = [el.strip() for el in text.strip().split("\n") if el.strip() != ""]

        full_Articles = []
        for i in range(len(ref_part)):
            try:
                cur_re = re.search(r"^(\d{,2}\.)|(\[\d{,2}\])", ref_part[i], re.UNICODE)
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
                a = 1
        #print("\n".join(full_Articles))
    except Exception as err:
        print("get_bibliography_array -> {0}".format(err))
    finally:
        return full_Articles
if __name__ == "__main__":
    main()