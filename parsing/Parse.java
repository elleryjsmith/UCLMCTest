import java.util.*;
import java.io.*;
import org.json.*;

class Parse
{

  public static void main(String args[])
  {

    if(args.length == 0)
    {

      System.out.println("Usage: ./parse.sh <dataset> (e.g. mc160.dev)");
      System.exit(1);

    }

    Parser p = new Parser();

    Dataset dt = Dataset.fromfile(args[0]);

    try
    {

      JSONArray st = new JSONArray();

      for(Story s : dt.getstories())
      {

	s.parse(p);
	st.put(s.tojson());

      }

      Writer w = new BufferedWriter(new OutputStreamWriter(
				      new FileOutputStream("datasets/" + 
							   args[0] +
							   ".json"),"utf-8"));

      w.write(st.toString());
      w.close();

    }
    catch(JSONException e)
    {
      
      System.out.println("Error writing parse file.");
      System.exit(1);
   
    }
    catch(IOException e)
    {

      System.out.println("Error writing parse file.");
      System.exit(1);

    }

  }

}