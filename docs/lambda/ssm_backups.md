# 1. Summary

We utilize the boto3 library to get the data from the parameter store. We utilize the `describe_parameters` function
to get all the data from the Parameter store. Since the max size of the response is 50 items we need to loop a couple
times calling `describe_parameters`.

`describe_parameters` provides all the necessary data related to the parameter from the parameter store EXCEPT the
value. In order to get the unencrypted value we need to call `get_parameter` for each parameter gotten from `describe_parameters`
response.

Once we have all the data for each parameter, we take each parameter name and value and place it in a dictionary with name 
being the key and the value being the value of that dictionary. We then format that dictionary in a file (ssm_backups.txt) looking something like:

#### ssm_backups.txt
```
some_parameter_name:12
...
...
```

Then we need to store that file in an aws s3 bucket using the boto3 function `upload_file`
# 2. Diagram

![](../images/ssm_backups.jpg)