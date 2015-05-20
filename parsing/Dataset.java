import java.util.*;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.*;


class Dataset
{

  private String name;
  private List<Story> stories = new ArrayList<Story>();

  public Dataset(String name)
  {

    this.name = name;

  }

  public static Dataset fromfile(String fname)
  {

    Dataset dt = new Dataset(fname);

    dt.parsestories();

    Stopwords.genstopwords();

    return dt;

  }

  private void parsestories()
  {

    try
    {

      List<String> lns =  Files.readAllLines(Paths.get("datasets/" + 
						       name + ".tsv"),
					     Charset.defaultCharset());

      for(String ln : lns)
	stories.add(Story.fromtext(ln));

    }
    catch(IOException e)
    {

      System.out.println("Error reading dataset.");
      System.exit(1);
    
    }

  }

  public List<Story> getstories()
  {

    return stories;

  }

}