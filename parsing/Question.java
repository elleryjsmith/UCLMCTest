import java.util.*;
import java.util.regex.Pattern;

class Question
{

  private static final int SINGLE = 0;
  private static final int MULTI = 1;

  private String question;
  private List<String> answers = new ArrayList<String>();
  private int mode, qlen;
  private List<Integer> alen = new ArrayList<Integer>();
  private boolean negative;

  private List<Token> qtoks = new ArrayList<Token>();
  private List<List<Token>> atoks = new ArrayList<List<Token>>();

  public Question(String q, List<String> ans)
  {

    String mdq[] = q.split(Pattern.quote(": "));

    this.question = mdq[1];
    this.mode = mdq[0].equals("one") ? SINGLE : MULTI;
    this.answers = ans;
    this.negative = false;
    
  }

  public String getquestion()
  {

    return question;

  }
  
  public List<String> getanswers()
  {

    return answers;

  }

  public void setqtoks(List<Token> t)
  {

    qtoks = t;
    qlen = t.size();

  }

  public void addatoks(List<Token> t)
  {
    
    atoks.add(t);
    alen.add(t.size());

  }

  public void setnegative(boolean b)
  {

    negative = b;

  }
  
  public int getqlen()
  {

    return qlen;

  }

  public List<Integer> getalen()
  {

    return alen;

  }


  public List<Token> getqtoks()
  {

    return qtoks;

  }

  public List<List<Token>> getatoks()
  {

    return atoks;

  }

  public int getmode()
  {

    return mode;

  }
  
  public boolean isnegative()
  {

    return negative;

  }

  public String toString()
  {
    
    StringBuilder sb = new StringBuilder();

    sb.append("Q: " + question + "\n");
    
    for(String a : answers)
    {
      
      sb.append("A: ");
      sb.append(a.toString());
      sb.append("\n");

    }

    sb.append("\n");

    return sb.toString();

  }

}
