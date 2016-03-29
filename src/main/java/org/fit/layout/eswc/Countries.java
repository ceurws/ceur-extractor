/**
 * Countries.java
 *
 * Created on 21. 3. 2015, 0:49:47 by burgetr
 */
package org.fit.layout.eswc;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * A database of countries and their URIs.
 *  
 * @author burgetr
 */
public class Countries
{
    private static Map<String, String> countries;
    
    static {
        try
        {
            countries = new HashMap<String, String>();
            BufferedReader is = new BufferedReader(new InputStreamReader(ClassLoader.getSystemResourceAsStream("countries_all.csv")));
            String line;
            while ((line = is.readLine()) != null)
            {
                String s[] = line.split(",");
                if (s.length == 3)
                {
                    countries.put(s[1].toLowerCase(), s[0]);
                    countries.put(s[2].toLowerCase(), s[0]);
                }
            }
        } catch (IOException e)
        {
            System.err.println("Load failed: " + e.getMessage());
        }
    }
    
    public static String getCountryUri(String name)
    {
        return countries.get(name.toLowerCase());
    }
    
    public static Set<String> getCountryNames(String s)
    {
        HashSet<String> ret = new HashSet<String>();
        //try single words
        String[] words = s.toLowerCase().split("\\W+");
        for (String w : words)
        {
            if (countries.containsKey(w))
                ret.add(w);
        }
        //try multiword separated
        String[] elems = s.toLowerCase().split("\\s*[,;]\\s*");
        for (String w : elems)
        {
            if (countries.containsKey(w))
                ret.add(w);
        }
        return ret;
    }
    
}
