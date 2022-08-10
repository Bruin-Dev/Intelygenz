import boto3


def get_resources_from_describe(ssm_details):
    results = ssm_details['Parameters']
    resources = [result for result in results]
    next_token = ssm_details.get('NextToken', None)
    return resources, next_token


def get_parameter_store(event, context):
    client = boto3.client('ssm')

    next_token = ' '
    resources = []
    parameter_dict = {}

    while next_token is not None:
        ssm_details = client.describe_parameters(MaxResults=50, NextToken=next_token)
        current_batch, next_token = get_resources_from_describe(ssm_details)
        resources += current_batch

    for resource in resources:
        response = client.get_parameter(Name=resource['Name'], WithDecryption=True)
        parameter_dict[resource['Name']] = response['Parameter']['Value']

    with open('/tmp/ssm_backup.txt', 'w') as ssm_backup:
        for key, value in parameter_dict.items():
            print('%s:%s\n' % (key, value))
            ssm_backup.write('%s:%s\n' % (key, value))
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('/tmp/ssm_backup.txt', 'ssmbackupbucket', 'ssm_backup.txt')
