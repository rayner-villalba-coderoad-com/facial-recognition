# boto3 is AWS SDK for Python (Boto3) to create, configure, and manage AWS services(S3, EC2, DynamoDb)
import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', 
                           region_name='us-east-1' # Make sure to use your AWS region
                          )
#Set you Dynamo DB table name 
dynamodbTableName = 'employee'

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

employeeTable = dynamodb.Table(dynamodbTableName)

def lambda_handler(event, context):
  print(event)
  # Remember based on our configuration s3 triggers our lambda function so we should get the name of the bucket 
  bucket = event['Records'][0]['s3']['bucket']['name']
  key = event['Records'][0]['s3']['object']['key']

  try:
    response = index_employee_image(bucket, key)
    print(response)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
      faceId = response['FaceRecords'][0]['Face']['FaceId']

      #make sure to save your image in the following format firstName_lastName.jpg for example rayner_villalba.jpeg
      name = key.split('.')[0].split('_')
      firstName = name[0]
      lastName = name[1]
      register_employee(faceId, firstName, lastName)
    
    return response

  except Exception as e:
    print(e)
    print('Error processing employee image {} from bucket {}.'.format(key, bucket))
    raise e

def index_employee_image(bucket, key):
  response = rekognition.index_faces(
    Image={
      'S3Object': 
      {
        'Bucket': bucket,
        'Name': key
      }
    },
    CollectionId='employees'
  )

  return response

def register_employee(faceId, firstName, lastName):
  employeeTable.put_item(
    Item={
      'rekognitionId': faceId,
      'firstName': firstName,
      'lastName': lastName
    }
  )