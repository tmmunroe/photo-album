
# Welcome to your CDK Python project!

cdk deploy - deploys deployment pipeline; which in turn builds cloudformation for all stacks

run lambda to create opensearch index - set up proper analyzer for opensearch

update api key and api url in frontend app





This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

## Lambda Layers

 * use lambda layers to deploy libraries that your lambda handler depends on 

 * Generate Lambda Layer

        ./gen-lambda-layer.sh

 * Deploy application

        cdk synth # test generation of CloudFormation

        cdk diff # check diffs

        cdk deploy # to deploy

 * Test endpoints

        curl -X GET https://GUID.execute-api.REGION.amazonaws.com/prod/

sam local invoke PhotoAlbumIndexer --no-event -t ./cdk.out/PhotoAlbumStack.template.json

sam local invoke PhotoAlbumIndexer -e ./s3_put_event.json -t ./cdk.out/PhotoAlbumStack.template.json


TODO:

use models in the indexing code

handle multiple query terms