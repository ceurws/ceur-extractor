package org.fit.layout.eswc;

public class Event
{
    public int order;
    public String sname;
    public String title;
    
    public Event()
    {
        order = -1;
        sname = null;
        title = null;
    }
    
    public Event(int order, String sname, String title)
    {
        this.order = order;
        this.sname = sname;
        this.title = title;
    }

    public int getEffectiveOrder()
    {
        return (order <= 0) ? 1 : order;
    }
    
    @Override
    public String toString()
    {
        return "Event [order=" + order + ", sname=" + sname + ", title=" + title + "]";
    }

    @Override
    public int hashCode()
    {
        final int prime = 31;
        int result = 1;
        result = prime * result + getEffectiveOrder();
        result = prime * result + ((sname == null) ? 0 : sname.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj)
    {
        if (this == obj) return true;
        if (obj == null) return false;
        if (getClass() != obj.getClass()) return false;
        Event other = (Event) obj;
        if (getEffectiveOrder() != other.getEffectiveOrder()) return false;
        if (sname == null)
        {
            if (other.sname != null) return false;
        }
        else if (!sname.equals(other.sname)) return false;
        return true;
    }

}