from google.appengine.ext import ndb
import random
import csv

DEBUG = False;
SIZE_LIMIT = 2;


class Trial:
    def __init__(self, token, falseChoice, beginningPhoneme, speakerID):
        self.token = token;
        self.beginningPhoneme = beginningPhoneme;
        self.speakerID = speakerID;
        self.correctResponseIndex = random.choice([0,1]);
        if self.correctResponseIndex == 0 :
            self.responseChoices = [token, falseChoice];
        else:
            self.responseChoices = [falseChoice, token];

    def getSoundFileName(self):
        return self.token + "_W3_" + self.speakerID + ".wav";

class SentenceTrial(Trial):
    def __init__(self, token, falseChoice, beginningPhoneme, speakerID, sentenceID, congruence):
        Trial.__init__(self, token, falseChoice, beginningPhoneme, speakerID);
        self.sentenceID = sentenceID;
        self.congruence = congruence;

    def getSoundFileName(self):
        return self.token + "_" + self.sentenceID + "_" + self.congruence + "_" + self.speakerID + ".wav";


class WordTrialSet:
    def __init__(self, spec_csv_filename):
        with open(spec_csv_filename, 'rb') as spec_file:
            self.trials = [];
            spec_reader = csv.reader(spec_file);
            for row in spec_reader:
                if DEBUG and len(self.trials) >= SIZE_LIMIT:
                    break;
                if len(row) != 4:
                    logging.error("Invalid CSV for word trial set!");
                else:
                    newTrial = Trial(row[0], row[3], row[2], row[1]);
                    self.trials.append(newTrial);


class SentenceTrialSet:
    def __init__(self, spec_csv_filename):
        with open(spec_csv_filename, 'rb') as spec_file:
            self.trials = [];
            spec_reader = csv.reader(spec_file);
            for row in spec_reader:
                if DEBUG and len(self.trials) >= SIZE_LIMIT:
                    break;
                if len(row) != 6:
                    logging.error("Invalid CSV for sentence trial set!");
                else:
                    newTrial = SentenceTrial(row[0], row[5], row[4], row[3], row[1], row[2]);
                    self.trials.append(newTrial);


class TrialResponse(ndb.Model):
    subjectID = ndb.StringProperty();
    position = ndb.StringProperty(); # either "pre" or "post"
    trialIndex = ndb.IntegerProperty();
    trialToken = ndb.StringProperty();
    trialBeginningPhoneme = ndb.StringProperty();
    trialCongruence = ndb.StringProperty();
    trialSpeakerID = ndb.StringProperty();
    trialSentenceID = ndb.StringProperty();
    isCorrect = ndb.BooleanProperty();
    reactionTime = ndb.IntegerProperty();
    timestamp = ndb.IntegerProperty();


PRETEST_WORD_TRIAL_SET = WordTrialSet("specs/word_pretest_trials.csv");
POSTTEST_WORD_TRIAL_SET = WordTrialSet("specs/word_posttest_trials.csv");
PRETEST_SENTENCE_TRIAL_SET = SentenceTrialSet("specs/sentence_pretest_trials.csv");
POSTTEST_SENTENCE_TRIAL_SET = SentenceTrialSet("specs/sentence_posttest_trials.csv");
