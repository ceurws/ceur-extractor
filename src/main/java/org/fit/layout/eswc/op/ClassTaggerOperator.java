/**
 * ClassTaggerOperator.java
 *
 * Created on 24. 2. 2015, 14:03:05 by burgetr
 */
package org.fit.layout.eswc.op;

import org.fit.layout.impl.BaseOperator;
import org.fit.layout.model.Area;
import org.fit.layout.model.AreaTree;
import org.fit.layout.model.Box;

/**
 * This operator assigns tags to the areas based on their CEUR class annotations (microformats).
 * 
 * @author burgetr
 */
public class ClassTaggerOperator extends BaseOperator
{

    private final String[] paramNames = {};
    private final ValueType[] paramTypes = {};
    
    public ClassTaggerOperator()
    {
    }
    
    @Override
    public String getId()
    {
        return "Ceur.Tag.Class";
    }
    
    @Override
    public String getName()
    {
        return "Tag CEUR microformats";
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

    //==============================================================================

    @Override
    public void apply(AreaTree atree)
    {
        apply(atree, atree.getRoot());
    }

    @Override
    public void apply(AreaTree atree, Area root)
    {
        //add tags based on classes
        recursivelyAddTags(root);
    }
    
    private void recursivelyAddTags(Area root)
    {
        if (root.isLeaf())
        {
            addAreaTags(root);
        }
        else
        {
            for (int i = 0; i < root.getChildCount(); i++)
                recursivelyAddTags(root.getChildArea(i));
        }
    }
    
    private void addAreaTags(Area area)
    {
        for (Box box : area.getBoxes())
        {
            String cstr = box.getAttribute("class");
            if (cstr != null)
            {
                String[] clss = cstr.split("\\s");
                for (String cls : clss)
                {
                    String tagname = CeurTag.getMapping(cls);
                    if (tagname != null)
                    {
                        CeurTag tag = new CeurTag(tagname);
                        area.addTag(tag, 1.0f); //we pretty believe this
                    }
                }
            }
        }
    }

}
