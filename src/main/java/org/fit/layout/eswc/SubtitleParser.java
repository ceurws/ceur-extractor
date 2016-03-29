/**
 * SubtitleParser.java
 *
 * Created on 21. 4. 2015, 11:46:01 by burgetr
 */
package org.fit.layout.eswc;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.Vector;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.fit.layout.eswc.op.AreaUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


/**
 *
 * @author burgetr
 */
public class SubtitleParser
{
    private static Logger log = LoggerFactory.getLogger(SubtitleParser.class);
    public ArrayList<String> INTEGERS = new ArrayList<>(Arrays.asList("fir", "seco", "three", "four", "fif", "six", "seven", "eight", "nin"));

    public enum TType { ORD, WORKSHOP, SHORT, COLOC, AT };
    private String src;
    private Vector<String> titleShorts;
    private Vector<Token> tokens;
    private Set<Event> ws;
    private Event colocEvent;

    public SubtitleParser(String inputText, Vector<String> titleShorts)
    {
        src = inputText;
        this.titleShorts = titleShorts;
        ws = new HashSet<Event>();
        tokenize();
        /*for (Token t: tokens)
            System.out.println(t);*/
        scanTokens();
    }

    public Set<Event> getWorkshops()
    {
        return ws;
    }

    public Event getColocEvent()
    {
        return colocEvent;
    }

    private void tokenize()
    {
        tokens = new Vector<Token>();

        Matcher matcher = AreaUtils.shortTitlePattern.matcher(src);
        while (matcher.find())
        {
            final String sname = matcher.group(0);
            if (sname.length() >= 2 && sname.length() <= 10 && !AreaUtils.blackShort.contains(sname))
                tokens.add(new Token(matcher.start(), TType.SHORT, sname));
        }

        //st nd rd th
        matcher = Pattern.compile("[1-9][0-9]*[snrt][tdh]|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth").matcher(src.toLowerCase());
        while (matcher.find())
        {
            final String order = matcher.group(0).trim();
            tokens.add(new Token(matcher.start(), TType.ORD, order));
        }

        matcher = Pattern.compile("workshop|col?\\p{Pd}*ll?ocated|in\\s+conjun?ction|located at").matcher(src.toLowerCase());
        while (matcher.find())
        {
            final String word = matcher.group(0);
            if (word.equals("workshop"))
                tokens.add(new Token(matcher.start(), TType.WORKSHOP, word));
            else
                tokens.add(new Token(matcher.start(), TType.COLOC, word));
        }

        matcher = Pattern.compile("^at\\s|\\sat\\s").matcher(src.toLowerCase());
        while (matcher.find())
        {
            final String word = matcher.group(0);
            tokens.add(new Token(matcher.start(), TType.AT, word));
        }

        Collections.sort(tokens);
    }

    private void scanTokens()
    {
        //count the occurences, gather statistics
        Token coloc = null;
        Token at = null;
        Token behindat = null;
        Map<String, Integer> counts = new HashMap<String, Integer>();
        for (Token t : tokens)
        {
            if (at != null && behindat == null)
                behindat = t;
            if (t.type == TType.SHORT && coloc == null)
            {
                Integer cnt = counts.get(t.value);
                if (cnt == null)
                    counts.put(t.value, 1);
                else
                    counts.put(t.value, cnt++);
            }
            else if (t.type == TType.COLOC)
                coloc = t;
            else if (t.type == TType.AT)
                at = t;
        }

        //if collocated not found, try to use 'at' if present
        if (coloc == null && at != null)
        {
            if (behindat != null && (behindat.type == TType.SHORT || behindat.type == TType.ORD))
                coloc = at;
        }

        //if colocated is found, disambiguate colocation now
        if (coloc != null)
        {
            coloc.used = true;
            for (int i = tokens.indexOf(coloc); i < tokens.size(); i++)
            {
                Token t = tokens.elementAt(i);
                if (t.type == TType.SHORT)
                {
                    t.used = true;
                    int ord = -1;
                    Token ordt = findOrdBeforeIndex(i);
                    if (ordt != null)
                    {
                        ordt.used = true;
                        String tmp = ordt.value.substring(0, ordt.value.length() - 2);
                        if(INTEGERS.contains(ordt.value.substring(0, ordt.value.length() - 2))){
                          tmp = (INTEGERS.indexOf(ordt.value.substring(0, ordt.value.length() - 2)) + 1) + "";
                        }
                        ord = Integer.parseInt(tmp);
                    }
                    colocEvent = new Event(ord, t.value, null);
                    break;
                }
            }
        }

        //try to find workshops
        Set<String> titles = new HashSet<String>(titleShorts);
        if (colocEvent != null)
            titles.remove(colocEvent.sname);
        Set<String> subtitles = new HashSet<String>(counts.keySet());
        if (colocEvent != null)
            subtitles.remove(colocEvent.sname);
        Set<String> supported = intersection(titles, subtitles);

        if (supported.isEmpty())
        {
            //no abbreviations in title or significantly more in subtitles -- scan subtitle
            if (titles.size() == 0 || (titles.size() <= 1 && subtitles.size() > 2))
                scanAbbreviations(subtitles, coloc, false);
            else
                scanAbbreviations(titles, coloc, true);
        }
        else //some intersection exists - use the intersection short names
        {
            scanAbbreviations(supported, coloc, false);
        }

        //no collocation, is some abbreviation remaining?
        if (coloc == null)
        {
            Set<String> remain = new HashSet<String>(counts.keySet());
            for (Event e : ws)
                remain.remove(e.sname);
            Vector<Integer> indices = findAbbrevIndices(remain, tokens.size(), false);
            if (!indices.isEmpty())
            {
                Token t = tokens.elementAt(indices.firstElement());
                t.used = true;
                int ord = -1;
                Token ordt = findOrdBeforeIndex(indices.firstElement());
                if (ordt != null)
                {
                    ordt.used = true;
                    ord = Integer.parseInt(ordt.value.substring(0, ordt.value.length() - 2));
                }
                colocEvent = new Event(ord, t.value, null);
            }
        }
    }

    private void scanAbbreviations(Set<String> supported, Token coloc, boolean allowNotFound)
    {
        log.info("Subtitle scan for {}", supported);
        int max = (coloc == null) ? tokens.size() : tokens.indexOf(coloc);
        //create ordered list of tokens
        Vector<String> names = new Vector<String>(supported);
        Vector<Integer> indices = findAbbrevIndices(names, max, allowNotFound);
        //are there any indices found?
        boolean ipresent = false;
        for (int i : indices)
        {
            if (i != -1)
            {
                ipresent = true;
                break;
            }
        }
        //try to find the numbers
        for (int ii = 0; ii < indices.size(); ii++)
        {
            int idx = indices.elementAt(ii);
            if (idx == -1) //not found in the subtitle (probably only in title)
            {
                int ord = -1;
                Token ordt = null;
                String wtitle = null;
                if (!ipresent) //none present, map the order numbers in order of appearance
                {
                    for (Token t : tokens)
                    {
                        if (coloc != null && t.pos >= coloc.pos)
                            break; //do not search afrer colocated
                        if (!t.used && t.type == TType.ORD)
                        {
                            t.used = true;
                            ordt = t;
                            ord = parseOrder(t.value);
                            break;
                        }
                    }
                    if (ordt != null) //search for title between order and some end
                    {
                        wtitle = extractTitle(ordt, coloc);
                    }
                }
                ws.add(new Event(ord, names.elementAt(ii), wtitle));
            }
            else //token found in subtitle
            {
                Token sn = tokens.elementAt(idx);
                sn.used = true;
                int ord = -1;
                String wtitle = null;
                Token ordt = findOrdBeforeIndex(idx);
                if (ordt != null)
                {
                    ordt.used = true;
                    ord = parseOrder(ordt.value);
                    wtitle = extractTitle(ordt, sn);
                }
                else
                {
                    Token wst = findWsBeforeIndex(idx);
                    if (wst != null)
                        wtitle = extractTitle(wst, sn);
                }
                ws.add(new Event(ord, sn.value, wtitle));
            }
        }
    }

    private String extractTitle(Token startt, Token stopt)
    {
        String wtitle = "";
        Token first = startt;
        Token last = stopt;

        int si = first.pos;
        if (first.type == TType.ORD)
            si += first.value.length();

        if (last == null) //need to find the end
        {
            for (Token t : tokens)
            {
                if (t.pos > first.pos)
                {
                    if (t.type == TType.ORD || t.type == TType.WORKSHOP || t.used)
                    {
                        last = t;
                        break;
                    }
                }
            }
        }
        int ei = (last == null) ? src.length() : last.pos;

        wtitle = src.substring(si, ei).trim();

        while (wtitle.toLowerCase().startsWith("workshop"))
            wtitle = wtitle.substring("workshop".length()).trim();
        while (wtitle.toLowerCase().startsWith("on"))
            wtitle = wtitle.substring("on".length()).trim();
        while (wtitle.toLowerCase().endsWith("the"))
            wtitle = wtitle.substring(0, wtitle.length() - "the".length()).trim();
        while (wtitle.length() > 0 && !Character.isAlphabetic(wtitle.codePointAt(wtitle.length() - 1)))
            wtitle = wtitle.substring(0, wtitle.length() - 1).trim();

        if (wtitle.isEmpty())
            return null;
        else
            return wtitle;
    }

    private int parseOrder(String value)
    {
        switch (value.toLowerCase())
        {
            case "first": return 1;
            case "second": return 2;
            case "third": return 3;
            case "fourth": return 4;
            case "fifth": return 5;
            case "sixth": return 6;
            case "seventh": return 7;
            case "eighth": return 8;
            case "ninth": return 9;
            default:
                return Integer.parseInt(value.substring(0, value.length() - 2));
        }
    }

    private int findToken(TType type, String value, int max)
    {
        for (int i = 0; i < max; i++)
        {
            final Token t = tokens.elementAt(i);
            if (t.type == type && value.equals(t.value))
                return i;
        }
        return -1;
    }

    private Token findOrdBeforeIndex(int index)
    {
        for (int i = index - 1; i >= 0; i--)
        {
            Token t = tokens.elementAt(i);
            if (t.used)
                break;
            if (t.type == TType.ORD)
                return t;
        }
        return null;
    }

    private Token findWsBeforeIndex(int index)
    {
        for (int i = index - 1; i >= 0; i--)
        {
            Token t = tokens.elementAt(i);
            if (t.used)
                break;
            if (t.type == TType.WORKSHOP)
                return t;
        }
        return null;
    }

    private Vector<Integer> findAbbrevIndices(Collection<String> supported, int max, boolean allowNotFound)
    {
        Vector<Integer> indices = new Vector<Integer>();
        for (String sname : supported)
        {
            int ti = findToken(TType.SHORT, sname, max);
            if (ti != -1 || allowNotFound)
                indices.add(ti);
            else
                log.error("{} not found in subtitle, this shouldn't happen", sname);
        }
        Collections.sort(indices);
        return indices;
    }

    private Set<String> intersection(Set<String> set1, Set<String> set2)
    {
        boolean set1IsLarger = set1.size() > set2.size();
        Set<String> cloneSet = new HashSet<String>(set1IsLarger ? set2 : set1);
        cloneSet.retainAll(set1IsLarger ? set1 : set2);
        return cloneSet;
    }

    class Token implements Comparable<Token>
    {
        public TType type;
        public int pos;
        public String value;
        public boolean used;

        public Token(int pos, TType type, String value)
        {
            this.pos = pos;
            this.type = type;
            this.value = value;
            this.used = false;
        }

        @Override
        public int compareTo(Token other)
        {
            return pos - other.pos;
        }

        @Override
        public String toString()
        {
            return "Token [type=" + type + ", pos=" + pos + ", value=" + value + "]";
        }
    }

}
