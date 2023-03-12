import aws_cdk as core
import aws_cdk.assertions as assertions

from birthday_discord_bot.birthday_discord_bot_stack import BirthdayDiscordBotStack

# example tests. To run these tests, uncomment this file along with the example
# resource in birthday_discord_bot/birthday_discord_bot_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = BirthdayDiscordBotStack(app, "birthday-discord-bot")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
