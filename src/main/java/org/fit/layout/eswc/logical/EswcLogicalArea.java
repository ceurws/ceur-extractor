/**
 * EswcLogicalArea.java
 *
 * Created on 19. 3. 2015, 13:48:01 by burgetr
 */
package org.fit.layout.eswc.logical;

import org.fit.layout.impl.DefaultLogicalArea;
import org.fit.layout.model.Area;
import org.fit.layout.model.Tag;

/**
 * 
 * @author burgetr
 */
public class EswcLogicalArea extends DefaultLogicalArea
{

    public EswcLogicalArea(Area area)
    {
        super(area);
    }
    
    public EswcLogicalArea(Area area, String text)
    {
        super(area, text);
    }
    
    public EswcLogicalArea(Area area, String text, Tag tag)
    {
        super(area, text);
        setMainTag(tag);
    }
    
}
