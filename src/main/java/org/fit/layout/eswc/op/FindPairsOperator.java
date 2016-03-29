/**
 * FindPairsOperator.java
 *
 * Created on 28. 2. 2015, 21:26:03 by burgetr
 */
package org.fit.layout.eswc.op;

import java.util.ArrayList;
import java.util.Arrays;

import org.fit.layout.classify.NodeStyle;
import org.fit.layout.classify.StyleCounter;
import org.fit.layout.eswc.logical.EswcLogicalArea;
import org.fit.layout.impl.BaseOperator;
import org.fit.layout.impl.DefaultTag;
import org.fit.layout.model.Area;
import org.fit.layout.model.AreaTree;
import org.fit.layout.model.LogicalArea;
import org.fit.layout.model.Rectangular;
import org.fit.layout.model.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Finds and tags the title/authors pairs.
 * 
 * @author burgetr
 */
public class FindPairsOperator extends BaseOperator
{
    private static Logger log = LoggerFactory.getLogger(FindPairsOperator.class);
    private static final String TT = "FitLayout.TextTag";
    
    private final String[] paramNames = {};
    private final ValueType[] paramTypes = {};
    private ArrayList<String> VOLLIST1 = new ArrayList<>(Arrays.asList("120", "88", "84", "41", "35", "18", "17", "12"));
    private ArrayList<String> VOLLIST2 = new ArrayList<>(Arrays.asList("331", "299"));
    
    //params
    private boolean useSiblings;
    
    //tags to compare to
    private Tag tpersons = new DefaultTag(TT, "persons");
    private Tag ttitle = new DefaultTag(TT, "title");
    private Tag eauthors = new EswcTag("authors");
    private Tag etitle = new EswcTag("title");
    private Tag vtitle = new EswcTag("vtitle");

    //statistics
    private int tacnt = 0; //title-author pairs
    private int atcnt = 0; //author-title pairs
    private int sidecnt = 0; //placed side-by side
    private int belowcnt = 0; //placed below
    private String curvol = "";
    private StyleCounter<NodeStyle> tstyles;
    private StyleCounter<NodeStyle> astyles;
    
    private Rectangular bounds; //bounds to operate on
    private Rectangular resultBounds;
    
    public FindPairsOperator()
    {
        this(null);
    }
    
    public FindPairsOperator(Rectangular bounds)
    {
        useSiblings = true;
        this.bounds = bounds;
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
        return "Eswc.Tag.Pairs";
    }
    
    @Override
    public String getName()
    {
        return "Tag title/authors pairs";
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

    public Rectangular getResultBounds()
    {
        return resultBounds;
    }

    //==============================================================================

    public void reset()
    {
        tacnt = 0;
        atcnt = 0;
        sidecnt = 0;
        belowcnt = 0;
        tstyles = new StyleCounter<NodeStyle>();
        astyles = new StyleCounter<NodeStyle>();
        resultBounds = null;
    }
    
    @Override
    public void apply(AreaTree atree)
    {
        apply(atree, atree.getRoot());
    }

    @Override
    public void apply(AreaTree atree, Area root)
    {
        reset();
        getCurVol(atree);
        
        //add tags to pairs based on their text tags
        gatherStatistics(root, 0.2f);
        log.info("Pairs count: TA={}, AT={}", tacnt, atcnt);
        log.info("Placement: side={}, below={}", sidecnt, belowcnt);
        log.info("Title st: " + tstyles.getMostFrequent());
        log.info("Author st: " + astyles.getMostFrequent());
        addTags(root, 0.8f, false);
        addTags(root, 0.8f, true); //add uncertain combinations
    }
    
    //==============================================================================
    
    private void gatherStatistics(Area root, float tprob)
    {
        if (root.getParentArea() != null && isIn(root)  && (VOLLIST1.contains(curvol) || acceptableTags(root, 0.0f, true)))// 
        {
            //try to find a neighbor area
            Area aa = findAlignedPreviousSibling(root, 5);
            //check the tags
            boolean found = false;
            if (aa != null && (VOLLIST2.contains(curvol) || acceptableTags(aa, 0.0f, true))) // && acceptableTags(aa, 0.0f, true)
            {
                if ((root.hasTag(tpersons) && !aa.hasTag(tpersons))
                    || (!root.hasTag(ttitle) && aa.hasTag(ttitle)))
                {
                    //title - authors
                	//System.out.println(aa);
                    aa.addTag(etitle, tprob);
                    root.addTag(eauthors, tprob);
                    tstyles.add(new NodeStyle(aa));
                    astyles.add(new NodeStyle(root));
                    tacnt++;
                    found = true;
                }
                else if ((root.hasTag(ttitle) && !aa.hasTag(ttitle))
                         || (!root.hasTag(tpersons) && aa.hasTag(tpersons)))
                {
                    //authors - title
                	//System.out.println(aa);
                    aa.addTag(eauthors, tprob);
                    root.addTag(etitle, tprob);
                    astyles.add(new NodeStyle(aa));
                    tstyles.add(new NodeStyle(root));
                    atcnt++;
                    found = true;
                }
                //other cases - will resolve later
            }
            if (found)
            {
                //placement statistics
                if (isAtSide(aa, root))
                    sidecnt++;
                else
                    belowcnt++;
            }
        }
        
        for (int i = 0; i < root.getChildCount(); i++)
            gatherStatistics(root.getChildArea(i), tprob);
    }

    private void addTags(Area root, float tprob, boolean allowUnsure)
    {
        if (root.getParentArea() != null && isIn(root) && acceptableTags(root, 0.5f, false) 
                && !root.getText().trim().isEmpty())
        {
            //try to find a neighbor area
            Area aa = findPairArea(root);
            //check the tags
            if (aa != null && acceptableTags(aa, 0.5f, false) && !aa.getText().trim().isEmpty())
            {
                if ((sidecnt > belowcnt && isAtSide(aa, root))
                    || (sidecnt <= belowcnt && !isAtSide(aa, root))) //required mutual positions
                {
                    //determine the expected order of the areas
                    Area atitle, aauth;
                    if (tacnt > atcnt) //title-author
                    {
                        atitle = aa;
                        aauth = root;
                    }
                    else //author-title
                    {
                        aauth = aa;
                        atitle = root;
                    }
                    
                    boolean found = false;
                    if (atitle.hasTag(ttitle) && aauth.hasTag(tpersons)) //no doubt
                    {
                        atitle.addTag(etitle, tprob);
                        aauth.addTag(eauthors, tprob);
                        found = true;
                    }
                    else if (allowUnsure)
                    {
                        NodeStyle stitle = new NodeStyle(atitle);
                        NodeStyle sauth = new NodeStyle(aauth);
                        if (atitle.hasTag(ttitle) && stitle.equals(tstyles.getMostFrequent())) 
                        {
                            atitle.addTag(etitle, tprob);
                            aauth.addTag(eauthors, tprob - 0.2f);
                            found = true;
                            //System.out.println("Uncertain1: " + aauth + " :: " + atitle);
                        }
                        else if (aauth.hasTag(tpersons) && sauth.equals(astyles.getMostFrequent()))
                        {
                            atitle.addTag(etitle, tprob - 0.2f);
                            aauth.addTag(eauthors, tprob);
                            found = true;
                            //System.out.println("Uncertain2: " + aauth + " :: " + atitle);
                        }
                    }
                    
                    if (found)
                    {
                        updateBounds(atitle);
                        updateBounds(aauth);
                    }
                }
            }
        }
        
        for (int i = 0; i < root.getChildCount(); i++)
            addTags(root.getChildArea(i), tprob, allowUnsure);
    }
    
    //==============================================================================
    
    private Area findPairArea(Area root)
    {
        if (useSiblings)
            return findAlignedPreviousSibling(root, 5);
        else
            return findClosestAbove(root);
    }
    
    /**
     * Checks if the given area is in the bounds being processed
     * @param a
     * @return
     */
    private boolean isIn(Area a)
    {
        return bounds == null || a.getBounds().intersects(bounds); 
    }
    
    private boolean acceptableTags(Area a, float minsp, boolean requireTextTag)
    {
        //area is not yet tagged and has the appropriate text tags
        return (a.hasTag(tpersons) || a.hasTag(ttitle) || !requireTextTag) &&
               (!a.hasTag(eauthors, minsp) && !a.hasTag(etitle, minsp)) &&
               !a.hasTag(vtitle); //ignore already recognized volume title
    }
    
    private boolean isAtSide(Area a1, Area a2)
    {
        final Rectangular gp1 = a1.getTopology().getPosition();
        final Rectangular gp2 = a2.getTopology().getPosition();
        return (gp1.getX1() != gp2.getX1());
    }
    
    private Area findAlignedPreviousSibling(Area a, int minlength)
    {
        //try to look about 10 elements back for finding the aligned sibling TODO
        Area cur = a;
        for (int i = 0; i < 10; i++)
        {
            cur = cur.getPreviousSibling();
            if (cur != null)
            {
                if (AreaUtils.isAligned(a, cur) && AreaUtils.isNeighbor(a, cur) && cur.getText().length() >= minlength)
                    return cur;
            }
            else
                break;
        }
        return null;
    }
    
    private Area findClosestAbove(Area a)
    {
        final Area parent = a.getParentArea();
        Rectangular gp = a.getTopology().getPosition();
        int y = gp.getY1();
        int mindif = Integer.MAX_VALUE;
        Area ret = null;
        if (y > 0)
        {
            //find closest left-aligned child above
            for (int i = 0; i < parent.getChildCount(); i++)
            {
                final Area child = parent.getChildArea(i);
                Rectangular cgp = child.getTopology().getPosition();
                if (cgp.getX1() == gp.getX1() && cgp.getY2() < y)
                {
                    final int dif = y - cgp.getY2();
                    if (dif < mindif)
                    {
                        ret = child;
                        mindif = dif;
                    }
                }
            }
            //sanity check: should be at most one line above
            if (ret != null)
            {
                int dy = a.getBounds().getY1() - ret.getBounds().getY2();
                if (dy > a.getBounds().getHeight() / 2)
                {
                    System.out.println("Too far " + a + " --- " + ret);
                    ret = null;
                }
            }
        }
        return ret;
    }

    private void updateBounds(Area a)
    {
        if (resultBounds == null)
            resultBounds = new Rectangular(a.getBounds());
        else
            resultBounds.expandToEnclose(a.getBounds());
    }
    
}
