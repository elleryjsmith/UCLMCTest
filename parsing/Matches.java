import java.util.*;
import org.json.*;

class Matches
{
  
  private Token token;

  private List<Boolean> qtokmatch = new ArrayList<Boolean>();
  private List<List<Boolean>> atokmatch = new ArrayList<List<Boolean>>();
  private List<Boolean> qlemmatch = new ArrayList<Boolean>();
  private List<List<Boolean>> alemmatch = new ArrayList<List<Boolean>>();

  private List<Map<String,Boolean>> qcrtmatch = 
    new ArrayList<Map<String,Boolean>>();
  private List<Map<String,List<Boolean>>> acrtmatch =
    new ArrayList<Map<String,List<Boolean>>>();


  public Matches(Token t)
  {

    this.token = t;

  }

  public void setmatches(Question q)
  {

    List<String> qtoks = new ArrayList<String>();
    List<String> qlems = new ArrayList<String>();

    for(Token t : q.getqtoks())
    {

      qtoks.add(t.gettoken());
      qlems.add(t.getlemma());

    }

    qtokmatch.add(qtoks.contains(token.gettoken()));
    qlemmatch.add(qlems.contains(token.getlemma()));

    Map<String,Boolean> cmp = new HashMap<String,Boolean>();      

    for(String s : new LinkedHashSet<String>(token.getcoref()))
      cmp.put(s,qtoks.contains(s));
    
    qcrtmatch.add(cmp);


    Map<String,List<Boolean>> amp = new HashMap<String,List<Boolean>>();
    List<Boolean> amt = new ArrayList<Boolean>();
    List<Boolean> aml = new ArrayList<Boolean>();

    for(String s : token.getcoref())
      amp.put(s,new ArrayList<Boolean>());

    for(List<Token> as : q.getatoks())
    {

      List<String> atoks = new ArrayList<String>();
      List<String> alems = new ArrayList<String>();

      for(Token t : as)
      {
	
	atoks.add(t.gettoken());
	alems.add(t.getlemma());
	
      }

      amt.add(atoks.contains(token.gettoken()));
      aml.add(alems.contains(token.getlemma()));
      
      for(String s : new LinkedHashSet<String>(token.getcoref()))
	amp.get(s).add(atoks.contains(s));
      
    }

    atokmatch.add(amt);
    alemmatch.add(aml);
    acrtmatch.add(amp);
    
  }

  public JSONObject tojson() throws JSONException
  {

    JSONObject m = new JSONObject();

    m.put("qtoken",new JSONArray(bltoil(qtokmatch)));
    m.put("qlemma",new JSONArray(bltoil(qlemmatch)));

    JSONArray at = new JSONArray();
    JSONArray al = new JSONArray();

    for(List<Boolean> a : atokmatch)
      at.put(new JSONArray(bltoil(a)));

    for(List<Boolean> a : alemmatch)
      al.put(new JSONArray(bltoil(a)));

    m.put("atoken",at);
    m.put("alemma",al);

    JSONArray qc = new JSONArray();

    for(Map<String,Boolean> c : qcrtmatch)
    {

      JSONObject qcr = new JSONObject();
      
      for(String s : c.keySet())
	qcr.put(s,btoi(c.get(s)));

      qc.put(qcr);

    }
    
    JSONArray ac = new JSONArray();

    for(Map<String,List<Boolean>> c : acrtmatch)
    {

      JSONObject mp = new JSONObject();

      for(String s : c.keySet())
	mp.put(s,new JSONArray(bltoil(c.get(s))));

      ac.put(mp);

    }

    m.put("qcoref",qc);
    m.put("acoref",ac);

    return m;

  }

  private List<Integer> bltoil(List<Boolean> bl)
  {

    List<Integer> il = new ArrayList<Integer>();

    for(Boolean b : bl)
      il.add(btoi(b));

    return il;

  }

  private int btoi(boolean b)
  {

    return b ? 1 : 0;

  }

}
