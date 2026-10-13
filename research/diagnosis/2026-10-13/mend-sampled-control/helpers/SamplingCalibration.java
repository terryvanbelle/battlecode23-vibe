package samplefixture;

/** Synthetic own code for zero-game loader-cache/metering fixtures only. */
public final class SamplingCalibration {
    static int helper(int input) {return input*7+3;}
    public static int burn(int input) {
        int answer=0;
        for(int i=0;i<19;i++)answer+=helper(input+i);
        return answer;
    }
}
