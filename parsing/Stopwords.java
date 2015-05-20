import java.util.*;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.*;

class Stopwords
{
  
  public static List<String> stopwords = new ArrayList<String>();

  public Stopwords()
  {

  }

  public static void genstopwords()
  {

    try
    {

      stopwords =  Files.readAllLines(Paths.get("datasets/stopwords.txt"),
				      Charset.defaultCharset());

    }
    catch(IOException e)
    {

      System.out.println("Error reading stopwords file.");
      System.exit(1);

    }
    
  }

}