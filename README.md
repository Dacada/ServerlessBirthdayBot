# How to build this

Hello future me (most likely). If you're reading this, it's been a while since you last tried to get this thing running.

- Install the following if not already installed:
  - [aws-cli](https://archlinux.org/packages/extra/any/aws-cli/)
  - [aws-cdk](https://aur.archlinux.org/packages/aws-cdk)
  - [nvm](https://aur.archlinux.org/packages/nvm)
  - [docker](https://wiki.archlinux.org/title/Docker)
    - Make sure it's properly set up as per the wiki (e.g. you can run a container)
- Get the AWS creds, if you don't have them on hand:
  - Check IAM > Security Credentials and create a new Access Key
- Setup a `.env` with `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
  - Check where stuff is in the console for the default region
- Get the discord bot creds if you don't have them on hand:
  - Add some dummy value, in the follow up step when you do a diff it will show you the environment variable difference
    and you can get the right value
- Add to the `.env` the `DISCORD_APPLICATION_ID`, `DISCORD_BOT_TOKEN`, `DISCORD_PUBLIC_KEY`
- Create a virtual environment and `pip install -r requirements.txt` into it
- Install and use npm version 18 (`nvm instll 18 && nvm use 18`)
- Remember to source the `.env`
- If you update the python version you likely also want to update the dependencies on `resources/requirements.txt` (use a different `venv`)
- Run `cdk synth`
- Run `cdk diff` for each of the stacks, check nothing major changes, and get the right values for the Discord stuff if
  you lost them
- If you want to deploy, `cdk deploy`
  
## Other useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
