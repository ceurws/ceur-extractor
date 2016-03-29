/**
 * ShortNameTagger.java
 *
 * Created on 10. 4. 2015, 11:36:13 by burgetr
 */
package org.fit.layout.eswc;

import java.util.Vector;

import org.fit.layout.classify.Tagger;
import org.fit.layout.classify.TextTag;
import org.fit.layout.eswc.op.AreaUtils;
import org.fit.layout.model.Area;
import org.fit.layout.model.Tag;

/**
 * 
 * @author burgetr
 */
public class ShortNameTagger implements Tagger
{
    
    public TextTag getTag()
    {
        return new TextTag("short", this);
    }

    public double getRelevance()
    {
        return 0.7;
    }
    
    public boolean belongsTo(Area node)
    {
        if (node.isLeaf())
        {
            return !AreaUtils.findShortTitles(node).isEmpty();
        }
        return false;
    }
    
    public boolean allowsContinuation(Area node)
    {
        return false;
    }

    public boolean allowsJoining()
    {
        return false;
    }
    
    public boolean mayCoexistWith(Tag other)
    {
        return true;
    }
    
    public Vector<String> extract(String src)
    {
        return AreaUtils.findShortTitles(src);
    }

}
