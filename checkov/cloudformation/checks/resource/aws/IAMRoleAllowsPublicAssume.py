import json
from typing import List

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class IAMRoleAllowsPublicAssume(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IAM role allows only specific services or principals to assume it"
        id = "CKV_AWS_60"
        supported_resources = ['AWS::IAM::Role']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        self.evaluated_keys = ["Properties/AssumeRolePolicyDocument/Statement"]
        if 'Properties' in conf:
            properties = conf['Properties']
            if 'AssumeRolePolicyDocument' in properties:
                assume_role_policy_doc = properties['AssumeRolePolicyDocument']
                if isinstance(assume_role_policy_doc, str):
                    assume_role_policy_doc = json.loads(assume_role_policy_doc)
                if 'Statement' in assume_role_policy_doc:
                    statements = assume_role_policy_doc['Statement']
                    if isinstance(statements, list):
                        for statement_index, statement in enumerate(statements):
                            if 'Effect' in statement:
                                if statement['Effect'] == "Deny":
                                    continue
                            if 'Principal' in statement:
                                principal = statement['Principal']
                                if 'AWS' in principal:
                                    aws_principals = principal['AWS']
                                    if aws_principals == "*":
                                        self.evaluated_keys = [f"Properties/AssumeRolePolicyDocument/Statement/[{statement_index}]/Principal/AWS"]
                                        return CheckResult.FAILED
                                    if isinstance(aws_principals, list):
                                        for principal_index, principal in enumerate(aws_principals):
                                            if principal == "*":
                                                self.evaluated_keys = [
                                                    f"Properties/AssumeRolePolicyDocument/Statement/[{statement_index}]/Principal/[{principal_index}]/AWS"]
                                                return CheckResult.FAILED
        return CheckResult.PASSED


check = IAMRoleAllowsPublicAssume()
