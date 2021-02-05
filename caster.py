#!/usr/bin/env python3

import boto3, json, argparse, os, logging, sys, time
#from datetime import datetime, timedelta - for access log parsing

#TODO lots of refactoring, seperate functions and main script, access log parsing options

parser = argparse.ArgumentParser(description='Bucket Inspection Protection:\nModify or create an S3 bucket and add explicit whitelisting in order to evade sandboxing')
SD = parser.add_mutually_exclusive_group()
SD.add_argument("-s", "--show_existing",help='show all existing bucket names and exit.\n', action='store_true') #TODO choose bucket from list
SD.add_argument("-b", "--bucket_name", help='name of bucket you want to create and/or add an ACL policy for.\n', default='test-bip') #TODO: logic if bucket not exist to ask if create one or exit, will need to read error from aws-cli output
FL = parser.add_mutually_exclusive_group()
FL.add_argument("-i", "--ip_list", nargs='*', help='IPs to whitelist OR blacklist', default=[])
FL.add_argument("-f", "--ip_file", help='file of IPs to whitelist OR blacklist\n')
parser.add_argument("-n", "--new_bucket", help='create a new bucket\n', action='store_true')
parser.add_argument("-u", "--uploads", nargs='+', type=os.path.abspath, help='file(s) to upload to the s3 bucket\n')
parser.add_argument("-r", "--region", nargs='?', help='set the region of the client session, new buckets will be created in the region of the session\n', default='us-east-2')
parser.add_argument("-v", "--version", help='bucket policy version to use\n', default='2012-10-17')
parser.add_argument("-e", "--explicit_blacklist", help='whitelist ALL or explicitly block IPs - using this switch with no IP arguments will allow all IPs\n', action='store_true')
args = parser.parse_args() 

with open('OPs_IPs.json') as f:
	OPs_IPs = json.load(f)
	print(f'Your IPs are: {OPs_IPs}')

#start s3 client sesh
region = args.region
s3 = boto3.client('s3', region_name=region)

#List exisiting buckets
if args.show_existing:
	response = s3.list_buckets()
	buckets = [bucket['Name'] for bucket in response['Buckets']]
	print("Bucket List: %s" % buckets) #TODO output needs better formatting and possibly indexing
	exit()

#Variables
bucket = args.bucket_name
version = json.dumps(args.version)

#Create new bucket
if args.new_bucket:
	print(f'Name for bucket will be: {bucket}')
	print(f'Region for new bucket will be: {region}')
	s3.create_bucket(Bucket=bucket)

#Toggle Allow/Deny && Parse IP inputs into json
if args.ip_file:
	with open(args.ip_file) as f:
		IPs = f.read().splitlines()
else:
	IPs = args.ip_list
if not args.explicit_blacklist:
	IPs.extend(OPs_IPs) #TODO read from config file
	print('Allowed IPs will be: ')
	toggle = 'Deny'
else:
	print('Denied IPs will be: ')
	toggle = 'Allow'
IPs = json.dumps(IPs)
print(f'\n{IPs}')

#create policy string
bucket_policy = '{"Version":'+version+',"Id":"S3PolicyID1","Statement":[{"Sid":"1","Effect":"'+toggle+'","Principal":"*","Action":"s3:*","Resource":"arn:aws:s3:::'+bucket+'/*","Condition":{"NotIpAddress":{"aws:SourceIp":'+IPs+'}}}]}' #bc nested string interpolation is hard

#Get the policy of a current bucket
if not args.new_bucket:
	try:
		json_policy = s3.get_bucket_policy(Bucket=bucket)['Policy']
		print('\nOld Policy: ')
		print(json_policy)
	except:
		print('\nCould not retrieve currrent policy or no policy exists yet')

#Set the bucket policy
s3.put_bucket_policy(Bucket=f"{bucket}", Policy=bucket_policy)
print('\nPolicy has been set to: ') 
print(s3.get_bucket_policy(Bucket=f"{bucket}")['Policy'])

#Upload files
if args.uploads:
	file_list = args.uploads
	for item in file_list:
		name = os.path.basename(item)
		s3.upload_file(item, bucket, name, ExtraArgs={'ACL':'public-read'})
		print(f'"{name}" was uploaded to bucket with URL: https://{bucket}.s3.{region}.amazonaws.com/{name}')

