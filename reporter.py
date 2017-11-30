from protorpc import messages
from experiment import *
from math import sqrt

class OrganizerType(messages.Enum):
    PHONEME = 0;
    TOKEN = 1;


def generateCSVResultsForSentences(organizerType):
    if not isinstance(organizerType, OrganizerType):
        return "invalid organizer type";

    resultsByOrganizerBySUID = {};

    allSentenceResponses = TrialResponse.query(TrialResponse.trialSentenceID != None).fetch();

    for sentenceResponse in allSentenceResponses:

        subjectID = sentenceResponse.subjectID;

        phoneme = sentenceResponse.trialBeginningPhoneme;
        if organizerType == OrganizerType.PHONEME:
            organizer = phoneme;
        else:
            organizer = sentenceResponse.trialToken + "," + phoneme;

        if resultsByOrganizerBySUID.has_key(subjectID):
            resultsByOrganizer = resultsByOrganizerBySUID[subjectID];
        else:
            resultsByOrganizer = {};
            resultsByOrganizerBySUID[subjectID] = resultsByOrganizer;

        if resultsByOrganizer.has_key(organizer):
            aggResults = resultsByOrganizer[organizer];
        else:
            congruentResults = AggregateResult();
            incongruentResults = AggregateResult();
            aggResults = [incongruentResults, congruentResults];

        index = 0;
        if sentenceResponse.trialCongruence == "C":
            index = 1;

        if sentenceResponse.position == "pre":
            aggResults[index].notePreResponseWithReactionTime(sentenceResponse.isCorrect, sentenceResponse.reactionTime);
        elif sentenceResponse.position == "post":
            aggResults[index].notePostResponseWithReactionTime(sentenceResponse.isCorrect, sentenceResponse.reactionTime);
        else:
            print "Unknown position encountered: " + sentenceResponse.position;
        resultsByOrganizer[organizer] = aggResults;


    if organizerType == OrganizerType.PHONEME:
        csvResults = "suid,phoneme,congruency,percent_correct_pre,percent_correct_post,rxn_time_pre,rxn_time_post,rxn_time_sd_pre,rxn_time_sd_post\n";
    else:
        csvResults = "suid,token,phoneme,congruency,percent_correct_pre,percent_correct_post,rxn_time_pre,rxn_time_post,rxn_time_sd_pre,rxn_time_sd_post\n";

    for key in resultsByOrganizerBySUID:
        resultsByOrganizer = resultsByOrganizerBySUID[key];
        for organizer in resultsByOrganizer:
            aggResults = resultsByOrganizer[organizer];
            for i in [0, 1]:
                aggResult = aggResults[i];
                percent_pre = aggResult.getPercentCorrectPre();
                percent_post = aggResult.getPercentCorrectPost();
                times_mean_pre = aggResult.getPreMeanReactionTime();
                times_mean_post = aggResult.getPostMeanReactionTime();
                times_sd_pre = aggResult.getPreReactionTimeSD();
                times_sd_post = aggResult.getPostReactionTimeSD();
                congruence = "C" if (i == 1) else "I";
                csvResults += "%s,%s,%s,%d,%d,%d,%d,%d,%d\n"\
                % (key, organizer, congruence, percent_pre, percent_post, times_mean_pre, times_mean_post, times_sd_pre, times_sd_post);

    return csvResults;


def generateCSVResultsForWords(organizerType):
    if not isinstance(organizerType, OrganizerType):
        return "invalid organizer type";

    resultsByOrganizerBySUID = {};

    allWordResponses = TrialResponse.query(TrialResponse.trialSentenceID == None).fetch();

    for wordResponse in allWordResponses:

        subjectID = wordResponse.subjectID;

        phoneme = wordResponse.trialBeginningPhoneme;
        if organizerType == OrganizerType.PHONEME:
            organizer = phoneme;
        else:
            organizer = wordResponse.trialToken + "," + phoneme;

        if resultsByOrganizerBySUID.has_key(subjectID):
            resultsByOrganizer = resultsByOrganizerBySUID[subjectID];
        else:
            resultsByOrganizer = {};
            resultsByOrganizerBySUID[subjectID] = resultsByOrganizer;

        if resultsByOrganizer.has_key(organizer):
            aggResult = resultsByOrganizer[organizer];
        else:
            aggResult = AggregateResult();

        if wordResponse.position == "pre":
            aggResult.notePreResponseWithReactionTime(wordResponse.isCorrect, wordResponse.reactionTime);
        elif wordResponse.position == "post":
            aggResult.notePostResponseWithReactionTime(wordResponse.isCorrect, wordResponse.reactionTime);
        else:
            print "Unknown position encountered: " + wordResponse.position;

        resultsByOrganizer[organizer] = aggResult;

    if organizerType == OrganizerType.PHONEME:
        csvResults = "suid,phoneme,percent_correct_pre,percent_correct_post,rxn_time_pre,rxn_time_post,rxn_time_sd_pre,rxn_time_sd_post\n";
    else:
        csvResults = "suid,token,phoneme,percent_correct_pre,percent_correct_post,rxn_time_pre,rxn_time_post,rxn_time_sd_pre,rxn_time_sd_post\n";

    for key in resultsByOrganizerBySUID:
        resultsByOrganizer = resultsByOrganizerBySUID[key];
        for organizer in resultsByOrganizer:
            aggResults = resultsByOrganizer[organizer];
            percent_pre = aggResults.getPercentCorrectPre();
            percent_post = aggResults.getPercentCorrectPost();
            times_mean_pre = aggResults.getPreMeanReactionTime();
            times_mean_post = aggResults.getPostMeanReactionTime();
            times_sd_pre = aggResults.getPreReactionTimeSD();
            times_sd_post = aggResults.getPostReactionTimeSD();
            csvResults += "%s,%s,%d,%d,%d,%d,%d,%d\n"\
            % (key, organizer, percent_pre, percent_post, times_mean_pre, times_mean_post, times_sd_pre, times_sd_post);

    return csvResults;


class AggregateResult:
    def __init__(self):
        self.preReactionTimes = [];
        self.postReactionTimes = [];
        self.preTotalCount = 0;
        self.preCorrectCount = 0;
        self.postTotalCount = 0;
        self.postCorrectCount = 0;
    def notePreResponseWithReactionTime(self, isCorrect, time):
        self.preTotalCount += 1;
        self.preCorrectCount += 1 if isCorrect else 0;
        self.preReactionTimes.append(float(time));
    def notePostResponseWithReactionTime(self, isCorrect, time):
        self.postTotalCount += 1;
        self.postCorrectCount += 1 if isCorrect else 0;
        self.postReactionTimes.append(float(time));
    def getPercentCorrectPre(self):
        if self.preTotalCount > 0:
            return (100.0 * self.preCorrectCount) / self.preTotalCount;
        else:
            return -1;
    def getPercentCorrectPost(self):
        if self.postTotalCount > 0:
            return (100.0 * self.postCorrectCount) / self.postTotalCount;
        else:
            return -1;
    def getPreMeanReactionTime(self):
        return getMean(self.preReactionTimes);
    def getPostMeanReactionTime(self):
        return getMean(self.postReactionTimes);
    def getPreReactionTimeSD(self):
        return getSD(self.preReactionTimes);
    def getPostReactionTimeSD(self):
        return getSD(self.postReactionTimes);


def getMean(values):
    if len(values) > 0:
        return float(sum(values)) / len(values);
    else:
        return -1;


def getSD(values):
    if len(values) > 0:
        mean = float(sum(values)) / len(values);
        variance = 0;
        for v in values:
            variance += pow((v - mean), 2);
        variance /= len(values);
        return sqrt(variance);
    else:
        return -1;
