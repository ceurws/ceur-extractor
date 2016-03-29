/**
 * EswcLogicalTree.java
 *
 * Created on 19. 3. 2015, 22:54:34 by burgetr
 */
package org.fit.layout.eswc.logical;

import org.fit.layout.model.AreaTree;
import org.fit.layout.model.LogicalArea;
import org.fit.layout.model.LogicalAreaTree;

/**
 * 
 * @author burgetr
 */
public class EswcLogicalTree implements LogicalAreaTree
{
    private AreaTree atree;
    private LogicalArea root;
    
    public EswcLogicalTree(AreaTree atree)
    {
        this.atree = atree;
    }
    
    public AreaTree getAreaTree()
    {
        return atree;
    }

    @Override
    public LogicalArea getRoot()
    {
        return root;
    }

    public void setRoot(LogicalArea root)
    {
        this.root = root;
    }

}
