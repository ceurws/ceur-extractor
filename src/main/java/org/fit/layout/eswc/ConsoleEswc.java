/**
 * ConsoleEswc.java
 *
 * Created on 26. 2. 2015, 15:46:07 by burgetr
 */
package org.fit.layout.eswc;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;

import javax.script.ScriptException;

import org.fit.layout.api.AreaTreeOperator;
import org.fit.layout.classify.InstanceExtractor;
import org.fit.layout.classify.op.TagEntitiesOperator;
import org.fit.layout.eswc.classify.ProgrammesFeatureExtractor;
import org.fit.layout.tools.Console;

/**
 *
 * @author burgetr
 */
public class ConsoleEswc extends Console
{
    private InstanceExtractor extractor;

    @Override
    protected void init()
    {
        super.init();
        //custom instance extractor for training data extraction
        extractor = new InstanceExtractor(new ProgrammesFeatureExtractor(), "CEUR");
        getProcessor().put("extr", extractor);
        //init custom taggers
        AreaTreeOperator tcls = getProcessor().getOperators().get("FitLayout.Tag.Entities");
        if (tcls != null && tcls instanceof TagEntitiesOperator)
        {
            ((TagEntitiesOperator) tcls).addTagger(new CountriesTagger());
            ((TagEntitiesOperator) tcls).addTagger(new ShortNameTagger());
        }
        else
            System.err.println("Couldn't configure FitLayout.Tag.Entities!");

    }

    @Override
    protected void initSession() throws ScriptException
    {
        super.initSession();
        getProcessor().execInternal("js/eswc_init.js");
    }

    public void browser()
    {
        BlockBrowserEswc.main(new String[0]);
    }

    public void dumpIndex(String destfile)
    {
        IndexFile.dumpIndex(destfile);
    }

    public String dumpIndex()
    {
        return IndexFile.dumpIndex();
    }

    public void dumpEditors(String destfile)
    {
        IndexFile.dumpEditors(destfile);
    }

    public String dumpEditors()
    {
        return IndexFile.dumpEditors();
    }

    public String readFile(String filename){
    	BufferedReader fileReader = null;
    	InputStream in = getClass().getResourceAsStream(filename);
    	List<String> urls = new ArrayList<String>();
    	try{
    		fileReader = new BufferedReader(new InputStreamReader(in));
    		String line = "";
    		while ((line = fileReader.readLine()) != null){
    			urls.add(line.split(";;")[0].replaceAll("^\\<|\\>$", ""));
    		}
    	}catch(Exception e){
    		System.out.println("Error in readFile of ConsoleEswc !!!");
    		e.printStackTrace();
    	}finally{
    		try {
    				fileReader.close();
    			} catch (IOException e) {
    				System.out.println("Error while closing fileReader !!!");
    				e.printStackTrace();
    			}

    	}
    	// List<String> sublist = urls.subList(1500, 1559); // Vol 1-300 (0-299)
    	// List<String> sublist = urls.subList(300, 600); // Vol 301-600 (300-599)
    	// ListIterator<String> iter = sublist.listIterator();
    	/*tmp_str.equals("http://ceur-ws.org/Vol-331/") || tmp_str.equals("http://ceur-ws.org/Vol-299/")
    				|| tmp_str.equals("http://ceur-ws.org/Vol-120/") || tmp_str.equals("http://ceur-ws.org/Vol-88/")
    				|| tmp_str.equals("http://ceur-ws.org/Vol-84/") || tmp_str.equals("http://ceur-ws.org/Vol-41/")
    				|| tmp_str.equals("http://ceur-ws.org/Vol-35/") || tmp_str.equals("http://ceur-ws.org/Vol-18/")
    				|| tmp_str.equals("http://ceur-ws.org/Vol-1260/") || tmp_str.equals("http://ceur-ws.org/Vol-989/") 
    				|| tmp_str.equals("http://ceur-ws.org/Vol-12/") || 
    	 * */
    	/*
    	while(iter.hasNext()){
    		String tmp_str = iter.next();
    		if(tmp_str.equals("http://ceur-ws.org/Vol-41/")){
    			iter.remove();
    		}
    	}*/
    	return urls.toString().replaceAll("^\\[|\\]$", "");
    }

    public static void main(String[] args)
    {
        System.out.println("FitLayout interactive console [ESWC]");
        Console con = new ConsoleEswc();
        try
        {
            con.interactiveSession(System.in, System.out, System.err);
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

}
