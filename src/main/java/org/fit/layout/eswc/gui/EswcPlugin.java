/**
 * EswcPlugin.java
 *
 * Created on 28. 2. 2015, 22:39:21 by burgetr
 */
package org.fit.layout.eswc.gui;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import javax.swing.JButton;
import javax.swing.JToolBar;

import org.fit.layout.gui.Browser;
import org.fit.layout.gui.BrowserPlugin;
import org.fit.layout.model.Area;
import org.fit.layout.model.Tag;

/**
 * 
 * @author burgetr
 */
public class EswcPlugin implements BrowserPlugin
{
    private static final float MIN_TAG_SUPPORT = 0.3f;
    
    private Browser browser;
    private JToolBar toolbar;
    private JButton classesButton;
    private JButton ceurButton;

    @Override
    public boolean init(Browser browser)
    {
        this.browser = browser;
        this.browser.addToolBar(getToolbar());
        return true;
    }

    private JToolBar getToolbar()
    {
        if (toolbar == null)
        {
            toolbar = new JToolBar("ESWC");
            toolbar.add(getClassesButton());
            toolbar.add(getCeurButton());
        }
        return toolbar;
    }

    private JButton getClassesButton()
    {
        if (classesButton == null)
        {
            classesButton = new JButton("ESWC");
            classesButton.addActionListener(new ActionListener()
            {
                public void actionPerformed(ActionEvent e)
                {
                    Area node = browser.getSelectedArea();
                    if (node != null)
                        colorizeTags(node, "ESWC");
                }
            });
        }
        return classesButton;
    }
    
    private JButton getCeurButton()
    {
        if (ceurButton == null)
        {
            ceurButton = new JButton("CEUR");
            ceurButton.addActionListener(new ActionListener()
            {
                public void actionPerformed(ActionEvent e)
                {
                    Area node = browser.getSelectedArea();
                    if (node != null)
                        colorizeTags(node, "CEUR");
                }
            });
        }
        return ceurButton;
    }
    
    //=================================================================
    
    private void colorizeTags(Area root, String type)
    {
        recursiveColorizeTags(root, type);
        browser.updateDisplay();
    }
    
    private void recursiveColorizeTags(Area root, String type)
    {
        //find tags of the given type
        Set<Tag> tags = new HashSet<Tag>();
        for (Map.Entry<Tag, Float> entry : root.getTags().entrySet())
        {
            if (entry.getValue() >= MIN_TAG_SUPPORT && entry.getKey().getType().equals(type))
                tags.add(entry.getKey());
        }
        //display the tags
        browser.getOutputDisplay().colorizeByTags(root, tags);
        for (Area child : root.getChildAreas())
            recursiveColorizeTags(child, type);
    }
    
}
