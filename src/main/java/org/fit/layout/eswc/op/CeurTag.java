/**
 * CeurTag.java
 *
 * Created on 24. 2. 2015, 14:08:07 by burgetr
 */
package org.fit.layout.eswc.op;

import java.util.HashMap;
import java.util.Map;

import org.fit.layout.impl.DefaultTag;

/**
 * A tag assigned based on the CEUR microformat class.
 * 
 * @author burgetr
 */
public class CeurTag extends DefaultTag
{

    private static Map<String, String> mapping;
    
    static {
        mapping = new HashMap<String, String>();
        mapping.put("CEURTITLE", "title");
        mapping.put("CEURPAGES", "pages");
        mapping.put("CEURAUTHORS", "authors");
        
        mapping.put("CEURSESSION", "session");
        
        mapping.put("CEURVOLEDITOR", "veditor");
        mapping.put("CEURVOLTITLE", "vtitle");
        mapping.put("CEURVOLACRONYM", "vacro");
    }

    public static String getMapping(String className)
    {
        return mapping.get(className.toUpperCase());
    }
    
    public CeurTag(String value)
    {
        super(value);
        setType("CEUR");
    }

}
