import java.util.*;
import org.json.*;

import edu.stanford.nlp.io.*;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.dcoref.*;
import edu.stanford.nlp.dcoref.CorefChain.*;
import edu.stanford.nlp.dcoref.CorefCoreAnnotations.*;
import edu.stanford.nlp.ling.CoreAnnotations.*;
import edu.stanford.nlp.semgraph.*;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.util.*;

class Story
{

  private static final List<Character> punct = Arrays.asList('\'','"','!',
							     '?','-',';',
							     '.',',',':',
							     '/','\\','@',
							     '#','*','&',
							     '`','$','+',
							     '=','%','_');

  private String text;
  private List<Question> questions = new ArrayList<Question>();

  private List<Token> tokens = new ArrayList<Token>();
  private List<Integer> sentoffsets = new ArrayList<Integer>();

  public Story()
  {

  }

  public static Story fromtext(String txt)
  {

    Story story = new Story();

    txt = txt.replace("\\newline"," ").replace("\\tab"," ");

    String fld[] = txt.split("\t");
    
    story.text = fld[2];

    for(int i = 3; i < fld.length; i += 5)
      story.questions.add(new Question(fld[i],
				       Arrays.asList(Arrays.
						     copyOfRange(fld,
								 i+1,i+5))));

    return story;

  }

  public void parse(Parser p)
  {

    Annotation a = procstory(p);
    proccorefs(a.get(CorefChainAnnotation.class).values());

    for(Question q : questions)
    {

      q.setqtoks(procqa(p,q.getquestion()));
      
      for(String ans : q.getanswers())
	q.addatoks(procqa(p,ans));

      procneg(p,q);

    }

    filtertoks();
    setfreqs();

    for(Token t : tokens)
      for(Question q : questions)
	t.setmatches(q);

  }

  private Annotation procstory(Parser p)
  {

    Annotation a = p.parse(text);

    int prev = 0;

    for(CoreMap sentence : a.get(SentencesAnnotation.class))
    {
      
      sentoffsets.add(prev);
      prev += sentence.get(TokensAnnotation.class).size();

      for(CoreLabel token : sentence.get(TokensAnnotation.class))
	tokens.add(mktoken(token));

    }

    return a;

  }

  private List<Token> procqa(Parser p, String sent)
  {

    Annotation a = p.parse(sent);

    List<Token> toks = new ArrayList<Token>();
    
    for(CoreMap sentence : a.get(SentencesAnnotation.class))
      for(CoreLabel token : sentence.get(TokensAnnotation.class))
      {
	
	Token t = mktoken(token);

	if(!t.ispunct())
	  toks.add(mktoken(token));

      }

    return toks;
    
  }

  private boolean punct(CoreLabel t)
  {

    return Story.punct.contains(t.get(TextAnnotation.class)
				.toString().charAt(0));
      
  }

  private Token mktoken(CoreLabel token)
  {

    return new Token(token.get(TextAnnotation.class).toString(),
		     token.get(LemmaAnnotation.class).toString(),
		     token.get(PartOfSpeechAnnotation.class)
		     .toString(),punct(token));

  }
  
  private void proccorefs(Collection<CorefChain> corefs)
  {
    
    for(CorefChain c : corefs)
    {
      
      List<CorefMention> mnts = c.getMentionsInTextualOrder();
      
      if(mnts.size() == 1)
	continue;
      
      CorefMention mn = c.getRepresentativeMention();
      
      int sofs = sentoffsets.get(mn.sentNum - 1) + (mn.startIndex - 1);
      int eofs = sentoffsets.get(mn.sentNum - 1) + (mn.endIndex - 1);
      
      List<Token> mntoks = new ArrayList<Token>();

      for(Token t : tokens.subList(sofs,eofs))
	if(!t.ispunct() && !t.isstopword())
	  mntoks.add(t);

      for(CorefMention m : mnts)
      {
	
	if(m.toString().equals(mn.toString()))
	  continue;
	
	int bofs = sentoffsets.get(m.sentNum - 1) + (m.startIndex - 1);
	int lofs = sentoffsets.get(m.sentNum - 1) + (m.endIndex - 1);
	
	tokens.get(bofs).setcoref(mntoks,tokens.get(sofs));

	for(Token t : tokens.subList(bofs + 1,lofs))
	  t.setsubcoref(true);
	
      }

    }

  }

  private void procneg(Parser p, Question q)
  {
 
    SemanticGraph deps = p.parse(q.getquestion())
      .get(SentencesAnnotation.class).get(0)
      .get(CollapsedCCProcessedDependenciesAnnotation.class);

    List<SemanticGraphEdge> hdmods = deps.outgoingEdgeList(deps.getRoots()
							   .iterator().next());
    
    for(SemanticGraphEdge e : hdmods)
      if(e.getRelation().getShortName().equals("neg"))
      {
	
	q.setnegative(true);
	break;

      }

  }

  private void filtertoks()
  {

    List<Token> nw = new ArrayList<Token>();
    
    for(Token t : tokens)
      if(!t.ispunct())
    	nw.add(t);

    tokens = nw;

  }

  private void setfreqs()
  {

    List<String> tokstory = new ArrayList<String>();
    List<String> lemstory = new ArrayList<String>();
    List<String> crtstory = new ArrayList<String>();

    for(Token t : tokens)
    {

      tokstory.add(t.gettoken());
      lemstory.add(t.getlemma());

      if(!t.hascoref())
	crtstory.add(t.gettoken());
      
      if(!t.issubcoref() && t.hascoref())
	for(String s : t.getcoref())
	  crtstory.add(s);

    }

    for(Token t : tokens)
    {

      t.tokcount(tokstory);
      t.lemcount(lemstory);
      t.crtcount(crtstory);

    }

  }

  public String gettext()
  {

    return text;

  }

  public List<Question> getquestions()
  {

    return questions;

  }

  public JSONObject tojson() throws JSONException
  {

    JSONObject j = new JSONObject();

    JSONArray t = new JSONArray();
    JSONArray qn = new JSONArray();
    JSONArray ql = new JSONArray();
    JSONArray sm = new JSONArray();

    JSONArray qtk = new JSONArray();
    JSONArray atk = new JSONArray();
    JSONArray qlm = new JSONArray();
    JSONArray alm = new JSONArray();

    JSONArray s = new JSONArray(sentoffsets);

    for(Token tk : tokens)
      t.put(tk.tojson());



    for(Question q : questions)
    {

      JSONObject lens = new JSONObject();

      lens.put("question",q.getqlen());
      lens.put("answers",new JSONArray(q.getalen()));

      ql.put(lens);

      qn.put(q.isnegative());
      sm.put(q.getmode());

      
      JSONArray qtnt = new JSONArray();
      JSONArray qtnl = new JSONArray();
      
      for(Token tn : q.getqtoks())
      {

	qtnt.put(tn.gettoken());
	qtnl.put(tn.getlemma());

      }

      qtk.put(qtnt);
      qlm.put(qtnl);


      JSONArray atnt = new JSONArray();
      JSONArray atnl = new JSONArray();
      
      for(List<Token> a : q.getatoks())
      {

	JSONArray tk = new JSONArray();
	JSONArray lm = new JSONArray();
	
	for(Token tn : a)
	{

	  tk.put(tn.gettoken());
	  lm.put(tn.getlemma());

	}

	atnt.put(tk);
	atnl.put(lm);

      }

      atk.put(atnt);
      alm.put(atnl);

    }

    j.put("tokens",t);
    j.put("qalengths",ql);
    j.put("negativeqs",qn);
    j.put("sentenceoffsets",s);
    j.put("multiqs",sm);
    j.put("qtokens",qtk);
    j.put("atokens",atk);
    j.put("qlemmas",qlm);
    j.put("alemmas",alm);

    return j;

  }

  public String toString()
  {

    StringBuilder sb = new StringBuilder();

    sb.append("Story:\n\n" + text + "\n\n");
    
    for(Question q : questions)
      sb.append(q.toString());

    return sb.toString();

  }

}
