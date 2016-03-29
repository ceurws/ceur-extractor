/**
 * CountriesTagger.java
 *
 * Created on 30. 3. 2015, 13:30:19 by burgetr
 */
package org.fit.layout.eswc;

import java.util.Vector;

import org.fit.layout.classify.Tagger;
import org.fit.layout.classify.TextTag;
import org.fit.layout.model.Area;
import org.fit.layout.model.Tag;

/**
 * 
 * @author burgetr
 */
public class CountriesTagger implements Tagger
{
    
    public TextTag getTag()
    {
        return new TextTag("countries", this);
    }

    public double getRelevance()
    {
        return 0.95;
    }
    
    public boolean belongsTo(Area node)
    {
        if (node.isLeaf())
        {
            String text = node.getText();
            return !Countries.getCountryNames(text).isEmpty();
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
        return new Vector<String>(Countries.getCountryNames(src));
    }
}
