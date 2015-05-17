# -*- coding: UTF-8 -*-
__author__ = 'Alexander'
import os, codecs

def main():
    test_string = r"We describe our computational experience using the algorithm, and demonstrate that it is indeed possible to efficiently solve the standard concept subsumption reasoning problem in four large real-world OWL ontologies: SNOMED-CT, NCI, SWEET-JPL and GALEN."

    dependecies = get_dependencies(test_string)

def get_dependencies(test_string):
    try:
        dependecies = []
        res = write_test_string_to_file(test_string)
        if not res:
            print("Impossible to save information to temp file")
            return dependecies
        command = "lexparser \"{0}\" > \"{1}\"".format(
            os.path.join(os.path.dirname(__file__), "temp_standford", "temp_standford.txt"),
            os.path.join(os.path.dirname(__file__), "temp_standford", "standford_out.txt")
        )
        os.system(command)

        dependecies = read_dependecies_file()
        a = 1
    except Exception as err:
        print("get_dependencies -> {0}".format(err))
    finally:
        return dependecies
def read_dependecies_file():
    try:
        outpt = []
        fh = None
        temp_filename = os.path.join(os.path.dirname(__file__), "temp_standford", "standford_out.txt")
        fh = codecs.open(temp_filename, "r", encoding="UTF-8")

        for line in fh:
            try:
                line = line.strip()
                if line.strip() == "":
                    continue
                #nsubj(describe-2, We-1)
                ind_skobka = line.find("(")
                if ind_skobka == -1:
                    continue
                elements = line[ind_skobka+1:-1].split(", ")
                if len(elements) != 2:
                    continue
                first_n_ind = elements[0].rindex("-")
                second_n_ind = elements[1].rindex("-")

                first_word = elements[0][:first_n_ind]
                first_ind = int(elements[0][first_n_ind+1:])-1

                second_word = elements[1][:second_n_ind]
                second_ind = int(elements[1][second_n_ind+1:])-1
                a = 1
                outpt.append([first_word, first_ind, second_word, second_ind])
            except Exception as err:
                print(err)
    except Exception as err:
        print("read_dependecies_file -> {0}".format(err))
    finally:
        if fh is not None:
            fh.close()
        return outpt
def write_test_string_to_file(test_string):
    try:
        temp_dir = os.path.join(os.path.dirname(__file__), "temp_standford")
        res = 0
        wh = None
        if not os.path.isdir(temp_dir):
            os.mkdir(temp_dir)

        wh = codecs.open( os.path.join(temp_dir, "temp_standford.txt"), "w", encoding="UTF-8")

        wh.write(test_string)
        res = 1
    except Exception as err:
        print("write_test_string_to_file -> {0}".format(err))
    finally:
        if wh is not None:
            wh.close()
        return res

def read_stop_words():
    try:
        words = []
        fh = None
        fh = codecs.open(os.path.join(os.path.dirname(__file__), "dictionaries", "stopwords.txt"), "rb")#, encoding="UTF-8")
        words = [el.strip() for el in fh.read(os.path.getsize(os.path.join(os.path.dirname(__file__), "dictionaries", "stopwords.txt"))).decode("UTF-8").split("\n") if el.strip() != ""]
    except Exception as err:
        print("read_stop_words -> {0}".format(err))
    finally:
        if fh is not None:
            fh.close()
        return words


def read_existonto():
    try:
        words = []
        fh = None
        fh = codecs.open(os.path.join(os.path.dirname(__file__), "dictionaries", "existonto.txt"), "r", encoding="UTF-8")
        for line in fh:
            words.append(line.strip())
        #words = [el.strip() for el in text.split("\n") if el.strip() != ""]
        words = [el for el in dict([(el, 1) for el in words]).keys() if el.strip() != ""]
    except Exception as err:
        print("read_stop_words -> {0}".format(err))
    finally:
        if fh is not None:
            fh.close()
        return words
if __name__ == "__main__":
    main()