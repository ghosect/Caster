# Caster
Tool to list your S3 buckets, create a new S3 bucket, upload files to a bucket, use policy based IP whitelisting and blacklisting. Supports regioning and allows for IP lists or specifying IPs in the command line. Originially created as a tool to quickly host files meant for Phishing engagements and help protect those files from sandbox inspection, thereby raising success rates and reducing false positives.

Requirements:
AWS CLI - install AWS CLI, then run 'aws configure' - https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html#cliv2-linux-prereq 
	See quickstart -> configuration https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
	Your keys can be found in your S3 client under Account -> Manage Account -> (with your account selected) Edit. | Just click on your secret access key to view it. 
BOTO 3 - https://github.com/boto/boto3

OPs_IPs.json:
The script will use OPs_IPs.json to hold your IP addresses so that you do not lock yourself out of your own bucket! You must keep the format correct in order for the script to work. Add or remove as many IPs or CIDR ranges as needed. 
Format: [ "x.x.x.x", "x.x.x.x/24" ] 
