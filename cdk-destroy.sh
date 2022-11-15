#!/bin/bash
STACKS="$(cdk list | tr '\n' ' ')"
cdk destroy ${STACKS}