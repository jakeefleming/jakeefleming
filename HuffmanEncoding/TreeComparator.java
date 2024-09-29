import java.util.Comparator;

/**
 * compares trees so they can be added to priority queue
 */
public class TreeComparator implements Comparator<BinaryTree<CodeTreeElement>> {
    public int compare(BinaryTree<CodeTreeElement> t1, BinaryTree<CodeTreeElement> t2) {
        if (t1.getData().getFrequency() < t2.getData().getFrequency()) {
            return -1;
        }
        else if (t1.getData().getFrequency() > t2.getData().getFrequency()) {
            return 1;
        }
        else {
            return 0;
        }
    }
}
