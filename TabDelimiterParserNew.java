/* 
Code by Jacob Eisenstein, March 2012. 
*/

//package parsing;

import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.trees.Tree;
//ARVIND: added the below four imports
import edu.stanford.nlp.trees.PennTreebankLanguagePack;
import edu.stanford.nlp.trees.TreebankLanguagePack;
import edu.stanford.nlp.trees.Constituent;
import edu.stanford.nlp.trees.GrammaticalStructureFactory;
import edu.stanford.nlp.trees.GrammaticalStructure;

import java.io.BufferedReader;
import java.io.Reader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Set;

/* 
   class for parsing delimited files, 
   in which each token is the first column
   and sentences are separated by newlines
*/

class TabDelimitedParserNew {
    public static void main(String[] args){
	String[] options = { "-maxLength", "1000", "-retainTmpSubcategories" };
	String grammar = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";
	LexicalizedParser lp = LexicalizedParser.loadModel(grammar,options);
	TabDelimitedParserNew p = new TabDelimitedParserNew(lp);
	p.parseFile(args[0]);
    }
    public void parseFile(String filename) {
	try {
	    BufferedReader input = new BufferedReader(new FileReader(new File(filename)));
	    parseLines(input);
	} catch (IOException e){
	    e.printStackTrace();
	}
    }

    public void parseLines(BufferedReader input) throws IOException{
	List<String[]> tokens = new ArrayList<String[]>();
	String line = null;
	Tree tree = null;
	while ((line = input.readLine()) != null){
	    String[] parts = line.split(k_delimiter);
	    if (parts.length > 1)
		tokens.add(parts);
	    else {
		parseSentence(tokens);
		tokens.clear();
	    }
	}
	parseSentence(tokens);
    }
    
    /* subclasses should override this */
    public void processParse(Tree output, List<String[]> tokens){
	output.pennPrint();
  System.out.println();
  Set<Constituent> constituents = output.constituents();
    for(Constituent con : constituents)
    {
      System.out.println(con);
      //System.out.println(con.label());
    }
  
    //ARVIND: added the lines below
    //System.out.println();
    // System.out.println(output.taggedYield());
    // System.out.println();
    // GrammaticalStructure gs = this.gsf.newGrammaticalStructure(output);
    // Collection tdl = gs.typedDependenciesCCprocessed(true);
    // System.out.println(tdl);
    // System.out.println();

    }
    
    public Tree parseSentence(List<String[]> tokens){
	List<CoreLabel> rawWords = new ArrayList<CoreLabel>();
	for (String[] word : tokens){
	    CoreLabel l = new CoreLabel();
	    l.setWord(word[k_column]);
	    rawWords.add(l);
	}
	Tree output = parser.apply(rawWords);
	processParse(output,tokens);
	return output;
    }

    public TabDelimitedParserNew(LexicalizedParser parser){
	this.parser = parser;
  this.tlp = new PennTreebankLanguagePack();
  this.gsf = tlp.grammaticalStructureFactory();
    }
    protected LexicalizedParser parser;
    protected static String k_delimiter = " ";
    protected static int k_column = 0;
    private TreebankLanguagePack tlp;
    private GrammaticalStructureFactory gsf;
}