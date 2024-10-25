import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

public class POSTagger {

    //Map of maps to represent graph
    private final Map<String, Map<String, Double>> observations;
    private final Map<String, Map<String, Double>> transitions;

    //Constructor that takes no parameters and makes empty maps for training
    public POSTagger() {
        observations = new HashMap<>();
        transitions = new HashMap<>();
    }

    //Constructor that passes in hard coded maps
    public POSTagger(Map<String, Map<String, Double>> observations, Map<String, Map<String, Double>> transitions) {
        this.observations = observations;
        this.transitions = transitions;
    }

    /**
     * Viterbi algorithm used on a list of words in a sentence
     * @param sentence
     * @return List of tag sequence
     */
    public List<String> viterbi(String[] sentence) {
        //List of maps that keep track of all nextStates to currState
        List<Map<String, String>> backTrace = new ArrayList<>();

        Set<String> currStates = new HashSet<>();   //set of all current states so no repetition; initialize with #
        currStates.add("#");

        Map<String, Double> currScores = new HashMap<>();   //map of states to scores; initialize with # as 0
        currScores.put("#", 0.0);

        double unseen = -100.0;     //unseen word score

        //loop through all words, creating new sets and maps for next possible states and backpointer for each
        for (int i = 0; i < sentence.length; i++) {
            Set<String> nextStates = new HashSet<>();
            Map<String, Double> nextScores = new HashMap<>();
            Map<String, String> backpointer = new HashMap<>();
            for (String currState: currStates) {
                for (String nextState: transitions.get(currState).keySet()) {
                    nextStates.add(nextState);  //add all next states
                    double obsScore = unseen;
                    //update observation score if it exists for the current word i
                    if (observations.get(nextState).containsKey(sentence[i])) {
                        obsScore = observations.get(nextState).get(sentence[i]);
                    }
                    //calculate new score for each next state
                    double nextScore = currScores.get(currState) + transitions.get(currState).get(nextState) + obsScore;
                    //if best path, add the score and backpointer
                    if (!nextScores.containsKey(nextState) || nextScore > nextScores.get(nextState)) {
                        nextScores.put(nextState, nextScore);
                        backpointer.put(nextState, currState);
                    }
                }
            }
            //update sets and maps for loop to run again
            backTrace.add(backpointer);
            currStates = nextStates;
            currScores = nextScores;
        }
        //use backpointer map to make a list of the parts of speech in order
        List<String> tagSequence = new ArrayList<>();
        String currTag = "";
        //find last tag by picking the one with the biggest score
        for (String state: currStates) {
            if (currTag.equals("")) {
                currTag = state;
            }
            if (currScores.get(state) > currScores.get(currTag)) currTag = state;
        }
        //add each tag working backwards
        while (!currTag.equals("#")) {
            tagSequence.add(0, currTag);
            currTag = backTrace.remove(backTrace.size()-1).get(currTag);
        }
        return tagSequence;
    }

    /**
     * Uses given files to create observation and transition map for a tagger
     * @param sentencesFilename
     * @param tagsFilename
     * @throws IOException
     */
    public void modelTrainer(String sentencesFilename, String tagsFilename) throws IOException {
        BufferedReader sentenceInput = new BufferedReader(new FileReader(sentencesFilename));
        BufferedReader tagsInput = new BufferedReader(new FileReader(tagsFilename));
        String sentenceLine;
        //always add the start
        transitions.put("#", new HashMap<>());
        //since both sentence file and tag file have same number of lines, only loop once through one of them
        while ((sentenceLine = sentenceInput.readLine()) != null) {
            //parse each sentence and make a list of words and tags for each line
            sentenceLine = sentenceLine.toLowerCase();
            String[] words = sentenceLine.split(" ");
            String tagLine = tagsInput.readLine();
            String[] tags = tagLine.split(" ");

            //add or update each first tag to transition from start
            if (!transitions.get("#").containsKey(tags[0])) {
                transitions.get("#").put(tags[0], 1.0);
            }
            else {
                transitions.get("#").put(tags[0], transitions.get("#").get(tags[0]) + 1);
            }
            //loop through all the tags
            for (int i = 0; i < tags.length; i++) {
                //add tag to observations if not seen before
                if (!observations.containsKey(tags[i])) {
                    observations.put(tags[i], new HashMap<>());
                }
                //add word to tag in observations if not seen before
                if (!observations.get(tags[i]).containsKey(words[i])) {
                    observations.get(tags[i]).put(words[i], 0.0);
                }
                //update each observation
                observations.get(tags[i]).put(words[i], observations.get(tags[i]).get(words[i]) + 1);

                //do all the same things for transitions except the last one
                if (i < tags.length-1) {
                    if (!transitions.containsKey(tags[i])) {
                        transitions.put(tags[i], new HashMap<>());
                    }
                    if (!transitions.get(tags[i]).containsKey(tags[i + 1])) {
                        transitions.get(tags[i]).put(tags[i + 1], 0.0);
                    }
                    transitions.get(tags[i]).put(tags[i + 1], transitions.get(tags[i]).get(tags[i + 1]) + 1);
                }
            }
        }
        //add an observation to transitions if it doesn't exist there yet (useful for periods)
        for (String state: observations.keySet()) {
            if (!transitions.containsKey(state)) {
                transitions.put(state, new HashMap<>());
            }
        }
        //create maps that store all the totals
        Map<String, Integer> observationTotals = new HashMap<>();
        Map<String, Integer> transitionTotals = new HashMap<>();

        //for each state in observations, add sum of all word counts to total
        for (String state: observations.keySet()) {
            int osum = 0;
            for (String word: observations.get(state).keySet()) {
                osum += observations.get(state).get(word);
            }
            observationTotals.put(state, osum);
        }

        //for each state in transitions, add sum of all nextstate counts to total
        for (String state: transitions.keySet()) {
            int tsum = 0;
            for (String nextState: transitions.get(state).keySet()) {
                tsum += transitions.get(state).get(nextState);
            }
            transitionTotals.put(state, tsum);
        }

        //assign each word its new value by taking log of probability
        for (String state: observations.keySet()) {
            for (String word: observations.get(state).keySet()) {
                if (observations.get(state).get(word) != 0) {
                    observations.get(state).put(word, (Math.log((observations.get(state).get(word) / observationTotals.get(state)))));
                }
            }
        }

        //assign each next state its new value by taking log of probability
        for (String state: transitions.keySet()) {
            for (String nextState: transitions.get(state).keySet()) {
                if (transitions.get(state).get(nextState) != 0) {
                    transitions.get(state).put(nextState, (Math.log((transitions.get(state).get(nextState) / transitionTotals.get(state)))));
                }
            }
        }
    }

    /**
     * Uses a scanner to perform viterbi on a typed in sentence
     */
    public void consoleTagger() {
        Scanner in = new Scanner(System.in);
        System.out.println("Please enter a sentence to be tagged. Put a space between punctuation and words as well.");
        System.out.println("Enter Q to quit.");
        String sentence = in.nextLine();
        //perform viterbi on each new sentence until user quits
        while (!sentence.equals("q")) {
            //parse each sentence and call viterbi
            String[] originalWords = sentence.split(" ");
            String[] words = sentence.toLowerCase().split(" ");
            printTaggedLine(viterbi(words), originalWords);

            System.out.println("Please enter a sentence to be tagged. Put a space between punctuation and words as well.");
            System.out.println("Enter Q to quit.");
            sentence = in.nextLine();
        }
    }

    public void fileTagger(String sentencesFilename, String tagsFilename) throws Exception {
        Scanner in = new Scanner(System.in);
        BufferedReader sentenceInput = new BufferedReader(new FileReader(sentencesFilename));
        BufferedReader tagsInput = new BufferedReader(new FileReader(tagsFilename));

        System.out.println("Would you like to print each tagged line? Enter Y/N:");
        String print = in.nextLine().toLowerCase();

        System.out.println("Would you like to evaluate performance for the test files? Enter Y/N:");
        String eval = in.nextLine().toLowerCase();

        //initialize sentence and guess count variables
        String sentenceLine;
        int goodGuesses = 0;
        int badGuesses = 0;

        while ((sentenceLine = sentenceInput.readLine()) != null) {
            //parse each sentence in file
            String lowercase = sentenceLine.toLowerCase();
            String[] words = lowercase.split(" ");
            String[] originalWords = sentenceLine.split(" ");
            //parse each tag in file
            String tagLine = tagsInput.readLine();
            String[] tags = tagLine.split(" ");

            //keep track of calculated tags using viterbi
            List<String> tagGuess = this.viterbi(words);

            //if tag matches calculation, add to goodGuess, otherwise, add to badGuess
            for (int i = 0; i < tags.length; i++) {
                if (tagGuess.get(i).equals(tags[i])) {
                    goodGuesses++;
                } else {
                    badGuesses++;
                }
            }
            if (print.equals("y")) {
                printTaggedLine(tagGuess, originalWords);
            }
        }
        //prints stats for given file
        if (eval.equals("y")) {
            System.out.println("\nNumber of correct tags: " + goodGuesses);
            System.out.println("Number of wrong tags: " + badGuesses);
            double percentCorrect = ((goodGuesses) / (double)(goodGuesses + badGuesses)) * 100;
            System.out.printf("Percent correct tags: %.2f%%", percentCorrect);
            System.out.println("\n");
        }
    }

    /**
     * prints the sentence and tags side by side
     * @param tags
     * @param words
     */
    public static void printTaggedLine(List<String> tags, String[] words) {
        String toPrint = "";
        for (int i = 0; i < tags.size(); i++) {
            toPrint += words[i] + "/" + tags.get(i) + " ";
        }
        System.out.println(toPrint);
    }

    /**
     * hard code a graph of sentences from recitation
     * @return
     */
    public static POSTagger createTest1() {
        Map<String, Map<String, Double>> observations = new HashMap<>();
        Map<String, Map<String, Double>> transitions = new HashMap<>();

        observations.put("NP", new HashMap<>());
        observations.put("N", new HashMap<>());
        observations.put("CNJ", new HashMap<>());
        observations.put("V", new HashMap<>());
        observations.get("NP").put("chase",10.0);
        observations.get("N").put("cat",4.0);
        observations.get("N").put("dog",4.0);
        observations.get("N").put("watch",2.0);
        observations.get("CNJ").put("and",10.0);
        observations.get("V").put("get",1.0);
        observations.get("V").put("chase",3.0);
        observations.get("V").put("watch",6.0);

        transitions.put("#", new HashMap<>());
        transitions.put("NP", new HashMap<>());
        transitions.put("N", new HashMap<>());
        transitions.put("CNJ", new HashMap<>());
        transitions.put("V", new HashMap<>());
        transitions.get("#").put("NP",3.0);
        transitions.get("#").put("N",7.0);
        transitions.get("NP").put("CNJ",2.0);
        transitions.get("NP").put("V",8.0);
        transitions.get("N").put("CNJ",2.0);
        transitions.get("N").put("V",8.0);
        transitions.get("CNJ").put("NP",2.0);
        transitions.get("CNJ").put("N",4.0);
        transitions.get("CNJ").put("V",4.0);
        transitions.get("V").put("NP",4.0);
        transitions.get("V").put("CNJ",2.0);
        transitions.get("V").put("N",4.0);

        return new POSTagger(observations,transitions);
    }
    public static POSTagger createTest4() {
        Map<String, Map<String, Double>> observations = new HashMap<>();
        Map<String, Map<String, Double>> transitions = new HashMap<>();

        observations.put("PRO", new HashMap<>());
        observations.put("V", new HashMap<>());
        observations.put("P", new HashMap<>());
        observations.put("N", new HashMap<>());
        observations.put("CNJ", new HashMap<>());
        observations.put("NP", new HashMap<>());
        observations.get("PRO").put("i",4.0);
        observations.get("PRO").put("him",2.0);
        observations.get("V").put("fish",2.0);
        observations.get("V").put("drink",4.0);
        observations.get("V").put("water",1.0);
        observations.get("P").put("with",3.0);
        observations.get("N").put("fish",3.0);
        observations.get("N").put("water",2.0);
        observations.get("N").put("salt",3.0);
        observations.get("N").put("plants",2.0);
        observations.get("CNJ").put("and",6.0);
        observations.get("NP").put("josh",2.0);

        transitions.put("#", new HashMap<>());
        transitions.put("NP", new HashMap<>());
        transitions.put("N", new HashMap<>());
        transitions.put("CNJ", new HashMap<>());
        transitions.put("V", new HashMap<>());
        transitions.put("PRO", new HashMap<>());
        transitions.put("P", new HashMap<>());
        transitions.get("#").put("PRO", 2.0);
        transitions.get("#").put("N", 3.0);
        transitions.get("#").put("NP", 1.0);
        transitions.get("PRO").put("V", 3.0);
        transitions.get("V").put("P", 2.0);
        transitions.get("V").put("N", 4.0);
        transitions.get("V").put("CNJ", 1.0);
        transitions.get("P").put("PRO", 2.0);
        transitions.get("P").put("NP", 1.0);
        transitions.get("N").put("V", 3.0);
        transitions.get("N").put("CNJ", 3.0);
        transitions.get("N").put("P", 1.0);
        transitions.get("CNJ").put("N", 3.0);
        transitions.get("CNJ").put("PRO", 2.0);
        transitions.get("CNJ").put("V", 1.0);
        transitions.get("NP").put("CNJ", 1.0);

        return new POSTagger(observations,transitions);
    }

    public static void main(String[] args) throws Exception {
        //game interface runs through main and methods above
        Scanner in = new Scanner(System.in);
        POSTagger test1 = createTest1();
        System.out.println("Would you like to test hardcoded model 1? Enter Y/N: ");
        String shouldTest1 = in.nextLine().toLowerCase();
        if (shouldTest1.equals("y")) {
            String[] testSentence = new String[]{"chase", "watch", "dog", "chase", "watch"};
            printTaggedLine(test1.viterbi(testSentence), testSentence);
        }

        System.out.println("Would you like to test simple model? Enter Y/N: ");
        String shouldTest2 = in.nextLine().toLowerCase();
        if (shouldTest2.equals("y")) {
            POSTagger test2 = new POSTagger();
            test2.modelTrainer("inputs/simple-train-sentences.txt", "inputs/simple-train-tags.txt");
            System.out.println("Entering console test:");
            test2.consoleTagger();

            System.out.println("Entering file test:");
            test2.fileTagger("inputs/simple-test-sentences.txt", "inputs/simple-test-tags.txt");
        }

        System.out.println("Would you like to test Brown model? Enter Y/N: ");
        String shouldTest3 = in.nextLine().toLowerCase();
        if (shouldTest3.equals("y")) {
            POSTagger test3 = new POSTagger();
            test3.modelTrainer("inputs/brown-train-sentences.txt", "inputs/brown-train-tags.txt");
            System.out.println("Entering console test:");
            test3.consoleTagger();

            System.out.println("Entering file test:");
            test3.fileTagger("inputs/brown-test-sentences.txt", "inputs/brown-test-tags.txt");
        }
        POSTagger test4 = createTest4();
        System.out.println("Would you like to test hardcoded model 2? Enter Y/N: ");
        String shouldTest4 = in.nextLine().toLowerCase();
        if (shouldTest4.equals("y")) {
            String[] testSentence = new String[]{"josh", "and", "water", "water", "fish"};
            printTaggedLine(test4.viterbi(testSentence), testSentence);
        }
    }
}