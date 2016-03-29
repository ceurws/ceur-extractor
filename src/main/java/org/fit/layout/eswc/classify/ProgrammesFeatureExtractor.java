/**
 * ProgrammesFeatureExtractor.java
 *
 * Created on 25. 2. 2015, 16:15:52 by burgetr
 */
package org.fit.layout.eswc.classify;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import org.fit.layout.classify.DefaultFeatureExtractor;
import org.fit.layout.model.Area;
import org.fit.layout.model.Box;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import weka.core.DenseInstance;
import weka.core.Instance;
import weka.core.Instances;

/**
 * A simplified feature extractor for CEUR proceedings analysis.
 * 
 * @author burgetr
 */
public class ProgrammesFeatureExtractor extends DefaultFeatureExtractor
{
    private static Logger log = LoggerFactory.getLogger(ProgrammesFeatureExtractor.class);

    private Area root;
    private float avgfont;
    

    public ProgrammesFeatureExtractor()
    {
    }
    
    @Override
    public void setTree(Area rootNode)
    {
        root = rootNode;
        avgfont = root.getFontSize();
    }
    
    @Override
    public Area getTreeRoot()
    {
        return root;
    }

    @Override
    public Instance getAreaFeatures(Area area, Instances dataset)
    {
        String text = area.getText();
        int plen = text.length();
        if (plen == 0) plen = 1; //kvuli deleni nulou

        Instance inst = new DenseInstance(15);
        inst.setDataset(dataset);
        int i = 0;
        inst.setValue(i++, 0.0); //class
        inst.setValue(i++, area.getFontSize() / avgfont);
        inst.setValue(i++, area.getFontWeight());
        inst.setValue(i++, area.getFontStyle());
        inst.setValue(i++, area.isReplaced()?1:0);
        inst.setValue(i++, getLineCount(area));
        inst.setValue(i++, area.getDepth());
        inst.setValue(i++, text.length());
        inst.setValue(i++, countChars(text, Character.DECIMAL_DIGIT_NUMBER) / (double) plen);
        inst.setValue(i++, countChars(text, Character.LOWERCASE_LETTER) / (double) plen);
        inst.setValue(i++, countChars(text, Character.UPPERCASE_LETTER) / (double) plen);
        inst.setValue(i++, countChars(text, Character.SPACE_SEPARATOR) / (double) plen);
        inst.setValue(i++, countCharsPunct(text) / (double) plen);
        inst.setValue(i++, getRelX(area));
        inst.setValue(i++, getRelY(area));
        
        return inst;
    }

    @Override
    public Instances createEmptyDataset()
    {
        try {
            return loadArffDatasetResource("eswc_header.arff");
        } catch (Exception e) {
            log.error("Couldn't create empty dataset: " + e.getMessage());
            return null;
        }
    }

    //============================================================================================
    
    private int countChars(String s, int type)
    {
        int ret = 0;
        for (int i = 0; i < s.length(); i++)
            if (Character.getType(s.charAt(i)) == type)
                    ret++;
        return ret;
    }

    private int countCharsPunct(String s)
    {
        int ret = 0;
        for (int i = 0; i < s.length(); i++)
        {
            char ch = s.charAt(i);
            if (ch == ',' || ch == '.' || ch == ';' || ch == ':')
                    ret++;
        }
        return ret;
    }

    public int getLineCount(Area a)
    {
        final int LINE_THRESHOLD = 5; //minimal distance between lines in pixels
        
        List<Box> leaves = a.getAllBoxes();
        Collections.sort(leaves, new AbsoluteYPositionComparator());
        int lines = 0;
        int lastpos = -10;
        for (Box leaf : leaves)
        {
            int pos = leaf.getBounds().getY1();
            if (pos - lastpos > LINE_THRESHOLD)
            {
                lines++;
                lastpos = pos;
            }
        }
        return lines;
    }

    private double getRelX(Area a)
    {
        int objx1 = a.getX1();
        if (objx1 < 0) objx1 = 0;
        int objx2 = a.getX2();
        if (objx2 < 0) objx2 = 0;
        
        int topx1 = root.getX1();
        if (topx1 < 0) topx1 = 0;
        int topx2 = root.getX2();
        if (topx2 < 0) topx2 = 0;
        
        double midw = (objx2 - objx1) / 2.0;
        double topx = topx1 + midw; //zacatek oblasti, kde lze objektem posunovat
        double midx = (objx1 + objx2) / 2.0 - topx; //stred objektu v ramci teto oblasti
        double topw = (topx2 - topx1) - (objx2 - objx1); //sirka, kam lze stredem posunovat
        return midx / topw;
    }

    public double getRelY(Area a)
    {
        int objy1 = a.getY1();
        if (objy1 < 0) objy1 = 0;
        int objy2 = a.getY2();
        if (objy2 < 0) objy2 = 0;
        
        int topy1 = root.getY1();
        if (topy1 < 0) topy1 = 0;
        int topy2 = root.getY2();
        if (topy2 < 0) topy2 = 0;
        
        double midh = (objy2 - objy1) / 2.0;
        double topy = topy1 + midh; //zacatek oblasti, kde lze objektem posunovat
        double midy = (objy1 + objy2) / 2.0 - topy; //stred objektu v ramci teto oblasti
        double toph = (topy2 - topy1) - (objy2 - objy1); //sirka, kam lze stredem posunovat
        return midy / toph;
    }
    
    //============================================================================================
    
    class AbsoluteYPositionComparator implements Comparator<Box>
    {
        @Override
        public int compare(Box o1, Box o2)
        {
            return o1.getBounds().getY1() - o2.getBounds().getY1(); 
        }
    }

}
