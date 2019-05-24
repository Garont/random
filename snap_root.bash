#!/bin/bash

export AWS_DEFAULT_REGION='us-east-2'
export AWS_ACCESS_KEY_ID='AKIAxxxxxxxxxxxx'
export AWS_SECRET_ACCESS_KEY='xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

## instancexxx
DESC=$(date +instancexxx-root-%d-%m-%Y)
aws ec2 create-snapshot --volume-id vol-0101010101 --description "$DESC"
