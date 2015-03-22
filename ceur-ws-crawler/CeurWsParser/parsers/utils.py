import re
from datetime import datetime

REGEX_1 = re.compile(r'.*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*(\d{1,2})[th]*'
                     r'[-\s]*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*(\d{1,2})[,\s]*(\d{4}).*',
                     re.I | re.S)
REGEX_2 = re.compile(r'.*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|dic)[a-z]*[,\.\s]*(\d{1,2})[th]*'
                     r'[-\sand]+(\d{1,2})[th]*[\s,]*(\d{4}).*', re.I | re.S)
REGEX_3 = re.compile(
    r'.*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|out)[a-z]*[,\s]*(\d{1,2})[sthnd]*[,\s]*(\d{4}).*',
    re.I | re.S)
REGEX_4 = re.compile(r'.*[,\s]+(\d{1,2})[.th]*[-\sbisund]+(\d{1,2})[.th]*'
                     r'\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|m\xe4r|okt)[a-z]*[,\s]*(\d{4}).*',
                     re.I | re.S | re.U)
REGEX_5 = re.compile(r'.*[,\s]+(\d{1,2})[th]*\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[,\s]*(\d{4}).*',
                     re.I | re.S)
REGEX_6 = re.compile(r'.*(20\d{2}).*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*'
                     r'[,\.\s]*(\d{1,2})[th]*[-\s]+(\d{1,2})[th]*.*', re.I | re.S)
REGEX_7 = re.compile(r'.*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[,\.\s]+(\d{4}).*', re.I | re.S)


def parse_date(text):
    match_1 = re.match(REGEX_1, text)
    if match_1:
        month_start = match_1.group(1)
        day_start = match_1.group(2)
        month_end = match_1.group(3)
        day_end = match_1.group(4)
        year = match_1.group(5)
        return [
            datetime.strptime("%s-%s-%s" % (month_start, day_start, year), '%b-%d-%Y'),
            datetime.strptime("%s-%s-%s" % (month_end, day_end, year), '%b-%d-%Y')
        ]
    match_2 = re.match(REGEX_2, text)
    if match_2:
        month = parse_month(match_2.group(1))
        day_start = match_2.group(2)
        day_end = match_2.group(3)
        year = match_2.group(4)
        return [
            datetime.strptime("%s-%s-%s" % (month, day_start, year), '%b-%d-%Y'),
            datetime.strptime("%s-%s-%s" % (month, day_end, year), '%b-%d-%Y')
        ]
    match_3 = re.match(REGEX_3, text)
    if match_3:
        month = parse_month(match_3.group(1))
        date = datetime.strptime(month + "-" + match_3.group(2) + "-" + match_3.group(3),
                                 '%b-%d-%Y')
        return [date]
    match_4 = re.match(REGEX_4, text)
    if match_4:
        month = parse_month(match_4.group(3))
        day_start = match_4.group(1)
        day_end = match_4.group(2)
        year = match_4.group(4)
        return [
            datetime.strptime("%s-%s-%s" % (month, day_start, year), '%b-%d-%Y'),
            datetime.strptime("%s-%s-%s" % (month, day_end, year), '%b-%d-%Y')
        ]
    match_5 = re.match(REGEX_5, text)
    if match_5:
        date = datetime.strptime(match_5.group(2) + "-" + match_5.group(1) + "-" + match_5.group(3),
                                 '%b-%d-%Y')
        return [date]
    match_6 = re.match(REGEX_6, text)
    if match_6:
        month = match_6.group(2)
        day_start = match_6.group(3)
        day_end = match_6.group(4)
        year = match_6.group(1)
        return [
            datetime.strptime("%s-%s-%s" % (month, day_start, year), '%b-%d-%Y'),
            datetime.strptime("%s-%s-%s" % (month, day_end, year), '%b-%d-%Y')
        ]
    match_7 = re.match(REGEX_7, text)
    if match_7:
        month = parse_month(match_7.group(1))
        year = match_7.group(2)
        date = datetime.strptime(month + "-" + year, '%b-%Y')
        return [date]

    return None


def parse_month(string):
    if string.lower() in ['out', 'okt']:
        return 'oct'
    if string.lower() == u'm\xe4r':
        return 'mar'
    if string.lower() == 'dic':
        return 'dec'
    else:
        return string