/**
 * FindTitlesOperator.java
 *
 * Created on 4. 3. 2015, 21:12:33 by burgetr
 */
package org.fit.layout.eswc.op;

import java.util.Collections;
import java.util.Comparator;
import java.util.Vector;

import org.fit.layout.impl.BaseOperator;
import org.fit.layout.model.Area;
import org.fit.layout.model.AreaTree;
import org.fit.layout.model.Rectangular;
import org.fit.segm.grouping.AreaImpl;

/**
 * 
 * @author burgetr
 */
public class FindTitlesOperator extends BaseOperator
{
    private final String[] paramNames = {};
    private final ValueType[] paramTypes = {};

    private Rectangular bounds; //the bounds to operate on
    private Rectangular resultBounds;
    
    
    public FindTitlesOperator()
    {
        this.bounds = null; //use the whole page
    }
    
    public FindTitlesOperator(Rectangular bounds)
    {
        this.bounds = bounds;
    }
    
    @Override
    public String getId()
    {
        return "Eswc.Tag.Titles";
    }
    
    @Override
    public String getName()
    {
        return "Tag workshop titles";
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

    @Override
    public void apply(AreaTree atree)
    {
        apply(atree, atree.getRoot());
    }

    @Override
    public void apply(AreaTree atree, Area root)
    {
        Vector<Area> leaves = new Vector<Area>();
        findLeaves(root, leaves);
        sortLeaves(leaves);
        
        /*System.out.println("MAX:");
        for (int i = 0; i < 50 && i < leaves.size(); i++)
        {
            Area a = leaves.elementAt(i);
            System.out.println(a.getFontSize() + " " + a.getFontWeight() + " " + a);
        }*/
        
        //find start and end of the title
        float maxsize = leaves.firstElement().getFontSize(); //largest font size
        int maxlen = 0;
        int first = -1;
        int last = -1;
        int cur = 0;
        //find longest text of the maximal font size
        for (Area a : leaves)
        {
            if (a.getFontSize() == maxsize)
            {
                final String text = a.getText().trim();
                if (text.length() > maxlen)
                {
                    maxlen = text.length();
                    first = cur;
                }
            }
            cur++;
        }
        //expand up
        while (first > 0)
        {
            Area before = leaves.elementAt(first - 1);
            if (before != null && before.getFontSize() == maxsize)
                first--;
            else
                break;
        }
        //expand down
        if (first >= 0)
        {
            AreaImpl fa = (AreaImpl) leaves.elementAt(first);
            resultBounds = fa.getBounds();
            Rectangular pos = fa.getGridPosition();
            //System.out.println("FIRST: " + fa);
            //find the last index
            last = first;
            for (int i = first + 1; i < leaves.size(); i++)
            {
                final AreaImpl a = (AreaImpl) leaves.elementAt(i);
                if (a.getFontSize() == maxsize)
                {
                    last = i;
                    pos.expandToEnclose(a.getGridPosition());
                    fa.joinArea(a, pos, true);
                    resultBounds.expandToEnclose(a.getBounds());
                }
                else
                    break;
            }
            //System.out.println("LAST: " + leaves.elementAt(last));
            
            fa.addTag(new EswcTag("vtitle"), 0.6f);
        }
        //find short names of the same size
        for (Area a : leaves)
        {
            if (a.getFontSize() == maxsize)
            {
                Vector<String> snames = AreaUtils.findShortTitles(a);
                if (!snames.isEmpty())
                {
                    a.addTag(new EswcTag("vshort"), 0.7f);
                    break;
                }
            }
        }
        
       
    }
    
    //==============================================================================
    
    private void findLeaves(Area root, Vector<Area> dest)
    {
        if (root.isLeaf())
        {
            if (bounds == null || root.getBounds().intersects(bounds))
                dest.add(root);
        }
        else
        {
            for (int i = 0; i < root.getChildCount(); i++)
                findLeaves(root.getChildArea(i), dest);
        }
    }
    
    private void sortLeaves(Vector<Area> dest)
    {
        Collections.sort(dest, new Comparator<Area>()
        {
            @Override
            public int compare(Area o1, Area o2)
            {
                return Math.round(o2.getFontSize()*100 - o1.getFontSize()*100);
            }
        });
    }
    
}
