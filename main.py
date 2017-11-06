#!/usr/bin/env python

import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from experiment import *
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=["jinja2.ext.autoescape"],
    autoescape=True)


class ResponseSet(ndb.Model):
    experiment_version =  ndb.IntegerProperty();
    responses = ndb.StringProperty();
    percent_correct = ndb.FloatProperty();


class MainHandler(webapp2.RequestHandler):
    def get(self):
        prompts = ACTIVE_EXPERIMENT.prompts;
        promptHTML = "";
        prompt_index = 1;
        for prompt in prompts:
            promptHTML += self.makeHTMLForPrompt(prompt, prompt_index);
            prompt_index += 1;

        template_values = {"prompts": promptHTML, "final_index": (len(prompts) + 1)};
        template = JINJA_ENVIRONMENT.get_template('index.html');
        self.response.write(template.render(template_values));

    def makeHTMLForPrompt(self, prompt, index):
        choiceHTML = "";
        choice_index = 0;
        for choice in prompt.choices:
            choiceHTML += "<p><a href=\"javascript:recordChoiceAndAdvanceToNext(%d, %d);\">%s</a></p>"\
             % (choice_index, index, choice);
            choice_index += 1;

        return "<div class=\"page\" id=\"%d\" style=\"text-align: center\">\
            <p><img src=\"/images/speaker.png\" width=\"25&#37;\"/></p>\
            <br />\
            <br />\
            %s\
          <audio>\
            <source src=\"/sounds/%s\" type=\"audio/mpeg\" />\
            Your browser does not support modern audio.\
          </audio>\
        </div>" % (index, choiceHTML, prompt.stimulus);


class EndHandler(webapp2.RequestHandler):
    def showErrorPage(self):
        template = JINJA_ENVIRONMENT.get_template('end_bad.html');
        self.response.write(template.render({}));

    def get(self):
        self.showErrorPage();

    def post(self):
        prompts = ACTIVE_EXPERIMENT.prompts;
        choices_json = self.request.get("choices");
        choices = json.loads(choices_json);
        if (len(choices) != len(prompts)):
            logging.error("Unequal number of choices vs prompts!");
            self.showErrorPage();
        else:
            prompt_index = 0;
            correct_count = 0;
            for prompt in prompts:
                if prompt.correct_index == choices[prompt_index]:
                    correct_count += 1;
                prompt_index += 1;
            correct_percent = 100 * correct_count / len(prompts);

            response_set = ResponseSet();
            response_set.experiment_version = ACTIVE_EXPERIMENT.version;
            response_set.responses = choices_json;
            response_set.percent_correct = correct_percent;
            response_set.put();

            template = JINJA_ENVIRONMENT.get_template('end_good.html');
            self.response.write(template.render({"correct": correct_percent}));


app = webapp2.WSGIApplication([('/', MainHandler), ('/end', EndHandler)], debug=True)
