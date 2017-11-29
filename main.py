#!/usr/bin/env python

import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from experiment import *
import json
import logging
import hashlib
from math import sqrt


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=["jinja2.ext.autoescape"],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('new.html');
        self.response.write(template.render({}));

    def post(self):
        activeSubjectID = self.request.get("subject_id");
        if len(activeSubjectID) < 1:
            template = JINJA_ENVIRONMENT.get_template('end_bad.html');
            self.response.write(template.render({}));
        else:
            template = JINJA_ENVIRONMENT.get_template('console.html');
            self.response.write(template.render({"subject_id": activeSubjectID}));


class BeginPhaseHandler(webapp2.RequestHandler):
    # Sublcasses must override to return a TrialSet object.
    def getActiveTrialSet(self):
        raise NotImplementedError;

    # Sublcasses must override to return the result submission URL.
    def getEndURL(self):
        raise NotImplementedError;

    def get(self):
        activeSubjectID = self.request.get("suid");
        if activeSubjectID is None:
            template = JINJA_ENVIRONMENT.get_template('end_bad.html');
            self.response.write(template.render({}));
            return;

        trials = self.getActiveTrialSet().trials;
        trialHTML = "";
        trialIndex = 1;
        for trial in trials:
            trialHTML += self.makeHTMLForTrial(trial, trialIndex);
            trialIndex += 1;
        endURL = self.getEndURL() + "?suid=" + activeSubjectID;
        template_values = {"trials": trialHTML, "final_index": (len(trials) + 1), "end_url": endURL};
        template = JINJA_ENVIRONMENT.get_template('experiment.html');
        self.response.write(template.render(template_values));

    def makeHTMLForTrial(self, trial, index):
        responseHTML = "";
        for response in trial.responseChoices:
            responseHTML += "<p><a href=\"#\">%s</a></p>" % (response);

        return "<div class=\"page\" id=\"%d\" style=\"text-align: center\">\
            <p><img src=\"/images/speaker.png\" width=\"25&#37;\"/></p>\
            <br />\
            <br />\
            %s\
          <audio>\
            <source src=\"/sounds/%s\" type=\"audio/wav\" />\
            Your browser does not support modern audio.\
          </audio>\
        </div>" % (index, responseHTML, trial.getSoundFileName());


class EndPhaseHandler(webapp2.RequestHandler):
    # Subclasses must override to return either "pre" or "post"
    def getPositionID(self):
        raise NotImplementedError;

    # Sublcasses must override to return a TrialSet object.
    def getActiveTrialSet(self):
        raise NotImplementedError;

    def showErrorPage(self):
        template = JINJA_ENVIRONMENT.get_template('end_bad.html');
        self.response.write(template.render({}));

    def get(self):
        self.showErrorPage();

    def post(self):
        activeSubjectID = self.request.get("suid");
        response_json = self.request.get("responses");
        response_times_json = self.request.get("reaction_times");
        timestamps_json = self.request.get("timestamps");

        print "response_json: " + response_json;
        responses = json.loads(response_json);

        print "response_times_json: " + response_times_json;
        response_times = json.loads(response_times_json);

        print "timestamps_json: " + timestamps_json;
        timestamps = json.loads(timestamps_json);

        trials = self.getActiveTrialSet().trials;

        if (len(responses) != len(trials)) or (len(responses) != len(response_times)):
            logging.error("Unequal number of responses vs trials!");
            self.showErrorPage();
        else:
            trialIndex = 0;
            persistentResponseList = [];
            for trial in trials:
                userResponse = responses[trialIndex];
                response = TrialResponse();
                response.isCorrect = (trial.correctResponseIndex == userResponse);
                response.reactionTime = response_times[trialIndex];
                response.timestamp = timestamps[trialIndex];
                response.position = self.getPositionID();
                response.subjectID = activeSubjectID;
                response.trialIndex = trialIndex;
                response.trialToken = trial.token;
                response.trialBeginningPhoneme = trial.beginningPhoneme;
                response.trialSpeakerID = trial.speakerID;
                if isinstance(trial, SentenceTrial):
                    response.trialCongruence = trial.congruence;
                    response.trialSentenceID = trial.sentenceID;
                persistentResponseList.append(response);
                trialIndex += 1;

            if len(persistentResponseList) > 0:
                ndb.put_multi(persistentResponseList);

            template = JINJA_ENVIRONMENT.get_template('end_good.html');
            self.response.write(template.render({"save_count": trialIndex}));


class WordPretestHandler(BeginPhaseHandler):
    def getActiveTrialSet(self):
        return PRETEST_WORD_TRIAL_SET;
    def getEndURL(self):
        return "/wpre/end";

class WordPosttestHandler(BeginPhaseHandler):
    def getActiveTrialSet(self):
        return POSTTEST_WORD_TRIAL_SET;
    def getEndURL(self):
        return "/wpost/end";

class SentencePretestHandler(BeginPhaseHandler):
    def getActiveTrialSet(self):
        return PRETEST_SENTENCE_TRIAL_SET;
    def getEndURL(self):
        return "/spre/end";

class SentencePosttestHandler(BeginPhaseHandler):
    def getActiveTrialSet(self):
        return POSTTEST_SENTENCE_TRIAL_SET;
    def getEndURL(self):
        return "/spost/end";

class WordPretestEndHandler(EndPhaseHandler):
    def getActiveTrialSet(self):
        return PRETEST_WORD_TRIAL_SET;
    def getPositionID(self):
        return "pre";

class WordPosttestEndHandler(EndPhaseHandler):
    def getActiveTrialSet(self):
        return POSTTEST_WORD_TRIAL_SET;
    def getPositionID(self):
        return "post";

class SentencePretestEndHandler(EndPhaseHandler):
    def getActiveTrialSet(self):
        return PRETEST_SENTENCE_TRIAL_SET;
    def getPositionID(self):
        return "pre";

class SentencePosttestEndHandler(EndPhaseHandler):
    def getActiveTrialSet(self):
        return POSTTEST_SENTENCE_TRIAL_SET;
    def getPositionID(self):
        return "post";

class ResultDownloadHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('download.html');
        self.response.write(template.render());

    def post(self):
        password = self.request.get("password");
        fileType = self.request.get("file_type");

        passwordHash = hashlib.md5(password).hexdigest();

        if passwordHash != "79a43dc64b1107a2185670f603e80c0d":
            template = JINJA_ENVIRONMENT.get_template('end_bad.html');
            self.response.write(template.render({}));
        else:
            csvResults = "";
            if fileType == "1":
                csvResults = self.generateCSVResultsForSentencesByPhoneme();
            elif fileType == "2":
                csvResults = self.generateCSVResultsForWordByPhoneme();
            elif fileType == "3":
                csvResults = self.generateCSVResultsForWordsByPhoneme();
            else:
                csvResults = self.generateCSVResultsForWordsByPhoneme();
            self.response.headers["Content-Type"] = "text/csv";
            self.response.headers["Content-Disposition"] = "attachment; filename=results.csv";
            self.response.write(csvResults);

    def generateCSVResultsForSentencesByPhoneme(self):
        resultsByPhonemeBySUID = {};
        allSentenceResponses = TrialResponse.query(TrialResponse.trialSentenceID != None).fetch();
        for sentenceResponse in allSentenceResponses:
            subjectID = sentenceResponse.subjectID;
            phoneme = sentenceResponse.trialBeginningPhoneme;
            if resultsByPhonemeBySUID.has_key(subjectID):
                resultsByCongruencyByPhoneme = resultsByPhonemeBySUID[subjectID];
            else:
                resultsByPhoneme = {};
                resultsByPhonemeBySUID[subjectID] = resultsByPhoneme;
            if resultsByPhoneme.has_key(phoneme):
                aggResults = resultsByPhoneme[phoneme];
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
            resultsByPhoneme[phoneme] = aggResults;

        csvResults = "suid,phoneme,congruency,percent_correct_pre,percent_correct_post,rxn_time_pre,rxn_time_post,rxn_time_sd_pre,rxn_time_sd_post\n";
        for key in resultsByPhonemeBySUID:
            resultsByPhoneme = resultsByPhonemeBySUID[key];
            for phoneme in resultsByPhoneme:
                aggResults = resultsByPhoneme[phoneme];
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
                     % (key, phoneme, congruence, percent_pre, percent_post, times_mean_pre, times_mean_post, times_sd_pre, times_sd_post);
        return csvResults;

    def generateCSVResultsForWordsByPhoneme(self):
        resultsByPhonemeBySUID = {};
        allWordResponses = TrialResponse.query(TrialResponse.trialSentenceID == None).fetch();
        for wordResponse in allWordResponses:
            subjectID = wordResponse.subjectID;
            phoneme = wordResponse.trialBeginningPhoneme;
            if resultsByPhonemeBySUID.has_key(subjectID):
                resultsByPhoneme = resultsByPhonemeBySUID[subjectID];
            else:
                resultsByPhoneme = {};
                resultsByPhonemeBySUID[subjectID] = resultsByPhoneme;
            if resultsByPhoneme.has_key(phoneme):
                aggResult = resultsByPhoneme[phoneme];
            else:
                aggResult = AggregateResult();
            if wordResponse.position == "pre":
                aggResult.notePreResponseWithReactionTime(wordResponse.isCorrect, wordResponse.reactionTime);
            elif wordResponse.position == "post":
                aggResult.notePostResponseWithReactionTime(wordResponse.isCorrect, wordResponse.reactionTime);
            else:
                print "Unknown position encountered: " + wordResponse.position;
            resultsByPhoneme[phoneme] = aggResult;

        csvResults = "suid,phoneme,percent_correct_pre,percent_correct_post,rxn_time_pre,rxn_time_post,rxn_time_sd_pre,rxn_time_sd_post\n";
        for key in resultsByPhonemeBySUID:
            resultsByPhoneme = resultsByPhonemeBySUID[key];
            for phoneme in resultsByPhoneme:
                aggResults = resultsByPhoneme[phoneme];
                percent_pre = aggResults.getPercentCorrectPre();
                percent_post = aggResults.getPercentCorrectPost();
                times_mean_pre = aggResults.getPreMeanReactionTime();
                times_mean_post = aggResults.getPostMeanReactionTime();
                times_sd_pre = aggResults.getPreReactionTimeSD();
                times_sd_post = aggResults.getPostReactionTimeSD();
                csvResults += "%s,%s,%d,%d,%d,%d,%d,%d\n"\
                 % (key, phoneme, percent_pre, percent_post, times_mean_pre, times_mean_post, times_sd_pre, times_sd_post);
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


handlerMappings = [
('/', MainHandler),
('/wpre', WordPretestHandler),
('/wpre/end', WordPretestEndHandler),
('/spre', SentencePretestHandler),
('/spre/end', SentencePretestEndHandler),
('/wpost', WordPosttestHandler),
('/wpost/end', WordPosttestEndHandler),
('/spost', SentencePosttestHandler),
('/spost/end', SentencePosttestEndHandler),
('/resdolo', ResultDownloadHandler)
];

app = webapp2.WSGIApplication(handlerMappings, debug=True)
