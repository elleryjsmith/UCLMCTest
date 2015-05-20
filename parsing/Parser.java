import java.util.*;

import edu.stanford.nlp.io.*;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.util.*;


class Parser
{

  private Properties props = new Properties();
  private StanfordCoreNLP cnlp;

  public Parser()
  {

    this.props.setProperty("annotators","tokenize, ssplit, pos, " +
			   "lemma, ner, parse, depparse, dcoref");
    this.cnlp = new StanfordCoreNLP(this.props);

  }

  public Annotation parse(String txt)
  {
    
    Annotation doc = new Annotation(txt);

    cnlp.annotate(doc);

    return doc;

  }

}