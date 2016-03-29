/**
 * EswcTag.java
 *
 * Created on 28. 2. 2015, 21:30:11 by burgetr
 */
package org.fit.layout.eswc.op;

import org.fit.layout.impl.DefaultTag;

/**
 * An ESWC tag used for tagging the results.
 *  
 * @author burgetr
 */
public class EswcTag extends DefaultTag
{

    public EswcTag(String value)
    {
        super(value);
        setType("ESWC");
    }

}
