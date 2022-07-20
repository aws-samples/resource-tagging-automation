#!/bin/bash
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

npm install -g aws-cdk

python3 -m venv .venv

case "$OSTYPE" in
  darwin*)  source .venv/bin/activate ;; 
  linux*)   source .venv/bin/activate ;;
  msys*)    .venv\Scripts\activate.bat ;;
  cygwin*)  .venv\Scripts\activate.bat ;;
  *)        echo "unknown: $OSTYPE" ;;
esac

pip3 install -r requirements.txt

cdk bootstrap

cdk destroy --force

cdk deploy --require-approval never \
--parameters tags='{"TagName1": "TagValue1","TagName2": "TagValue2"}'
