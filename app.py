#!/usr/bin/env python3

from aws_cdk import App

from resourcetagging.tagging_stack import ResourceTaggingStack

app = App()
ResourceTaggingStack(app, "resource-tagging-automation")

app.synth()
