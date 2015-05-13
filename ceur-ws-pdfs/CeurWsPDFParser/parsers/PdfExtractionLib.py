# -*- coding: UTF-8 -*-

import os,re,codecs, re, sys

if sys.version[0] == '3':
    import html.entities as htmlentitydefs
    unicode = str
    unichr = chr
else:
    import htmlentitydefs

path_to_pdf2txt = os.path.join("{0} {1}".format(sys.executable,os.path.dirname(__file__)), 'pdf2txt.py')

def main():
    directory = True
    if directory:
        input_directory = os.path.join(os.path.dirname(__file__), "pdfs")

        for filename in os.listdir(input_directory):
            if not filename.endswith(".pdf"):
                continue
            print(filename)

            fullname = os.path.join(input_directory, filename)

            res = get_html_and_txt(fullname, add_files = True, update_files = False)
    else:
        a = 1

def get_html_and_txt(input_filename, add_files = False, update_files = True):
    try:
        out_inf = {
            "html": u"",
            "txt": u"",
        }

        temp_html_file = ''
        temp_txt_file = ''
        temp_txt_from_html_file = ''

        if not add_files:
            if not os.path.isdir(os.path.join( os.path.dirname(__file__), 'temp_dir') ):
                os.mkdir( os.path.join( os.path.dirname(__file__), 'temp_dir') )
            temp_html_file = os.path.join( os.path.dirname(__file__), 'temp_dir', "1.html" )
            temp_txt_file = os.path.join( os.path.dirname(__file__), 'temp_dir', "1.txt" )
            temp_txt_from_html_file = os.path.join( os.path.dirname(__file__), 'temp_dir', "1.txt_html" )
        else:
            #pos_dot = os.path.basename(input_filename).rindex(".")

            temp_html_file = os.path.join( os.path.dirname(input_filename), os.path.basename(input_filename).replace(".pdf", '.html'))
            temp_txt_file = os.path.join( os.path.dirname(input_filename), os.path.basename(input_filename).replace(".pdf", '.txt'))
            temp_txt_from_html_file =  os.path.join( os.path.dirname(input_filename), os.path.basename(input_filename).replace(".pdf", '.txt_html'))


        txt_command = u"{0} -o \"{1}\" \"{2}\"".format(path_to_pdf2txt, temp_txt_file, input_filename)
        html_command =u"{0} -o \"{1}\" \"{2}\"".format(path_to_pdf2txt, temp_html_file, input_filename)

        if not os.path.exists(temp_txt_file):
            print(txt_command)
            os.system(txt_command)
        else:
             if update_files:
                print(txt_command)
                os.system(txt_command)
        if not os.path.exists(temp_html_file):
            print(html_command)
            os.system(html_command)
        else:
            if update_files:
                print(html_command)
                os.system(html_command)

        fh = codecs.open(temp_txt_file, 'rb')
        out_inf["txt"] = fh.read(os.path.getsize(temp_txt_file)).decode("UTF-8")
        fh.close()

        fh = codecs.open(temp_html_file, 'rb')
        out_inf["html"] = fh.read(os.path.getsize(temp_html_file)).decode("UTF-8")
        fh.close()

        out_inf['txt_from_html'] = html2text(out_inf["html"])

        wh = codecs.open(temp_txt_from_html_file, 'w', encoding="UTF-8")
        wh.write(out_inf['txt_from_html'])
        wh.close()
    except Exception as err:
        print("get_html_and_txt -> {0}".format(err))
    finally:
        return out_inf

def html2text(html_text):
    def char_from_entity(match):
        code = htmlentitydefs.name2codepoint.get(match.group(1), 0xFFFD)
        return unichr(code)
    #убрал таким образом комментарии
    text = re.sub(r"<[Pp][^>]*?(?!</)>", "\n\n", unicode(html_text))
    #text = re.sub(r"<[Hh]\d+[^>]*?(?!</)>", "\n\n", unicode(html_text))
    text = re.sub(r"<[^>]*?>", " ", text)
    text = re.sub(r"&#(\d+);", lambda m: unichr(int(m.group(1))), text)
    text = re.sub(r"&([A-Za-z]+);", char_from_entity, text)
    text = re.sub(r"\n(?:[ \xA0\t]+\n)+", "\n", text)
    return re.sub(r"\n\n+", "\n\n", text.strip())
if __name__ == '__main__':
    main()

