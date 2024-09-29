import java.io.*;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.TreeMap;

/**
 * Uses Huffman interface to compress and decompress files
 */
public class Compression implements Huffman {
    TreeComparator compareTrees = new TreeComparator();
    PriorityQueue<BinaryTree<CodeTreeElement>> pq = new PriorityQueue<>(compareTrees);
    public Compression() {
    }
    public Map<Character, Long> countFrequencies(String pathName) throws IOException {
        BufferedReader input = new BufferedReader(new FileReader(pathName));
        Map<Character, Long> frequencies = new TreeMap<>();
        try {
            int i = input.read();
            while (i != -1) {
                Character c = (char) i;
                if (frequencies.containsKey(c)) {
                    frequencies.put(c, frequencies.get(c) + 1);
                } else {
                    frequencies.put(c, (long) 1);
                }
                i = input.read();
            }
        }
        catch (IOException e) {
            System.out.println("file does not exist");
        }
        input.close();
        return frequencies;
    }
    public BinaryTree<CodeTreeElement> makeCodeTree(Map<Character, Long> frequencies) {
        for (Character key: frequencies.keySet()) {
            CodeTreeElement e = new CodeTreeElement(frequencies.get(key), key);
            BinaryTree<CodeTreeElement> bt = new BinaryTree<>(e);
            pq.add(bt);
        }
        while (pq.size() != 1) {
            BinaryTree<CodeTreeElement> t1 = pq.remove();
            BinaryTree<CodeTreeElement> t2 = pq.remove();
            CodeTreeElement r = new CodeTreeElement(t1.getData().getFrequency() + t2.getData().getFrequency(), null);
            BinaryTree<CodeTreeElement> t = new BinaryTree<>(r, t1, t2);
            pq.add(t);
        }
        System.out.println(pq.peek());
    return pq.peek();
    }
    public Map<Character, String> computeCodes(BinaryTree<CodeTreeElement> codeTree) {
        Map<Character, String> codeMap = new TreeMap<>();
        codeHelper(codeTree, codeMap, "");
        return codeMap;
    }
    public void codeHelper(BinaryTree<CodeTreeElement> pathSoFar, Map<Character, String> codeMap, String code) {
        if (pathSoFar.isLeaf()) {
            codeMap.put(pathSoFar.getData().getChar(), code);
        }
        if (pathSoFar.hasLeft()) {
            codeHelper(pathSoFar.getLeft(), codeMap, code+"0");
        }
        if (pathSoFar.hasRight()) {
            codeHelper(pathSoFar.getRight(), codeMap, code+"1");
        }
    }
    public void compressFile(Map<Character, String> codeMap, String pathName, String compressedPathName) throws IOException {
        BufferedReader input = new BufferedReader(new FileReader(pathName));
        BufferedBitWriter bitOutput = new BufferedBitWriter(compressedPathName);
        int i = input.read();
        while (i != -1) {

            Character c = (char) i;
            String code = codeMap.get(c);
            if (code != null) {
                for (char ch : code.toCharArray()) {
                    if (ch == '0') {
                        bitOutput.writeBit(false);
                    } else if (ch == '1') {
                        bitOutput.writeBit(true);
                    }
                }
            }
            i = input.read();
        }
        input.close();
        bitOutput.close();
    }
    public void decompressFile(String compressedPathName, String decompressedPathName, BinaryTree<CodeTreeElement> codeTree) throws IOException {
        BufferedBitReader bitInput = new BufferedBitReader(compressedPathName);
        BufferedWriter output = new BufferedWriter(new FileWriter(decompressedPathName));
        BinaryTree<CodeTreeElement> location = codeTree;
        while (bitInput.hasNext()) {
            boolean bit = bitInput.readBit();
            if (bit) {
                location = location.getRight();
            }
            else {
                location = location.getLeft();
            }
            if (location.isLeaf()) {
                Character c = location.getData().getChar();
                output.write(c);
                location = codeTree;
            }
        }
        bitInput.close();
        output.close();
    }

    public static void main(String[] args) throws IOException {
        Compression compressor = new Compression();
        Map<Character, Long> frequencyMap = compressor.countFrequencies("inputs/test1.txt");
        BinaryTree<CodeTreeElement> codeTree = compressor.makeCodeTree(frequencyMap);
        Map<Character, String> codeMap = compressor.computeCodes(codeTree);
        System.out.println(codeMap);
        compressor.compressFile(codeMap, "inputs/test1.txt", "inputs/test1_compressed.txt");
        compressor.decompressFile("inputs/test1_compressed.txt", "inputs/test1_decompressed.txt", codeTree);

    }
}
