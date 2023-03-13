import aws_cdk as cdk
from aws_cdk import aws_lambda

lambda_code = aws_lambda.Code.from_asset(
    "resources",
    bundling=cdk.BundlingOptions(
        image=aws_lambda.Runtime.PYTHON_3_8.bundling_image,
        command=[
            "bash",
            "-c",
            "pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output",
        ],
    ),
)
