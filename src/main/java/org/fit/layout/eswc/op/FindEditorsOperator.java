/**
 * FindEditorsOperator.java
 *
 * Created on 6. 3. 2015, 15:13:45 by burgetr
 */
package org.fit.layout.eswc.op;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Vector;

import org.fit.layout.classify.StyleCounter;
import org.fit.layout.impl.BaseOperator;
import org.fit.layout.impl.DefaultTag;
import org.fit.layout.model.Area;
import org.fit.layout.model.AreaTree;
import org.fit.layout.model.Rectangular;
import org.fit.layout.model.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Finds the editor names in the given area of the page.
 * 
 * @author burgetr
 */
public class FindEditorsOperator extends BaseOperator
{
    private static Logger log = LoggerFactory.getLogger(FindEditorsOperator.class);
    private static final String TT = "FitLayout.TextTag";
    
    private final String[] paramNames = {};
    private final ValueType[] paramTypes = {};
    private ArrayList<String> EDITORS = new ArrayList<>(Arrays.asList("1260", "989"));
    private String curvol;

    private Rectangular bounds;
    private Rectangular resultBounds;
    private boolean keepGroup = false;
    
    
    public FindEditorsOperator()
    {
        this(0, 300, 1200, 600); //just a guess
    }
    
    public FindEditorsOperator(int x1, int y1, int x2, int y2)
    {
        bounds = new Rectangular(x1, y1, x2, y2);
    }
    
    public FindEditorsOperator(Rectangular r)
    {
        bounds = new Rectangular(r);
    }
    
    private void getCurVol(AreaTree tree)
    {
        String uri = tree.getRoot().getAllBoxes().firstElement().getPage().getSourceURL().toString();
        curvol = uri.substring("http://ceur-ws.org/Vol-".length(), uri.length() - 1);
        //System.out.println("Current Vol is : " + curvol);
    }
    
    @Override
    public String getId()
    {
        return "Eswc.Tag.Editors";
    }
    
    @Override
    public String getName()
    {
        return "Tag workshop editors";
    }

    @Override
    public String getDescription()
    {
        return "";
    }

    @Override
    public String[] getParamNames()
    {
        return paramNames;
    }

    @Override
    public ValueType[] getParamTypes()
    {
        return paramTypes;
    }

    public Rectangular getBounds()
    {
        return bounds;
    }

    public Rectangular getResultBounds()
    {
        return resultBounds;
    }

    public void setKeepGroup(boolean b)
    {
        keepGroup = b;
    }
    
    //==============================================================================

    @Override
    public void apply(AreaTree atree)
    {
        apply(atree, atree.getRoot());
    }

    @Override
    public void apply(AreaTree atree, Area root)
    {
        resultBounds = null;
        //find tagged names in the area
        Vector<Area> names = new Vector<Area>();
        Tag tag = new DefaultTag(TT, "persons");
        float support = 0.5f;
        findTagsInArea(root, bounds, tag, support, true, names);
        getCurVol(atree);

        
        if (names.isEmpty()) //no names found -- try again with lower support (to obey some uncertain hints)
        {
            support = 0.25f;
            findTagsInArea(root, bounds, tag, support, true, names);
        }
        
        if (!names.isEmpty())
        {
            //find the group containing the last name discovered
            Vector<Area> leaves = new Vector<Area>();
            findLeavesInArea(root, bounds, leaves);
            int last = leaves.indexOf(names.lastElement());
            
            //go until the beginning of the group
            int first = last;
            Area prev = names.lastElement();
            for (int i = last - 1; i >= 0; i--)
            {
                Area cur = leaves.elementAt(i);
                if (!keepGroup || AreaUtils.isNeighbor(cur, prev))
                {
                    first = i;
                    prev = cur;
                }
                //else continue because some of the previous boxes may be a neighbor too 
            }
            //go until the end of the group
            prev = names.lastElement();
            for (int i = last + 1; i < leaves.size(); i++)
            {
                Area cur = leaves.elementAt(i);
                if (AreaUtils.isNeighbor(cur, prev))
                {
                    last = i;
                    prev = cur;
                }
            }
            log.debug("Editors start: {} end: {}", leaves.elementAt(first), leaves.elementAt(last));

            //check if there are links to at least some author
            boolean authorsLinked = false;
            for (int i = first; i <= last; i++)
            {
                Area a = leaves.elementAt(i);
                if (a.hasTag(tag, support) && AreaUtils.isLink(a))
                {
                    authorsLinked = true;
                    break;
                }
            }
            
            //build statistics about names
            prev = null;
            int sameline = 0;
            int nextline = 0;
            int other = 0;
            int minx = -1;
            int multiPerson = -1;
            StyleCounter<FontNodeStyle> estyles = new StyleCounter<FontNodeStyle>();
            for (int i = first; i <= last; i++)
            {
                Area a = leaves.elementAt(i);
                //when some names are links, use only those for statistics 
                if (a.hasTag(tag, support) && (!authorsLinked || AreaUtils.isLink(a)))
                {
                    estyles.add(new FontNodeStyle(a));
                    if (multiPerson == -1 && a.getText().contains(" and ")) //multiple persons separated by 'and'
                        multiPerson = i;
                    final int x = a.getTopology().getPosition().getX1();
                    if (prev != null)
                    {
                        if (AreaUtils.isOnSameLine(prev, a))
                            sameline++;
                        else if (AreaUtils.isInSameColumn(prev, a))
                            nextline++;
                        else
                            other++;
                        if (x < minx)
                            minx = x;
                    }
                    else
                        minx = x;
                    prev = a;
                }
            }
            List<FontNodeStyle> mstyles = estyles.getMostFrequentAll();
            //use the largest font size if there are multiple styles of the same frequency
            FontNodeStyle estyle = null;
            for (FontNodeStyle st : mstyles)
            {
            	if(EDITORS.contains(curvol)){
            		estyle = new FontNodeStyle(leaves.elementAt(1));
            		break;
            	}
                if (estyle == null || st.getFontSize() > estyle.getFontSize())
                    estyle = st;
            }
            log.info("Layout: same line {}, next line {}, other {}, minx {}, style {}, linked {}", sameline, nextline, other, minx, estyle, authorsLinked);
            
            //tag the names according to the layout
            if (sameline == 0 && nextline == 0 && multiPerson != -1) //probably a single author area
            {
                Area a = leaves.elementAt(multiPerson);
                a.addTag(new EswcTag("veditor"), 0.6f);
            }
            else
            {
                for (int i = first; i <= last; i++)
                {
                    Area a = leaves.elementAt(i);
                    String text = a.getText().trim();
                    boolean found = false;
                    //System.out.println("Test" + a);
                    //System.out.println("Outer: " + a.getText());
                    if (text.length() > 0 && estyle.equals(new FontNodeStyle(a))) //&& estyle.equals(new FontNodeStyle(a)), changed because 1260
                    {
                    	//System.out.println("Inter: " + a.getText());
                        if (nextline >= sameline) //probably names on separate lines
                        {
                            if (a.getTopology().getPosition().getX1() == minx)
                            {
                                if (!Character.isAlphabetic(text.charAt(0))) //not a name in the first line -- stop tagging
                                    break;
                                //System.out.println("Editors Tag: "+a.toString());
                                a.addTag(new EswcTag("veditor"), 0.7f);
                                found = true;
                            }
                        }
                        else //multiple names on lines
                        {
                            //TODO some conditions?
                            a.addTag(new EswcTag("veditor"), 0.7f);
                            found = true;
                        }
                    }
                    if (found)
                    {
                        if (resultBounds == null)
                            resultBounds = new Rectangular(a.getBounds());
                        else
                            resultBounds.expandToEnclose(a.getBounds());
                    }
                }
            }
            
        }
        else
            log.warn("Could not find any names for editors!");
        
    }
    
    //==============================================================================
    
    private void findLeavesInArea(Area root, Rectangular limit, Vector<Area> dest) 
    {
        if (root.isLeaf() && root.getBounds().intersects(limit))
            dest.add(root);
        for (int i = 0; i < root.getChildCount(); i++)
            findLeavesInArea(root.getChildArea(i), limit, dest);
    }
    
    private void findTagsInArea(Area root, Rectangular limit, Tag tag, float minSupport, 
                                boolean startWithLetter, Vector<Area> dest) 
    {
        if (root.hasTag(tag, minSupport) && root.getBounds().intersects(limit))
        {
            if (startWithLetter)
            {
                String text = root.getText().trim();
                if (!text.isEmpty() && Character.isAlphabetic(text.codePointAt(0)))
                    dest.add(root);
            }
            else
                dest.add(root);
        }
        for (int i = 0; i < root.getChildCount(); i++)
            findTagsInArea(root.getChildArea(i), limit, tag, minSupport, startWithLetter, dest);
    }
    
    
}
