/**
 * LogicalTreeBuilder.java
 *
 * Created on 19. 3. 2015, 13:54:48 by burgetr
 */
package org.fit.layout.eswc.logical;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.Vector;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.fit.layout.classify.taggers.DateTagger;
import org.fit.layout.classify.taggers.LocationsTagger;
import org.fit.layout.eswc.Countries;
import org.fit.layout.eswc.CountriesTagger;
import org.fit.layout.eswc.Event;
import org.fit.layout.eswc.IndexFile;
import org.fit.layout.eswc.SubtitleParser;
import org.fit.layout.eswc.op.AreaUtils;
import org.fit.layout.eswc.op.CeurTag;
import org.fit.layout.eswc.op.EswcTag;
import org.fit.layout.impl.BaseLogicalTreeProvider;
import org.fit.layout.model.Area;
import org.fit.layout.model.AreaTree;
import org.fit.layout.model.Box;
import org.fit.layout.model.LogicalArea;
import org.fit.layout.model.LogicalAreaTree;
import org.fit.layout.model.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.ibm.icu.util.Calendar;


/**
 *
 * @author burgetr
 */
public class LogicalTreeBuilder extends BaseLogicalTreeProvider
{
    private static Logger log = LoggerFactory.getLogger(LogicalTreeBuilder.class);

    private static final float ms = 0.5f;

    private static int paperIdCnt = 0;

    private static Tag tagRoot = new EswcTag("root");
    private static Tag tagVTitle = new EswcTag("vtitle");
    private static Tag tagPublished = new EswcTag("published");
    private static Tag tagRelated = new EswcTag("related");
    private static Tag tagVShort = new EswcTag("vshort");
    private static Tag tagVOrder = new EswcTag("vorder");
    private static Tag tagWTitle = new EswcTag("wtitle");
    private static Tag tagColoc = new EswcTag("colocated");
    private static Tag tagSubtitle = new EswcTag("subtitle");
    private static Tag tagVCountry = new EswcTag("vcountry");
    private static Tag tagVDate = new EswcTag("vdate");
    private static Tag tagStartDate = new EswcTag("startdate");
    private static Tag tagEndDate = new EswcTag("enddate");
    private static Tag tagVEditor = new EswcTag("veditor");
    private static Tag tagEAffil = new EswcTag("eaffil");
    private static Tag tagECountry = new EswcTag("ecountry");
    private static Tag tagPaper = new EswcTag("paper");
    private static Tag tagAuthor = new EswcTag("authors");
    private static Tag tagTitle = new EswcTag("title");
    private static Tag tagPages = new EswcTag("pages");
    private static Tag tagStartPage = new EswcTag("pstart");
    private static Tag tagEndPage = new EswcTag("pend");
    private static Tag tagSection = new EswcTag("section");

    private EswcLogicalTree tree;
    private LogicalArea rootArea;
    private Vector<Area> leaves;
    private int curvol; //currently processed volume number
    private String curtitle;

    private Area subtitle;

    private int iTitle = -1;
    private int iShort = -1;
    private int iDates = -1;
    private int iCountry = -1;
    private int editorStart = -1;
    private int editorEnd = -1;
    private int paperStart = -1;
    private int paperEnd = -1;

    @Override
    public String getId()
    {
        return "CEUR.Logical";
    }

    @Override
    public String getName()
    {
        return "CEUR Logical Tree Builder";
    }

    @Override
    public String getDescription()
    {
        return "Logical structure builder for CEUR proceedings";
    }

    @Override
    public String[] getParamNames()
    {
        return new String[0];
    }

    @Override
    public ValueType[] getParamTypes()
    {
        return new ValueType[0];
    }

    //====================================================================================

    private void reset()
    {
        iTitle = -1;
        iShort = -1;
        iDates = -1;
        iCountry = -1;
        editorStart = -1;
        editorEnd = -1;
        paperStart = -1;
        paperEnd = -1;
        subtitle = null;
        paperIdCnt = 0;
    }

    @Override
    public LogicalAreaTree createLogicalTree(AreaTree areaTree)
    {
        reset();

        rootArea = createRoot(areaTree);
        tree = new EswcLogicalTree(areaTree);
        tree.setRoot(rootArea);

        leaves = new Vector<Area>();
        findLeaves(areaTree.getRoot(), leaves);

        scanLeaves();

        //addVTitle();
        try{
	        addIndexData();
	        analyzeShortNames();
	        addVDates();
	        addVCountry();
	        addEditors();
	        addPapers();
        }catch(Exception e){
        	e.printStackTrace();
        	throw e;
        }

        return tree;
    }

    private void findLeaves(Area root, Vector<Area> dest)
    {
        if (root.hasTag(tagSubtitle) && subtitle == null)
            subtitle = root;

        if (root.isLeaf())
        {
            dest.add(root);
        }
        else
        {
            for (int i = 0; i < root.getChildCount(); i++)
                findLeaves(root.getChildArea(i), dest);
        }
    }

    private void scanLeaves()
    {
        int i = 0;
        for (Area a : leaves)
        {
            if (iTitle == -1 && a.hasTag(tagVTitle, ms))
                iTitle = i;
            if (iShort == -1 && a.hasTag(tagVShort, ms))
                iShort = i;
            if (iDates == -1 && a.hasTag(tagVDate, ms))
                iDates = i;
            if (iCountry == -1 && a.hasTag(tagVCountry, ms))
                iCountry = i;
            if (a.hasTag(tagVEditor, ms))
            {
            	//System.out.println(a.getText());
                if (editorStart == -1) editorStart = i;
                editorEnd = i;
            }
            if (a.hasTag(tagTitle, ms) || a.hasTag(tagAuthor, ms) || a.hasTag(tagPages, ms))
            {
            	//System.out.println(a.getText());
                if (paperStart == -1) paperStart = i;
                paperEnd = i;
            }

            i++;
        }
    }

    private LogicalArea createRoot(AreaTree tree)
    {
        String uri = tree.getRoot().getAllBoxes().firstElement().getPage().getSourceURL().toString();
        curvol = Integer.parseInt(uri.substring("http://ceur-ws.org/Vol-".length(), uri.length() - 1));
        return new EswcLogicalArea(tree.getRoot(), uri, tagRoot);
    }

    //====================================================================================

    @SuppressWarnings("unused")
    private void addVTitle()
    {
        Area root = leaves.elementAt(iTitle);
        String text = root.getText();
        rootArea.appendChild(new EswcLogicalArea(root, text, tagVTitle));
        curtitle = text;
    }

    private void addIndexData()
    {
        String url = rootArea.getText();
        Matcher matcher = Pattern.compile("vol-[1-9][0-9]*").matcher(url.toLowerCase());
        if (matcher.find())
        {
            int vol = IndexFile.parseVol(matcher.group(0));
            SimpleDateFormat dfmt = new SimpleDateFormat("yyyy-MM-dd");
            curtitle = IndexFile.getTitle(vol);
            rootArea.appendChild(new EswcLogicalArea(leaves.elementAt(iTitle), curtitle, tagVTitle));
            rootArea.appendChild(new EswcLogicalArea(leaves.elementAt(iTitle), dfmt.format(IndexFile.getPubDate(vol)), tagPublished));
            List<Integer> related = IndexFile.getRelated(vol);
            if (related != null)
            {
                for (int rel : related)
                    rootArea.appendChild(new EswcLogicalArea(leaves.elementAt(iTitle), "http://ceur-ws.org/Vol-" + rel + "/", tagRelated));
            }
        }
    }

    private void analyzeShortNames()
    {
        //gather the abbreviations around the title
        Vector<String> titleShorts = null;
        if (iShort != -1)
        {
            Area root = leaves.elementAt(iShort);
            titleShorts = AreaUtils.findShortTitles(root);
        }
        else
            titleShorts = new Vector<String>(); //no short names around the title?

        //analyze the subtitle
        SubtitleParser sp;
        if (subtitle != null)
        {
            sp = new SubtitleParser(subtitle.getText(" "), titleShorts);
        }
        else
        {
            log.warn("No subtitle!");
            sp = new SubtitleParser("", titleShorts);
        }

        //cross check
        Set<Event> ws = sp.getWorkshops();
        Set<Event> iws = IndexFile.getShortNames(curvol);
        if (!ws.equals(iws))
        {
            Set<Event> cws = new HashSet<Event>();
            //try to complete missing orders from index
            for (Event ev : ws)
            {
                if (ev.order == -1)
                {
                    Event iev = findEventByName(iws, ev.sname);
                    if (iev != null)
                    {
                        iev.title = ev.title;
                        cws.add(iev);
                    }
                    else
                        cws.add(ev);
                }
                else
                    cws.add(ev);
            }
            ws = cws;
        }
        if (!ws.equals(iws))
        {
            log.warn("Short name mismatch: {} x {}", ws, iws);
            IndexFile.setShortNames(curvol, ws);
        }

        String coloc = (sp.getColocEvent() != null) ? sp.getColocEvent().sname : "";
        String icoloc = IndexFile.getColoc(curvol);
        if (icoloc == null)
            icoloc = "";
        if (!coloc.equals(icoloc))
        {
            log.warn("Colocation mismatch: {} x {}", coloc, icoloc);
            IndexFile.setColoc(curvol, coloc);
        }

        //output acronyms
        for (Event ev : ws)
        {
            LogicalArea sa = new EswcLogicalArea(subtitle, ev.sname, tagVShort);
            rootArea.appendChild(sa);
            if (ev.order > 0)
                sa.appendChild(new EswcLogicalArea(subtitle, String.valueOf(ev.order), tagVOrder));
            String wt = curtitle;
            if (ws.size() > 1) //multiworkshop volume, use individual titles
            {
                if (ev.title != null)
                    wt = ev.title;
                else
                    wt = ev.sname;
            }
            sa.appendChild(new EswcLogicalArea(subtitle, wt, tagWTitle));
        }
        if (sp.getColocEvent() != null)
        {
            LogicalArea sa = new EswcLogicalArea(subtitle, sp.getColocEvent().sname, tagColoc);
            rootArea.appendChild(sa);
        }


    }

    private Event findEventByName(Set<Event> set, String name)
    {
        for (Event ev : set)
        {
            if (ev.sname.equals(name))
                return ev;
        }
        return null;
    }

    private void addVDates()
    {
        if (iDates != -1)
        {
            Area a = leaves.elementAt(iDates);
            DateTagger dt = new DateTagger();
            List<Date> dates = dt.extractDates(a.getText());
            SimpleDateFormat dfmt = new SimpleDateFormat("yyyy-MM-dd");

            if (dates.size() == 1)
            {
                dates.add(dates.get(0));
            }
            if (dates.size() == 2)
            {
                //cross-check with index
                Date[] idates = IndexFile.getDates(curvol);
                if (idates[0] != null && idates[1] != null)
                {
                    for (int i = 0; i < 2; i++)
                    {
                        Calendar c1 = Calendar.getInstance();
                        c1.setTime(dates.get(i));
                        Calendar c2 = Calendar.getInstance();
                        c2.setTime(idates[i]);

                        if (c1.get(Calendar.DAY_OF_MONTH) != c2.get(Calendar.DAY_OF_MONTH)
                                || c1.get(Calendar.MONTH) != c2.get(Calendar.MONTH)
                                || c1.get(Calendar.YEAR) != c2.get(Calendar.YEAR))
                        {
                            log.warn("Date mismatch: {} x {}", dates, idates);
                            if (c1.get(Calendar.DAY_OF_MONTH) == c2.get(Calendar.DAY_OF_MONTH)
                                    && c1.get(Calendar.MONTH) == c2.get(Calendar.MONTH)
                                    && c1.get(Calendar.YEAR) == 2015
                                    && c2.get(Calendar.YEAR) < 2015)
                            {
                                dates.set(i, idates[i]);
                                log.warn("Using {} " + idates[i]);
                            }
                        }
                        IndexFile.setDates(curvol, dates.get(0), dates.get(1));
                    }
                }
                else
                    log.warn("No dates in index file for vol {}", curvol);

                rootArea.appendChild(new EswcLogicalArea(a, dfmt.format(dates.get(0)), tagStartDate));
                rootArea.appendChild(new EswcLogicalArea(a, dfmt.format(dates.get(1)), tagEndDate));
            }
            else
                log.warn("Strange number of date values: {} in {}", dates, a.getText());
        }
        else
            log.warn("No dates found");
    }

    private void addVCountry()
    {
        if (iCountry != -1)
        {
            Area a = leaves.elementAt(iCountry);
            CountriesTagger ct = new CountriesTagger();
            List<String> countries = ct.extract(a.getText());
            if (countries.size() >= 1)
            {
                String uri = Countries.getCountryUri(countries.get(countries.size() - 1)); //use the last country
                rootArea.appendChild(new EswcLogicalArea(a, uri, tagVCountry));
            }
            if (countries.size() != 1)
                log.warn("Strange number of countries: {} in {}", countries, a.getText());
        }
        else
            log.warn("No country found");

    }

    //====================================================================================

    private void addEditors()
    {
        Vector<String> names = new Vector<String>();
        //extend editors till the end of the last line
        Area last = leaves.elementAt(editorEnd);
        while (editorEnd + 1 < leaves.size())
        {
            Area next = leaves.elementAt(editorEnd + 1);
            if (AreaUtils.isOnSameLineRoughly(last, next))
            {
                last = next;
                editorEnd++;
            }
            else
                break;
        }
        //find editor data
        Area curEd = null;
        StringBuilder textb = null;
        for (int i = editorStart; i <= editorEnd; i++)
        {
            Area a = leaves.elementAt(i);
            if (a.hasTag(tagVEditor, ms))
            {
                if (curEd != null)
                    names.addAll(saveEditor(curEd, textb.toString().trim()));
                curEd = a;
                textb = new StringBuilder(a.getText());
            }
            else
            {
                if (textb != null)
                    textb.append(a.getText());
            }
        }
        if (curEd != null)
            names.addAll(saveEditor(curEd, textb.toString().trim()));

        //cross-check with index file
        List<String> inames = IndexFile.getEditorNames(curvol);
        Vector<String> i1 = new Vector<String>(inames);
        i1.removeAll(names);
        Vector<String> i2 = new Vector<String>(names);
        i2.removeAll(inames);
        if (!i1.isEmpty() || !i2.isEmpty())
        {
            log.warn("Editors mismatch: {} x {} ~~ ({} / {})", names, inames, i1, i2);
            IndexFile.setEditorNames(curvol, names);
        }
    }

    /**
     * Saves the editor data to RDF.
     * @param editor
     * @param text
     * @return the extracted editor names
     */
    private List<String> saveEditor(Area editor, String text)
    {
        Vector<String> ret = new Vector<String>(3);
        //System.out.println("ED: " + text);
        //find the name
        int i = 0;
        text = text.replaceAll(", ", "").replaceAll("[*]", "");		//filter case like in vol-317
        while (i < text.length())
        {
            char ch = text.charAt(i);
            if (ch != '.' && ch != '-' && ch != '\''
                    && !Character.isLetter(ch)
                    && !Character.isSpaceChar(ch))
                break;
            i++;
        }
        if (i > 0)
        {
            String name = text.substring(0, i);
            String affil = text.substring(i).trim();
            while (affil.startsWith(","))
                affil = affil.substring(1).trim();
            while (affil.endsWith(","))
                affil = affil.substring(0, affil.length() - 1);

            if (affil.isEmpty())
            {
                Area follow = leaves.elementAt(editorEnd+1);
                if (AreaUtils.isNeighbor(editor, follow))
                {
                    String ftext = getTextOnLine(editorEnd+1, paperStart);
                    affil = ftext.trim();
                }
                else
                    log.warn("No affiliation for " + text);
            }

            //decode editor section in () if present
            String affsect = null;
            Matcher matcher = Pattern.compile("\\([a-zA-Z].+\\)$").matcher(affil);
            if (matcher.find())
            {
                String s = matcher.group(0);
                affsect = s.substring(1, s.length() - 1);
                affil = affil.substring(0, affil.length() - s.length()).trim();
            }

            //no affiliation but some section -- the section is probably affiliation
            if (affil.trim().length() == 0 && affsect != null)
            {
                affil = affsect;
                affsect = null;
            }

            //complete the affiliation when symbols are used
            affil = completeAffil(affil);
            String affs[] = splitAffilCountry(affil);
            affil = affs[0];

            String[] names = name.split("\\s+and\\s+"); //multiple names separated by 'and'?
            for (String curname : names)
            {
                LogicalArea aname = new EswcLogicalArea(editor, curname.trim(), tagVEditor);
                ret.add(curname.trim());
                rootArea.appendChild(aname);
                LogicalArea aaffil = new EswcLogicalArea(editor, affil.trim(), tagEAffil);
                aname.appendChild(aaffil);
                if (affs[1] != null)
                {
                    LogicalArea acountry = new EswcLogicalArea(editor, affs[1], tagECountry);
                    aname.appendChild(acountry);
                }
                if (affsect != null)
                {
                    aname.appendChild(new EswcLogicalArea(editor, affsect, tagSection));
                }
            }
        }
        else
            log.warn("Couldn't find editor name: {}", text);

        return ret;
    }

    private String completeAffil(String src)
    {
        if (src.length() > 0 && !Character.isLetter(src.charAt(0)))
        {
            src = src.trim();
            //remove () before the affiliation sign
            if (src.length() > 2 && src.charAt(0) == '(' && src.charAt(src.length() - 1) != ')')
            {
                int i = src.indexOf(')');
                if (i != -1)
                {
                    src = src.substring(i+1).trim();
                }
            }

            for (int i = editorEnd + 1; i < paperStart; i++)
            {
                final Area a = leaves.elementAt(i);
                final String s = a.getText();
                if (s.trim().startsWith(src))
                {
                    String ret = getAffilText(i, paperStart).trim();
                    ret = ret.substring(src.length()).trim();
                    return ret;
                }
            }
            log.warn("Couldn't find affiliation for " + src);
            return src;
        }
        else
            return src;
    }

    private String[] splitAffilCountry(String src)
    {
        String[] ret = new String[2];
        boolean found = false;
        String affil = new String(src.trim());
        while (affil.endsWith(","))
            affil = affil.substring(0, affil.length() - 1).trim();
        //try the last country separated by ","
        int pos = affil.lastIndexOf(",");
        if (pos > 0)
        {
            String cstr = affil.substring(pos + 1).trim().toLowerCase();
            String[] cands = cstr.split("[^A-Za-z0-9\\s\\.]");
            for (String cname : cands)
            {
                cname = cname.trim();
                while (cname.endsWith("."))
                    cname = cname.substring(0, cname.length() - 1).trim();
                String curi = Countries.getCountryUri(cname);
                if (curi != null)
                {
                    ret[0] = affil.substring(0, pos).trim();
                    ret[1] = curi;
                    found = true;
                }
            }

            if (!found)
            {
                log.warn("No country found in '{}' ({}?), let's try another way", affil, cands);
            }
        }

        if (!found)
        {
            LocationsTagger ltg = new LocationsTagger(1);
            Vector<String> cands = ltg.extract(affil);
            for (String cname : cands)
            {
                String curi = Countries.getCountryUri(cname.trim());
                if (curi != null)
                {
                    ret[0] = affil;
                    ret[1] = curi;
                    found = true;
                }
            }
        }

        if (!found)
        {
            ret[0] = affil;
            ret[1] = null;
            log.warn("No country position found in '{}', give up", affil);
        }

        return ret;
    }

    //====================================================================================

    private void addPapers()
    {
        Area curTitle = null;
        Area curAuthors = null;
        Area curPages = null;
        Area curSection = null;

        int paperI = -1;

        for (int i = paperStart; i <= paperEnd; i++)
        {
            Area a = leaves.elementAt(i);
            if (a.hasTag(tagTitle, ms) || a.hasTag(tagAuthor, ms) || a.hasTag(tagPages, ms))
            {
                if (curTitle == null && a.hasTag(tagTitle, ms))
                {
                    curTitle = a;
                    if (paperI == -1) paperI = i;
                }
                else if (curAuthors == null && a.hasTag(tagAuthor, ms))
                {
                    curAuthors = a;
                    if (paperI == -1) paperI = i;
                }
                else if (curPages == null && a.hasTag(tagPages, ms))
                    curPages = a;
                else if (paperI != -1)//some duplicate
                {
                    curSection = findSection(paperI);
                    savePaper(curTitle, curAuthors, curPages, curSection);
                    curTitle = null;
                    curAuthors = null;
                    curPages = null;
                    paperI = -1;
                    i--; //try the same area again
                }
            }
        }
        savePaper(curTitle, curAuthors, curPages, curSection);
    }

    private Area findSection(int start)
    {
        final float fsize = leaves.elementAt(start).getFontSize();
        final int bx = leaves.elementAt(start).getBounds().getX1();
        for (int i = start - 1; i > editorEnd; i--)
        {
            Area a = leaves.elementAt(i);
            if (a.getFontSize() > fsize || a.getBounds().getX1() < bx - 10)
            {
                if (a.getText().equalsIgnoreCase("Table of Contents"))
                    return null;
                else
                    return a;
            }
        }
        return null;
    }

    private void savePaper(Area title, Area authors, Area pages, Area curSection)
    {
        if (title != null && authors != null)
        {
            String pid = findPaperId(title, authors);
            if (pid != null)
            {
                LogicalArea ap = new EswcLogicalArea(title, pid, tagPaper);
                rootArea.appendChild(ap);

                LogicalArea at = new EswcLogicalArea(title, title.getText().trim(), tagTitle);
                ap.appendChild(at);
                String saut = authors.getText().trim();
                String names[] = saut.split("\\s*[,;]\\s*(and)?\\s*");
                for (String name : names)
                {
                    String nnames[] = name.split("\\s+and\\s+");
                    for (String nname : nnames)
                    {
                        LogicalArea aa = new EswcLogicalArea(authors, nname, tagAuthor);
                        ap.appendChild(aa);
                    }
                }
                if (pages != null)
                {
                    String[] pp = pages.getText().trim().split("\\s*\\p{Pd}\\s*");
                    if (pp.length == 2)
                    {
                        try {
                            int pi1 = Integer.parseInt(pp[0]);
                            int pi2 = Integer.parseInt(pp[1]);
                            LogicalArea ps = new EswcLogicalArea(pages, pp[0], tagStartPage);
                            ap.appendChild(ps);
                            LogicalArea pe = new EswcLogicalArea(pages, pp[1], tagEndPage);
                            ap.appendChild(pe);
                            LogicalArea pn = new EswcLogicalArea(pages, String.valueOf(pi2 - pi1 + 1), tagPages);
                            ap.appendChild(pn);
                        } catch (NumberFormatException e) {
                            log.warn("Invalid page numbers: {}", pages);
                        }
                    }
                    else if (pp.length == 1)
                    {
                        try {
                            Integer.parseInt(pp[0]);
                            LogicalArea ps = new EswcLogicalArea(pages, pp[0], tagStartPage);
                            ap.appendChild(ps);
                            LogicalArea pe = new EswcLogicalArea(pages, pp[0], tagEndPage);
                            ap.appendChild(pe);
                            LogicalArea pn = new EswcLogicalArea(pages, "1", tagPages);
                            ap.appendChild(pn);
                        } catch (NumberFormatException e) {
                            log.warn("Invalid page numbers: {}", pages);
                        }
                    }
                    else
                        log.warn("Invalid pages: {}", pages);
                }
                if (curSection != null)
                {
                    LogicalArea asec = new EswcLogicalArea(curSection, curSection.getText().trim(), tagSection);
                    ap.appendChild(asec);
                }
            }
            else
                log.error("Couldn't obtain paper id for {}", title);
        }
        else
            log.warn("Incomplete paper: {} : {}", title, authors);
    }

    private String getTextOnLine(int start, int end)
    {
        Area a = leaves.elementAt(start);
        StringBuilder sb = new StringBuilder(a.getText());
        int i = start + 1;
        while (i < end) //use all till end of line
        {
            Area next = leaves.elementAt(i);
            if (AreaUtils.isOnSameLineRoughly(a, next))
            {
                sb.append(next.getText());
                i++;
            }
            else
                break;
        }
        return sb.toString();
    }

    private String getAffilText(int start, int end)
    {
        Area strt = leaves.elementAt(start);
        StringBuilder sb = new StringBuilder(strt.getText());
        int i = start + 1;
        while (i < end) //use all till end of line
        {
            Area next = leaves.elementAt(i);
            if (AreaUtils.isOnSameLineRoughly(strt, next))
            {
                sb.append(next.getText());
            }
            else if (AreaUtils.isNeighbor(strt, next) && AreaUtils.isInSameColumn(strt, next)) //next line, same column, same group
            {
                String nt = next.getText().trim();
                if (nt.length() > 0)
                {
                    if (Character.isAlphabetic(nt.charAt(0)) && !nt.contains("proceedings"))
                    {
                        sb.append(", ");
                        sb.append(next.getText());
                        strt = next;
                    }
                    else
                        break;
                }
            }
            else
                break;
            i++;
        }
        return sb.toString();
    }

    private String findPaperId(Area title, Area authors)
    {
        Box box = title.getBoxes().firstElement();
        int top = box.getBounds().getY1();
        //try ID attribute
        String pid = null;
        Box cur = box;
        do
        {
            pid = cur.getAttribute("id");
            cur = cur.getParentBox();
        } while (pid == null && cur != null && cur.getBounds().getY1() - top < 20);
        if (pid != null)
        {
            //System.out.println("Found ID " + pid);
            return pid;
        }
        //try links
        String lnk = box.getAttribute("href");
        if (lnk == null)
        {
            //no link from title, try authors
            box = authors.getBoxes().firstElement();
            lnk = box.getAttribute("href");
            if (lnk != null && lnk.startsWith("http") && !lnk.contains("ceur-ws.org")) //ignore links outside of ceur-ws
                lnk = null;
        }
        if (lnk != null)
        {
            lnk = lnk.trim();
            File file = new File("/", lnk);
            String name = file.getName();
            if (name.toLowerCase().endsWith(".pdf"))
                name = name.substring(0, name.length() - 4);
            else if (name.toLowerCase().endsWith(".ps"))
                name = name.substring(0, name.length() - 3);
            else if (name.toLowerCase().endsWith(".ps.gz"))
                name = name.substring(0, name.length() - 6);
            else if (name.toLowerCase().endsWith(".html"))
                name = name.substring(0, name.length() - 5);

            if (!name.isEmpty())
                return name;
            else
            {
                log.warn("Empty paper id for title " + title);
                return generatePaperId();
            }
        }
        else
        {
            log.warn("Missing paper id (no id nor href) for title " + title);
            return generatePaperId();
        }
    }

    private String generatePaperId()
    {
        paperIdCnt++;
        return "paperX" + paperIdCnt;
    }

}
