import java.util.*;
import java.lang.*;
import org.json.*;

class Token
{

  private String token, lemma, pos;
  private boolean punct, subcoref, stopword;
  private List<String> coref = new ArrayList<String>();
  private float tokidf, lemidf;
  private Map<String,Float> crtidf = new HashMap<String,Float>();
  private Token rep;
  private float origidf = 1.0;
  private Matches matches;

  public Token(String t, String l, String p, boolean pc)
  {
    
    this.token = t.toLowerCase();
    this.lemma = l.toLowerCase();
    this.pos = p;
    this.punct = pc;
    this.subcoref = false;
    this.stopword = Stopwords.stopwords.contains(this.token);
    this.matches = new Matches(this);

  }

  public void setcoref(List<Token> crf, Token r)
  {

    for(Token t : crf)
      coref.add(t.gettoken());

    rep = r;

  }

  public void setsubcoref(boolean b)
  {

    subcoref = b;

  }

  public void setstopword(boolean b)
  {

    stopword = b;

  }

  private float count(String wd, List<String> st)
  {

    float c = 0;

    for(String s : st)
      if(wd.equals(s))
	++c;

    return Math.log(1 + (1 / (1 + c)));

  }

  public void tokcount(List<String> st)
  {

    tokidf = count(token,st);

  }

  public void lemcount(List<String> st)
  {

    lemidf = count(lemma,st);

  }

  public void crtcount(List<String> st)
  {

    for(String s : coref)
      crtidf.put(s,count(s,st));

    if(rep != null)
      origidf = rep.gettokidf();

  }

  public void setmatches(Question q)
  {

    matches.setmatches(q);

  }

  public String gettoken()
  {

    return token;

  }

  public String getlemma()
  {

    return lemma;

  }

  public String getpos()
  {

    return pos;

  }

  public List<String> getcoref()
  {
    
    return coref;
    
  }

  public float gettokidf()
  {

    return tokidf;

  }

  public float getlemidf()
  {

    return lemidf;

  }

  public Map<String,Float> getcrtidf()
  {

    return crtidf;

  }
  
  public boolean ispunct()
  {

    return punct;

  }

  public boolean issubcoref()
  {

    return subcoref;

  }
  
  public boolean hascoref()
  {

    return subcoref || (coref.size() > 0);

  }

  public boolean isstopword()
  {
    
    return stopword;

  }

  public JSONObject tojson() throws JSONException
  {

    JSONObject t = new JSONObject();

    JSONObject tk = new JSONObject();
    tk.put("word",token);
    tk.put("idf",tokidf);

    JSONObject lm = new JSONObject();
    lm.put("word",lemma);
    lm.put("idf",lemidf);

    t.put("token",tk);
    t.put("lemma",lm);

    JSONArray crfs = new JSONArray();

    for(String s : coref)
    {

      JSONObject c = new JSONObject();

      c.put("word",s);
      c.put("idf",crtidf.get(s));

      crfs.put(c);

    }

    t.put("coreference",crfs);

    t.put("pos",pos);
    t.put("stopword",btoi(stopword));
    t.put("subcoref",btoi(subcoref));
    t.put("origidf",origidf);

    t.put("matches",matches.tojson());

    return t;

  }

  private int btoi(boolean b)
  {

    return b ? 1 : 0;

  }

  public String toString()
  {

    return "Token: " + token + ", Lemma: " + lemma + ", POS: " + pos;

  }

}
